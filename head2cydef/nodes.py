from clang.cindex import Index, TypeKind, CursorKind, Type
import copy
import os
import random
import re

from header import TYPE_KIND_MAP, TAB


class clangParserGenericError(Exception):
    pass

class clangParserWrongNodeKindError(clangParserGenericError):
    pass


class Node(object):
    """
    Base class for all Node parsers.
    """
    def __init__(self, node, parser=None, *args, **kwargs):
        # Give easy access to the central parser class and some attributes of
        # it from within every class member.
        self.file_parser = parser
        self.files_to_parse = parser.files_to_parse
        self.used_names = parser.used_names

        self.node = node
        self.node_name = self.node.spelling
        # If the node has no name, e.g. in a nested struct, or a direct typedef
        # assign a random one to it, so it can be referenced to.
        if not self.node_name:
            self.set_random_node_name()
        # Append the name of the current node to it.
        self.used_names.append(self.node_name)

        # Always parse the node during initialization and assemble the Cython
        # string.
        self._parse_node()

    def _add_type_to_collection(self, type_kind):
        """
        Add a type to the global type collection.
        """
        if not isinstance(type_kind, Type):
            msg = "Not a clang.cindex.Type instance."
            raise TypeError(msg)
        # Store as (file_path
        self.file_parser.type_collection.append(type_kind)

    def _parse_node(self):
        raise NotImplementedError

    def get_cython_string(self, *args, **kwargs):
        return self.cython_string

    def __str__(self):
        return self.get_cython_string()

    def set_random_node_name(self):
        """
        Set a random node_name in one of the following forms:
            Struct_random_462343461
            Union_random_462343461
            Enum_random_462343461
        This will check with the file parser to avoid accidentically creating
        duplicate names.
        """
        # Loop until a previously untaken name is found.
        while True:
            # Assemble the new name based on the class name.
            class_name = self.__class__.__name__.lower()
            class_name = class_name.replace('node', '')
            class_name = class_name.capitalize()
            class_name += '_temp_random_%06i' % random.randint(0, 999999)
            if class_name not in self.used_names:
                break
        self.node_name = class_name
        self.used_names.append(self.node_name)

    def get_type_chain(self, type_node, type_chain):
        """
        GO RIGHT WHEN YOU CAN GO LEFT WHEN YOU MUST.

        Type chain will contain a list which specifies the "type chain", e.g. a
        pointer to an integer, int *:
            type_chain = ['__pointer__', 'int']
        An array of five integers, e.g. int[5]:
            type_chain = [('__array__', 5), 'int']
        An array of ten pointers to array of five integers,
        e.g. int (*[10])[5]:
            type_chain = [('__array__', 10), '__pointer__', ('__array__', 5), 'int']

        __pointer__ and __array__ strings denote pointers and arrays. The
        underscores are to avoid confusion in case some type is actually called
        "pointer" or "array" in the C source.

        Due to the recursive nature of the function and Python storing references
        of function parameters over calls, an initial type_chain has to be given to
        the method. This usually is just an empty list.
        """
        # Small sanity check.
        if not isinstance(type_node.kind, TypeKind):
            msg = 'type_node.kind is not of type TypeKind.'
            raise TypeError(msg)
        # A native type is mapped via a dictionary lookup.
        if type_node.kind in TYPE_KIND_MAP:
            type_chain.append(TYPE_KIND_MAP[type_node.kind])
        # Store an eventual pointer and recursivly call the function.
        elif type_node.kind is TypeKind.POINTER:
            type_chain.append('__pointer__')
            self.get_type_chain(type_node.get_pointee(), type_chain)
        # An array is another possibility.
        elif type_node.kind is TypeKind.CONSTANTARRAY:
            array_size = type_node.get_array_size()
            type_chain.append(('__array__', array_size))
            self.get_type_chain(type_node.get_array_element_type(), type_chain)
        # If it is a typedef lookup, get the original type and return. The chains
        # stops here and the type should be defined by another typedef somewhere.
        elif type_node.kind is TypeKind.TYPEDEF:
            self._add_type_to_collection(type_node)
            type_chain.append(type_node.get_declaration().displayname)
        else:
            self._add_type_to_collection(type_node)
            type_chain.append(type_node.get_declaration().displayname)
        return type_chain


    @staticmethod
    def assemble_type_string(type_chain, type_string=''):
        """
        Takes a type chain as returned by get_type_chain and assembles a string
        from it.

        >>> type_chain = ['__pointer__', 'int']
        >>> print Node.assemble_type_string(type_chain)
        int *

        If type_string is given it will be inserted as if it is the name given during
        a typedef, e.g.
        >>> type_chain = [('__array__', 10), '__pointer__', ('__array__', 5), 'int']
        >>> print Node.assemble_type_string(type_chain, type_string='cmplxIntType')
        int (*cmplxIntType[10])[5]

        Omitting it will just not insert anything.
        >>> print Node.assemble_type_string(type_chain)
        int (*[10])[5]

        Customs types are possible if. They have to be given in the type chain.
        >>> type_chain = [('__array__', 10), '__pointer__', ('__array__', 5), 'other_int']
        >>> print Node.assemble_type_string(type_chain, type_string='cmplxIntType')
        other_int (*cmplxIntType[10])[5]
        """
        # Create a copy because it will be altered.
        type_chain = type_chain[:]
        previous_type = None
        while type_chain:
            # Pop the first item.
            item = type_chain.pop(0)
            # Array.
            if isinstance(item, tuple) and item[0] == '__array__':
                # Set brackets if necessary.
                if previous_type == '__pointer__':
                    type_string = '(%s)' % type_string
                type_string += '[%i]' % item[1]
            # Pointer.
            elif item == '__pointer__':
                type_string = '*' + type_string
            elif isinstance(item, basestring):
                type_string = '%s %s' % (item, type_string)
            else:
                from IPython.core.debugger import Tracer; Tracer()()
            previous_type = item
        return type_string

    def get_pretty_typekind_string(self, type_node, type_string='',
                                   force_final_type_to=False):
        """
        If force_final_type_to is a string, the final type, e.g. the last item in
        the type chain will be replaced with it. This enables to pass typedef'ed
        types, e.g force_final_type_to='new_int' will transform
            int *newInts[8]
        to
            new_int *newInts[8]
        """
        chain = self.get_type_chain(type_node, type_chain=[])
        # Modify the type chain if necessary.
        if force_final_type_to is not False:
            if chain and isinstance(chain[-1], basestring) and \
               chain[-1] != '__pointer__':
                chain.pop(-1)
            chain.append(force_final_type_to)
        ret_str = self.assemble_type_string(chain, type_string)
        return ret_str.strip()


