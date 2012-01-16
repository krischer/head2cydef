from clang.cindex import Index, TypeKind, CursorKind
import os 
from header import TYPE_KIND_MAP, TAB

class clangParserGenericError(Exception):
    pass


def get_pretty_typekind_string(type_node, return_string=''):
    """
    Takes a clang.cindex.Type node and recursivly traverses it to the end and
    will return a string as it would be written in the code.

    e.g. it takes a Type that points to a pointer of an integer and returns
        int**
    """
    # A native type is mapped via a dictionary lookup.
    if  type_node.kind in TYPE_KIND_MAP:
        return_string = TYPE_KIND_MAP[type_node.kind] + return_string

    # If it is a pointer, recursively call the function again and append an
    # asterix.
    elif type_node.kind is TypeKind.POINTER:
        return_string = get_pretty_typekind_string(
            type_node.get_pointee(), return_string) + '*' + return_string

    # If it is a typedef lookup, get the original type and return.
    elif type_node.kind is TypeKind.TYPEDEF:
        return_string = type_node.get_declaration().displayname + return_string

    # An array is another possibility.
    elif type_node.kind is TypeKind.CONSTANTARRAY:
        array_type = get_pretty_typekind_string(
                            type_node.get_array_element_type())
        array_size = type_node.get_array_size()
        return_string = array_type + ' ' + return_string + '[%i]' % array_size

    else:
        msg = ('Error while traversing the TypeKind nodes. Node of type %s ' %\
               str(type_node.kind) ) + \
              'is not handled in the current implementation.'
        raise clangParserGenericError(msg)

    return return_string


class Node(object):
    """
    Base class for all Node parsers.
    """
    def __init__(self, node, parser=None):
        self.node = node
        self.node_name = self.node.spelling
        self.file_parser = parser
        self.files_to_parse = parser.files_to_parse
        self.external_types = parser.external_types
        self._parse_node()
    def _parse_node(self):
        raise NotImplementedError
    def _store_C_string(self):
        raise NotImplementedError
    def _store_cython_string(self):
        raise NotImplementedError
    def get_cython_string(self):
        self._store_cython_string()
        return self.cython_string
    def get_C_string(self):
        self._store_C_string()
        return self.C_string
    def __str__(self):
        return self.get_cython_string()


class MacroDefinitionNode(Node):
    """
    Handles macro definition node.

    Will parse all macros. Simple define constants aka
        #define PI 3.14
    will have self.is_define_constant set to True. More complicated macros will
    have it set to False.
    """
    def __init__(self, node, *args, **kwargs):
        Node.__init__(self, node, *args, **kwargs)

    def _parse_node(self):
        # A macro is special and the spelling is just None.
        self.node_name = self.node.displayname
        # Figure out if it is a simple macro definition or not.
        # XXX: Is there a way to do this within clang?
        with open(self.node.location.file.name, 'r') as file_object:
            start = self.node.extent.begin_int_data
            end = self.node.extent.end_int_data
            # Minus 2 because
            # a) Column starts counting at 1, e.g. to read the first column you
            # would have to seek(0).
            # b) ???? XXX: I have no idea but it seems to work in all tested
            #    cases.
            file_object.seek(start - 2, 0)
            self.defintion_code = file_object.read(end - start)
        # XXX: Whacky.
        # As only simple macro definitions are supported and of interest for
        # Cython (there might be rare use for full macros in Cython but the
        # user would also need to specify the types and therefore would need to
        # add the definition by hand anyway) full macros are not supported. As
        # soon as a macro definition contains brackets it will be considered to
        # not be a simple macro definition.
        if '(' in self.defintion_code or ')' in self.defintion_code:
            self.is_define_constant = False
        else:
            self.is_define_constant = True

    def _store_cython_string(self):
        """
        Define macros are defines as dummy enums.
        """
        self.cython_string = "cdef enum %s:\n%spass" % (self.node_name, TAB)

    def _store_C_string(self):
        self.C_string = 'Not implemented'


