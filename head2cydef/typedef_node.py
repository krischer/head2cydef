from head2cydef import Node


class TypedefNode(Node):
    """
    Parses a typedef node.
    """
    def __init__(self, node):
        """
        """
        Node.__init__(self, node)

    def _parse_node(self):
        self.typedef_name = self.node.displayname
        self.original_type = self.node.type.get_canonical()
        # If its a pointer that points to function prototype than it is a
        # typedef typecast, e.g. like
        #     typdef int (*funcptr)(float param1);
        self.is_typecast = False
        self.array_size = None
        self.pretty_original_type = None
        if self.original_type.get_pointee().kind == TypeKind.FUNCTIONPROTO:
            # self.typedef_name would be funcptr in the above example.
            self.is_typecast = True
            # self.func_params would be param1 in the above example.
            self.func_params = []
            exist_after_loop = False
            for child in self.node.get_children():
                if child.kind == CursorKind.PARM_DECL:
                    self.func_params.append(child)
                elif child.kind == CursorKind.TYPE_REF:
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

    def get_C_string(self):
        if self.is_typecast is True:
            return 'typedef %s (*%s)(%s);' % (self.original_type,
                self.typedef_name,
                ', '.join(['%s %s' % \
                (get_pretty_typekind_string(_i.type), _i.displayname) \
                for _i in self.func_params]))
        if self.pretty_original_type:
            ret_str = 'typedef %s %s' % (self.pretty_original_type,
                                      self.typedef_name)
            if self.array_size:
                ret_str += '[%i]' % self.array_size
            ret_str += ';'
            return ret_str
        else:
            # Otherwise its a typedef on a non-simple type.
            # Differentiate between struct, ...
            if self.original_type.kind == CursorKind.STRUCT_DECL:
                struct = StructNode(self.original_type)
                struct_string = struct.get_C_string()
                if struct.struct_name:
                    struct_string = struct_string[:-1]
                return 'typedef %s %s;' % (struct_string,
                                           self.typedef_name)
            # ... union, ...
            elif self.original_type.kind == CursorKind.UNION_DECL:
                union = UnionNode(self.original_type)
                union_string = union.get_C_string()
                if union.union_name:
                    union_string = union_string[:-1]
                return 'typedef %s %s;' % (union_string,
                                           self.typedef_name)
            # ... and enum.
            elif self.original_type.kind == CursorKind.ENUM_DECL:
                enum = EnumNode(self.original_type)
                enum_string = enum.get_C_string()
                if enum.enum_name:
                    enum_string = enum_string[:-1]
                return 'typedef %s %s;' % (enum_string,
                                           self.typedef_name)
            else:
                raise NotImplementedError

    def get_cython_string(self):
        if self.is_typecast is True or self.pretty_original_type:
            return 'c%s' % self.get_C_string()[:-1]
        else:
            if self.original_type.kind == CursorKind.STRUCT_DECL:
                struct = StructNode(self.original_type)
                # Only print the typedef if its not a straight struct typedef,
                # e.g. no name is actually given to the struct.
                if struct.struct_name:
                    ret_string = '%s' % struct.get_cython_string()
                    # Special case handling if the tag for struct and the name
                    # of the typedef are identical.
                    if struct.struct_name != self.typedef_name:
                        ret_string += '\nctypedef %s %s' % (struct.struct_name,
                                                            self.typedef_name)
                else:
                    ret_string = '%s' % struct.get_cython_string(\
                                        name_from_typedef=self.typedef_name)
                return ret_string
            elif self.original_type.kind == CursorKind.UNION_DECL:
                union = UnionNode(self.original_type)
                # Only print the typedef if its not a straight union typedef,
                # e.g. no name is actually given to the union.
                if union.union_name:
                    ret_string = '%s' % union.get_cython_string()
                    # Special case handling if the tag for struct and the name
                    # of the typedef are identical.
                    if union.union_name != self.typedef_name:
                        ret_string += '\nctypedef %s %s' % (union.union_name,
                                                            self.typedef_name)
                else:
                    ret_string = '%s' % union.get_cython_string(\
                                        name_from_typedef=self.typedef_name)
                return ret_string
            elif self.original_type.kind == CursorKind.ENUM_DECL:
                enum = EnumNode(self.original_type)
                # Only print the typedef if its not a straight enum typedef,
                # e.g. no name is actually given to the enum.
                if enum.enum_name:
                    ret_string = '%s' % enum.get_cython_string()
                    # Special case handling if the tag for struct and the name
                    # of the typedef are identical.
                    if enum.enum_name != self.typedef_name:
                        ret_string += '\nctypedef %s %s' % (enum.enum_name,
                                                            self.typedef_name)
                else:
                    ret_string = '%s' % enum.get_cython_string(\
                                        name_from_typedef=self.typedef_name)
                return ret_string
            else:
                if self.original_type.kind == CursorKind.TYPE_REF:
                    self.original_type = \
                    self.original_type.type.get_canonical().get_declaration()
                    return self.get_cython_string()
                raise NotImplementedError