class MacroDefinitionNode(Node):
    """
    Handles macro definition node.

    Will parse all macros. Simple define constants aka
        #define PI 3.14
    will have self.is_define_constant set to True. More complicated macros will
    have it set to False.
    Only those who have it set to true will be included in the final Cython
    definition file.
    """
    def __init__(self, node, *args, **kwargs):
        # Sanity check.
        if node.kind != CursorKind.MACRO_DEFINITION:
            msg = 'Not a valid macro definition node.'
            raise clangParserWrongNodeKindError(msg)
        Node.__init__(self, node, *args, **kwargs)

    def _parse_node(self):
        # A macro is special and the spelling is just None, therefore use the
        # displayname as the node name.
        self.node_name = self.node.displayname
        # Of course also append to the list of already used names.
        self.used_names.append(self.node_name)
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
        self.cython_string = "enum: %s" % self.node_name


class TypedefNode(Node):
    """
    Parses a typedef node.
    """
    def __init__(self, node, *args, **kwargs):
        """
        Parses a CursurKind.TYPEDEF_DECL node.
        """
        self.use_canonical_type = kwargs.get('use_canonical_type', False)
        # Sanity check.
        if node.kind != CursorKind.TYPEDEF_DECL:
            msg = 'Not a valid type definition node.'
            raise clangParserWrongNodeKindError(msg)
        Node.__init__(self, node, *args, **kwargs)

    def _parse_node(self):
        # The name of the typedef, e.g. the name of the newly created type is
        # stored in self.node_name.
        # The original type is the type that actually gets a new name. This is
        # the only way I could figure out how to get to the originally defined
        # type. If a typedef is done upon a typedef this will return the
        # original type, e.g. all typedefs are stripped away.
        self.original_type = self.node.type.get_canonical()

        # Handle function pointer casts differently.
        if self.original_type.kind == TypeKind.POINTER and \
           self.original_type.get_pointee().kind == TypeKind.FUNCTIONPROTO:
            self._parse_function_pointer()
            return

        # Get all children.
        children = []
        for child in self.node.get_children():
            children.append(child)

        force_final_type = False
        # Check if the first child is a type reference, if so, the original
        # type is already a typdefed type. Pass the typedef name to the string
        # generator function.
        if self.use_canonical_type is False and children and \
           children[0].kind == CursorKind.TYPE_REF:
            # Append the type to the type collection to identify eventual
            # external types.
            self._add_type_to_collection(children[0].type.get_declaration().type)
            force_final_type = children[0].displayname
            # If the final type is more than one word, it is usually something
            # like 'struct x' or 'union x'. The specifiers are not needed for a
            # typedef in Cython.
            force_final_type = force_final_type.split()[-1]
        # It can also be a struct/union/enum. If it is, loop through the list of all
        # nodes, finds the correct one and get the name.
        elif children and (children[0].kind == CursorKind.STRUCT_DECL or \
                          children[0].kind == CursorKind.UNION_DECL or \
                          children[0].kind == CursorKind.ENUM_DECL):
            all_nodes = self.file_parser.all_parsed_nodes
            for node in all_nodes:
                if bool(node.node==children[0]):
                    force_final_type = node.node_name
                    break

        # Get a pretty string representation of the original type.
        self.pretty_original_type = \
            self.get_pretty_typekind_string(self.original_type, self.node_name,
                                       force_final_type)

        # Assemble the Cython string. The syntax is almost the same as in C.
        self.cython_string = 'ctypedef %s' % (self.pretty_original_type)

    def _parse_function_pointer(self):
        """
        Parse function pointers seperatly in an attempt to keep the code clean.
        """
        function_pointer_node = FunctionPointerNode(self.node, self.file_parser)
        self.cython_string = 'ctypedef %s' % \
            function_pointer_node.get_cython_string()
        return