class TypedefNode(Node):
    """
    Parses a typedef node.

    XXX: The parsing feels kind of messy and might not be fully correct.
    """
    def __init__(self, node, *args, **kwargs):
        """
        """
        Node.__init__(self, node, *args, **kwargs)

    def _parse_node(self):
        self.original_type = self.node.type.get_canonical()
        # If its a pointer that points to function prototype than it is a
        # typedef typecast, e.g. like
        #     typdef int (*funcptr)(float param1);
        self.is_typecast = False
        self.array_size = None
        self.pretty_original_type = None

        if self.original_type.get_pointee().kind == TypeKind.FUNCTIONPROTO:
            # self.node_name would be funcptr in the above example.
            self.is_typecast = True
            # self.func_params would be param1 in the above example.
            self.func_params = []
            exist_after_loop = False
            for child in self.node.get_children():
                if child.kind == CursorKind.PARM_DECL:
                    self.func_params.append(child)
                elif child.kind ==  CursorKind.TYPE_REF:
                    self.original_type = child.displayname
                    exist_after_loop = True
            if exist_after_loop:
                return
            # The true original type, e.g. int in the above example.
            self.original_type = get_pretty_typekind_string(
                self.original_type.get_pointee().get_result())
            return

        # Array typedefs.
        elif self.original_type.kind == TypeKind.CONSTANTARRAY:
            self.array_size = self.original_type.get_array_size()
            self.original_type = self.original_type.get_array_element_type()
            self.pretty_original_type = get_pretty_typekind_string(
                                                            self.original_type)
            return

        # Handle simple typedefs.
        try:
            self.pretty_original_type = \
                get_pretty_typekind_string(self.original_type)
            children = []
            # Special case if one create a typdef from a typedef that has
            # native type. e.g.
            #   typedef int newInt;
            #   typedef newInt newerInt;
            # The canonical type for both would be int, but the later one also
            # has a child whose displayname is newInt which is a better choice
            # for the original type. This can play a role if for example the C
            # library uses stdint.h and creates typedefs of the integer types
            # defines therein.
            for _i in self.node.get_children():
                children.append(_i)
            if len(children):
                self.pretty_original_type = children[0].displayname

        # Otherwise parse the children to get the structure the typedef points
        # to.
        except clangParserGenericError:
            children = []
            for _i in self.node.get_children():
                children.append(_i)
            if len(children) != 1:
                raise NotImplementedError
            self.original_type = children[0]
            self.pretty_original_type = None

    def _store_C_string(self):
        if self.is_typecast is True:
            self.C_string = 'typedef %s (*%s)(%s);' % (self.original_type,
                self.node_name,
                ', '.join(['%s %s' % \
                (get_pretty_typekind_string(_i.type), _i.displayname) \
                for _i in self.func_params]))
            return
        if self.pretty_original_type:
            ret_str = 'typedef %s %s' % (self.pretty_original_type,
                                      self.node_name)
            if self.array_size:
                ret_str += '[%i]' % self.array_size
            ret_str += ';'
            self.C_string = ret_str
            return
        else:
            # Otherwise its a typedef on a non-simple type.
            # Differentiate between struct, ...
            if self.original_type.kind == CursorKind.STRUCT_DECL:
                struct = StructNode(self.original_type, self.file_parser)
                struct_string = struct.get_C_string()
                if struct.node_name:
                    struct_string = struct_string[:-1]
                self.C_string = 'typedef %s %s;' % (struct_string,
                                           self.node_name)
                return
            # ... union, ...
            elif self.original_type.kind == CursorKind.UNION_DECL:
                union = UnionNode(self.original_type, self.file_parser)
                union_string = union.get_C_string()
                if union.node_name:
                    union_string = union_string[:-1]
                self.C_string = 'typedef %s %s;' % (union_string,
                                           self.node_name)
                return
            # ... and enum.
            elif self.original_type.kind == CursorKind.ENUM_DECL:
                enum = EnumNode(self.original_type, self.file_parser)
                enum_string = enum.get_C_string()
                if enum.node_name:
                    enum_string = enum_string[:-1]
                self.C_string = 'typedef %s %s;' % (enum_string,
                                           self.node_name)
                return
            else:
                raise NotImplementedError


    def _store_cython_string(self):
        if self.is_typecast is True or self.pretty_original_type:
            self.cython_string = 'c%s' % self.get_C_string()[:-1]
            return
        else:
            if self.original_type.kind == CursorKind.STRUCT_DECL:
                struct = StructNode(self.original_type, self.file_parser)
                # Only print the typedef if its not a straight struct typedef,
                # e.g. no name is actually given to the struct.
                if struct.node_name:
                    ret_string = '%s' % struct.get_cython_string()
                    # Special case handling if the tag for struct and the name
                    # of the typedef are identical.
                    if struct.node_name != self.node_name:
                        ret_string += '\nctypedef %s %s' % (struct.node_name,
                                                            self.node_name)
                else:
                    struct._store_cython_string(name_from_typedef=self.node_name)
                    ret_string = '%s' % struct.get_cython_string()
                self.cython_string = ret_string
                return
            elif self.original_type.kind == CursorKind.UNION_DECL:
                union = UnionNode(self.original_type, self.file_parser)
                # Only print the typedef if its not a straight union typedef,
                # e.g. no name is actually given to the union.
                if union.node_name:
                    ret_string = '%s' % union.get_cython_string()
                    # Special case handling if the tag for struct and the name
                    # of the typedef are identical.
                    if union.node_name != self.node_name:
                        ret_string += '\nctypedef %s %s' % (union.node_name,
                                                            self.node_name)
                else:
                    union._store_cython_string(name_from_typedef=self.node_name)
                    ret_string = '%s' % union.get_cython_string()
                self.cython_string = ret_string
                return
            elif self.original_type.kind == CursorKind.ENUM_DECL:
                enum = EnumNode(self.original_type, self.file_parser)
                # Only print the typedef if its not a straight enum typedef,
                # e.g. no name is actually given to the enum.
                if enum.node_name:
                    ret_string = '%s' % enum.get_cython_string()
                    # Special case handling if the tag for struct and the name
                    # of the typedef are identical.
                    if enum.node_name != self.node_name:
                        ret_string += '\nctypedef %s %s' % (enum.node_name,
                                                            self.node_name)
                else:
                    enum._store_cython_string(name_from_typedef=self.node_name)
                    ret_string = '%s' % enum.get_cython_string()
                self.cython_string = ret_string
                return
            else:
                if self.original_type.kind == CursorKind.TYPE_REF:
                    self.original_type = \
                    self.original_type.type.get_canonical().get_declaration()
                    self.cython_string = self.get_cython_string()
                    return
                raise NotImplementedError