class FunctionPointerNode(Node):
    """
    Function pointer nodes. They usually are not a top level construct but
    occur either within a typedef, e.g.
        typedef float (*func_point)(int param1, void* param2);
    or within a struct/union, e.g.
        struct FPStruct {
            typedef float (*func_point)(int param1, void* param2);
            int other_member;};
    The returned cython string in both cases would be
        float (*func_point)(int param1, void* param2);
    """
    def __init__(self, node, *args, **kwargs):
        self.canonical = node.type.get_canonical()
        # Sanity check.
        if self.canonical.kind != TypeKind.POINTER or \
           (self.canonical.get_pointee().kind != TypeKind.FUNCTIONPROTO and \
            self.canonical.get_pointee().kind != TypeKind.FUNCTIONNOPROTO):
            msg = 'Not a valid function pointer node.'
            raise clangParserWrongNodeKindError(msg)
        Node.__init__(self, node, *args, **kwargs)

    def _parse_node(self):
        # Get the return type and the function name.
        return_type = self.get_pretty_typekind_string(
            self.canonical.get_pointee().get_result())
        if return_type.strip() == '':
            # If the return type is none, it refers to a typedef of a
            # previously unnamed struct/union/enum. Find that typedef.
            declaration = self.node.type.get_declaration()
            for child in declaration.get_children():
                if child.kind == CursorKind.TYPE_REF:
                    return_type = child.displayname

        function_name = self.node_name
        # The children are the parameters.
        params = []
        for child in self.node.get_children():
            if child.kind != CursorKind.PARM_DECL:
                continue
            # Fix some pure formatting issues with spaces between pointer
            # declarations and some other minor issues.
            pretty_type_string = \
                self.get_pretty_typekind_string(child.type).replace(' *', '*')
            params.append('%s %s' % (pretty_type_string, child.spelling))
            # Fix some formatting issues with unnamed function parameters which
            # would result in a whitespace at the end.
            params[-1] = params[-1].strip()
        self.cython_string = '%s (*%s)(%s)' % (return_type, function_name,
                                               ', '.join(params))


class StructOrUnionNode(Node):
    """
    Structs and unions are very similiar so one class is used for both.
    """
    def __init__(self, node, *args, **kwargs):
        """
        """
        # Sanity check.
        if node.kind == CursorKind.STRUCT_DECL:
            self.node_specifier = 'struct'
        elif node.kind == CursorKind.UNION_DECL:
            self.node_specifier = 'union'
        else:
            msg = 'Not a valid struct or union node.'
            raise clangParserWrongNodeKindError(msg)
        Node.__init__(self, node, *args, **kwargs)

    def _parse_node(self):
        self.fields = []
        for child in self.node.get_children():
            # If it is a struct/union and as NO children, add the struct/node
            # to the file parser object. If has children, it will interestingly
            # already be contained in the root node's nodes. This seems rather
            # inconsistently handled by clang.
            if child.kind == CursorKind.UNION_DECL:
                grandchilds = []
                for _i in child.get_children():
                    grandchilds.append(_i)
                if not grandchilds:
                    node = UnionNode(child, self.file_parser)
                    self.file_parser.all_parsed_nodes.append(node)
                    continue
            if child.kind == CursorKind.STRUCT_DECL:
                grandchilds = []
                for _i in child.get_children():
                    grandchilds.append(_i)
                if not grandchilds:
                    node = StructNode(child, self.file_parser)
                    self.file_parser.all_parsed_nodes.append(node)
                    continue
            # Only get field declarations.
            if child.kind != CursorKind.FIELD_DECL:
                continue
            self.fields.append(child)

        # Loop over all fields and get a pretty string representation.
        pretty_fields = []
        for field in self.fields:
            if field.kind != CursorKind.FIELD_DECL:
                continue
            if field.type.get_declaration().kind == CursorKind.UNION_DECL:
                node = UnionNode(field.type.get_declaration(), self.file_parser)
                self.file_parser.all_parsed_nodes.append(node)
                pretty_fields.append('%s%s %s' % (TAB, node.node_name,
                                                  field.displayname))
                continue
            if field.type.get_declaration().kind == CursorKind.STRUCT_DECL:
                node = StructNode(field.type.get_declaration(), self.file_parser)
                self.file_parser.all_parsed_nodes.append(node)
                pretty_fields.append('%s%s %s' % (TAB, node.node_name,
                                                  field.displayname))
                continue
            # Check if its a function pointer.
            canonical = field.type.get_canonical()
            if canonical.kind == TypeKind.POINTER and \
               (canonical.get_pointee().kind == TypeKind.FUNCTIONPROTO or \
                canonical.get_pointee().kind == TypeKind.FUNCTIONNOPROTO):
                function_pointer_node = FunctionPointerNode(field, self.file_parser)
                pretty_type = function_pointer_node.get_cython_string()
            else:
                pretty_type = self.get_pretty_typekind_string(field.type,
                                                         field.displayname)
            pretty_fields.append('%s%s' % (TAB, pretty_type))
        if len(pretty_fields) == 0:
            pretty_fields.append('%spass' % TAB)
        self.cython_string = 'cdef %s %s:\n' % (self.node_specifier, self.node_name)
        self.cython_string += '\n'.join(pretty_fields)