class StructNode(Node):
    """
    Parses a struct node.
    """
    def __init__(self, node, *args, **kwargs):
        """
        """
        Node.__init__(self, node, *args, **kwargs)

    def _parse_node(self):
        self.fields = []
        for child in self.node.get_children():
            # Only get field declarations.
            if child.kind == CursorKind.FIELD_DECL:
                # try:
                #     if get_pretty_typekind_string(child.type) == 'off_t':
                #         from IPython.core.debugger import Tracer; Tracer()()
                # except:
                #     pass
                type_decl = child.type.get_declaration()
                if hasattr(type_decl, 'location') and \
                   hasattr(type_decl.location, 'file') and \
                   type_decl.location.file and \
                   type_decl.location.file.name and \
                   os.path.abspath(type_decl.location.file.name) not in \
                   self.files_to_parse:
                    if get_pretty_typekind_string(child.type) == 'off_t':
                        print 'appending off_t'

                    self.external_types.append(
                        (os.path.abspath(type_decl.location.file.name),
                         get_pretty_typekind_string(child.type),
                         get_pretty_typekind_string(type_decl.type.get_canonical())))

                self.fields.append(child)

    def _store_C_string(self):
        if self.node_name:
            return_str = 'struct %s {\n' % self.node_name
        # Used for a straight typedefed struct which will have no name.
        else:
            return_str = 'struct {\n'
        pretty_fields = []
        for field in self.fields:
            try:
                pretty_type = get_pretty_typekind_string(field.type)

                pretty_fields.append('%s%s %s;' % (TAB, pretty_type,
                                                   field.displayname))
            except clangParserGenericError:
                if field.type.kind == TypeKind.POINTER:
                    canonical = field.type.get_pointee().get_canonical()
                    if canonical.kind != TypeKind.FUNCTIONPROTO:
                        raise NotImplementedError
                    return_type = get_pretty_typekind_string(
                        canonical.get_result())
                    function_name = field.displayname
                    params = []
                    for child in field.get_children():
                        if child.kind == CursorKind.PARM_DECL:
                            params.append(child)
                    param_string = ['%s %s' % \
                                    (get_pretty_typekind_string(_i.type),
                                     _i.displayname) for _i in params]
                    pretty_fields.append('%s%s (*%s) (%s);' % (TAB,
                        return_type, function_name, ', '.join(param_string)))
                else:
                    raise NotImplementedError
        if len(pretty_fields) == 0:
            pretty_fields.append('%spass' % TAB)
        return_str += '\n'.join(pretty_fields)
        return_str += '\n}'
        # Again for the straight typedefs.
        if self.node_name:
            return_str += ';'
        self.C_string = return_str
        return

    def _store_cython_string(self, name_from_typedef=None):
        """
        If the struct itself has no name, e.g. its a straight typedef without
        actually assigning a name to the struct, the name needs to be given to
        this function.
        """
        if name_from_typedef is None:
            return_str = 'cdef struct %s:\n' % self.node_name
        else:
            return_str = 'ctypedef struct %s:\n' % name_from_typedef
        pretty_fields = []
        for field in self.fields:
            try:
                pretty_type = get_pretty_typekind_string(field.type)
                pretty_fields.append('%s%s %s' % (TAB, pretty_type,
                                                   field.displayname))
            except clangParserGenericError:
                if field.type.kind == TypeKind.POINTER:
                    canonical = field.type.get_pointee().get_canonical()
                    if canonical.kind == TypeKind.RECORD:
                        if canonical.get_declaration().kind == \
                            CursorKind.STRUCT_DECL:
                            struct_name = \
                                    canonical.get_declaration().displayname
                            pretty_fields.append('%s%s* %s' % (TAB,
                                struct_name, field.displayname))
                            continue
                        else:
                            raise NotImplementedError
                    elif canonical.kind != TypeKind.FUNCTIONPROTO and \
                         canonical.kind != TypeKind.FUNCTIONNOPROTO:
                        raise NotImplementedError
                    return_type = get_pretty_typekind_string(
                        canonical.get_result())
                    function_name = field.displayname
                    params = []
                    for child in field.get_children():
                        if child.kind == CursorKind.PARM_DECL:
                            params.append(child)
                    # Verbose loop instead of list comprehension for easier
                    # debugging.
                    param_string = []

                    for param in params:
                        pointee = param.type.get_pointee()
                        if pointee.kind == TypeKind.UNEXPOSED:
                            if pointee.get_declaration().kind == \
                               CursorKind.STRUCT_DECL:
                                param_string.append('%s* %s' % \
                                    (pointee.get_declaration().displayname,
                                    param.displayname))
                                continue
                            else:
                                raise NotImplementedError
                        param_string.append('%s %s' % \
                            (get_pretty_typekind_string(param.type),
                             param.displayname))

                    pretty_fields.append('%s%s (*%s) (%s)' % (TAB,
                        return_type, function_name, ', '.join(param_string)))
                else:
                    from IPython.core.debugger import Tracer; Tracer()()
                    raise NotImplementedError
        if len(pretty_fields) == 0:
            pretty_fields.append('%spass' % TAB)
        return_str += '\n'.join(pretty_fields)
        self.cython_string = return_str
        return


class UnionNode(Node):
    """
    Parses a union node.
    """
    def __init__(self, node, *args, **kwargs):
        """
        """
        Node.__init__(self, node, *args, **kwargs)

    def _parse_node(self):
        self.fields = []
        for child in self.node.get_children():
            # Only get field declarations.
            if child.kind == CursorKind.FIELD_DECL:
                self.fields.append(child)
                type_decl = child.type.get_declaration()
                if hasattr(type_decl, 'location') and \
                   hasattr(type_decl.location, 'file') and \
                   type_decl.location.file and \
                   type_decl.location.file.name and \
                   os.path.abspath(type_decl.location.file.name) not in \
                   self.files_to_parse:
                    self.external_types.append(
                        (os.path.abspath(type_decl.location.file.name),
                         get_pretty_typekind_string(child.type),
                         get_pretty_typekind_string(type_decl.type.get_canonical())))

    def _store_C_string(self):
        if self.node_name:
            return_str = 'union %s {\n' % self.node_name
        # Used for a straight typedefed struct which will have no name.
        else:
            return_str = 'union {\n'
        return_str += '\n'.join(['%s%s %s;' % \
            (TAB, get_pretty_typekind_string(_i.type), _i.displayname) \
            for _i in self.fields])
        return_str += '\n}'
        # Again for the straight typedefs.
        if self.node_name:
            return_str += ';'
        self.C_string = return_str

    def _store_cython_string(self, name_from_typedef=None):
        """
        If the union itself has no name, e.g. its a straight typedef without
        actually assigning a name to the union, the name needs to be given to
        this function.
        """
        if name_from_typedef is None:
            return_str = 'cdef union %s:\n' % self.node_name
        else:
            return_str = 'ctypedef union %s:\n' % name_from_typedef
        return_str += '\n'.join(['%s%s %s' % \
            (TAB, get_pretty_typekind_string(_i.type), _i.displayname) \
            for _i in self.fields])
        self.cython_string = return_str