class StructNode(StructOrUnionNode):
    def __init__(self, node, *args, **kwargs):
        StructOrUnionNode.__init__(self, node, *args, **kwargs)


class UnionNode(StructOrUnionNode):
    def __init__(self, node, *args, **kwargs):
        StructOrUnionNode.__init__(self, node, *args, **kwargs)


class EnumNode(Node):
    """
    Parses an enum node.
    """
    def __init__(self, node, *args, **kwargs):
        # Sanity check.
        if node.kind != CursorKind.ENUM_DECL:
            msg = 'Not a valid enum node.'
            raise clangParserWrongNodeKindError(msg)
        Node.__init__(self, node, *args, **kwargs)

    def _parse_node(self):
        # Get all fields of the enum.
        self.fields = []
        for child in self.node.get_children():
            # Only get enum declarations. This is just a safety measure. There
            # never should be anything else in here if the C code is valid.
            if child.kind == CursorKind.ENUM_CONSTANT_DECL:
                self.fields.append(child)
        self.cython_string = 'cdef enum %s:\n' % self.node_name
        # Append all members, if no members exist, append pass.
        self.cython_string += '\n'.join(['%s%s' % \
            (TAB, _i.displayname) for _i in self.fields])


class FunctionProtoNode(Node):
    """
    Parses a function prototype node.
    """
    def __init__(self, node, *args, **kwargs):
        """
        Parses a node whose type.kind is TypeKind.FUNCTIONPROTO.
        """
        # Sanity check.
        if node.kind != CursorKind.FUNCTION_DECL:
            msg = 'Not a valid function declaration node.'
            raise clangParserWrongNodeKindError(msg)
        Node.__init__(self, node, *args, **kwargs)

    def _parse_node(self):
        # Get the return type and its pretty representation.
        self.return_type = self.node.type.get_result()
        self._add_type_to_collection(self.return_type)

        # XXX: What happens if a struct/union/enum is returned?
        self.pretty_return_string = \
            self.get_pretty_typekind_string(self.return_type)
        # XXX: Hacky
        self.pretty_return_string = self.pretty_return_string.replace(' ', '')

        # Loop through the node's children to get all function parameters.
        self.pretty_parameter_names = []
        self.function_parameters = []
        for param in self.node.get_children():
            # Filter to only get the parameters.
            if param.kind != CursorKind.PARM_DECL:
                continue
            self._add_type_to_collection(param.type)
            # Struct, union, enum specifiers do not appear in the cython
            # function definition.
            if param.kind == CursorKind.STRUCT_DECL or \
               param.kind == CursorKind.UNION_DECL or \
               param.kind == CursorKind.ENUM_DECL:
                continue
            else:
                p_type = self.get_pretty_typekind_string(param.type)
            # Check if its a function pointer.
            canonical = param.type.get_canonical()
            if canonical.kind == TypeKind.POINTER and \
               (canonical.get_pointee().kind == TypeKind.FUNCTIONPROTO or \
                canonical.get_pointee().kind == TypeKind.FUNCTIONNOPROTO):
                function_pointer_node = FunctionPointerNode(param, self.file_parser)
                self.pretty_parameter_names.append(function_pointer_node.get_cython_string())
                continue

            # Handle compiler specific datatype va_list.
            # XXX: Only tested with gcc and it will likely not correctly work
            # with other compilers.
            if p_type == '__va_list_tag *':
                p_type = 'va_list'
                self.file_parser.is_va_list_used = True

            self.pretty_parameter_names.append('%s %s' % (p_type,
                                               param.displayname))
            # Some formatting issues. Does not really change anything else.
            # Maybe find a more concise way of doing this.
            self.pretty_parameter_names[-1] = \
                self.pretty_parameter_names[-1].replace(' * ', ' *')
        # Assemble the cython string.
        self.cython_string = '%s %s(%s)' % (self.pretty_return_string, self.node_name,
            ', '.join(self.pretty_parameter_names))


if __name__ == "__main__":
    import doctest
    doctest.testmod()