class EnumNode(Node):
    """
    Parses an enum node.
    """
    def __init__(self, node, *args, **kwargs):
        """
        """
        Node.__init__(self, node, *args, **kwargs)

    def _parse_node(self):
        self.fields = []
        for child in self.node.get_children():
            # Only get enum declarations. This is just a safety measure. There
            # never should be anything else in here.
            if child.kind == CursorKind.ENUM_CONSTANT_DECL:
                self.fields.append(child)

    def _store_C_string(self):
        if self.node_name:
            return_str = 'enum %s {\n' % self.node_name
        # Used for a straight typedefed enum which will have no name.
        else:
            return_str = 'enum {\n'
        return_str += '\n'.join(['%s%s,' % \
            (TAB, _i.displayname) for _i in self.fields])
        # Remove the last comma.
        if return_str[-1] == ',':
            return_str = return_str[:-1]
        return_str += '\n}'
        # Again for the straight typedefs.
        if self.node_name:
            return_str += ';'
        self.C_string = return_str

    def _store_cython_string(self, name_from_typedef=None):
        """
        If the enum itself has no name, e.g. its a straight typedef without
        actually assigning a name to the enum, the name needs to be given to
        this function.
        """
        if name_from_typedef is None:
            return_str = 'cdef enum %s:\n' % self.node_name
        else:
            return_str = 'ctypedef enum %s:\n' % name_from_typedef
        return_str += '\n'.join(['%s%s' % \
            (TAB, _i.displayname) for _i in self.fields])
        self.cython_string =  return_str


class FunctionProtoNode(Node):
    """
    Parses a function prototype node.
    """
    def __init__(self, node, *args, **kwargs):
        """
        Parses a node whose type.kind is TypeKind.FUNCTIONPROTO.
        """
        Node.__init__(self, node, *args, **kwargs)

    def _parse_node(self):
        # Get the return type and its pretty representation.
        self.return_type = self.node.type.get_result()
        self.pretty_return_string = \
            get_pretty_typekind_string(self.return_type)

        # Loop through the node's children to get all function parameters.
        self.function_parameters = []
        for child in self.node.get_children():
            # Filter to only get the parameters.
            if child.kind == CursorKind.PARM_DECL:
                self.function_parameters.append(child)

        self.pretty_parameter_names = []
        for param in self.function_parameters:
            if param.kind == CursorKind.STRUCT_DECL:
                p_type = 'struct'
            elif param.kind == CursorKind.UNION_DECL:
                p_type = 'union'
            elif param.type.kind == TypeKind.ENUM:
                p_type = 'enum'
            elif param.type.kind == TypeKind.POINTER:
                # from IPython.core.debugger import Tracer; Tracer()()
                start = param.extent.begin_int_data
                end = param.extent.end_int_data
                with open(os.path.abspath(param.location.file.name),
                          'r') as file_object:
                    file_object.seek(start - 2, 0)
                    self.pretty_parameter_names.append(\
                                    file_object.read(end - start))
                continue
                # if pointee.get_canonical().get_declaration().kind == \
                #    CursorKind.STRUCT_DECL:
                #     org_type = 'struct'
                # else:
                #     raise NotImplementedError
                # p_type = org_type
            else:
                p_type = get_pretty_typekind_string(param.type)
            self.pretty_parameter_names.append('%s %s' % (p_type,
                                                          param.displayname))

    def _store_cython_string(self):
        """
        The same as the pretty function string minus the semicolon.
        """
        self.cython_string = self.C_string[:-1]

    def _store_C_string(self):
        """
        Returns the function declaration as it would be written in code.
        """
        self.C_string = '%s %s(%s);' % (self.pretty_return_string, self.node_name,
            ', '.join(self.pretty_parameter_names))

