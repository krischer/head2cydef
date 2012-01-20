#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Convert C header files to Cython definition files using libclang's Python
bindings.

:copyright:
    Lion Krischer (krischer@geophysik.uni-muenchen.de), 2012
:license:
    GNU Lesser General Public License, Version 3
    (http://www.gnu.org/copyleft/lesser.html)
"""

from clang.cindex import Index, TypeKind, CursorKind
from glob import glob
import os

from nodes import *


class CFileParser(object):
    """
    """
    def __init__(self, filename):
        """
        """
        self.filename = filename
        self.file_directory = os.path.dirname(os.path.abspath(self.filename))
        # Only parse files in the directory of the initial header file.
        self.files_to_parse = glob(os.path.join(self.file_directory, '*'))

        self.index = Index.create()
        # options set the CXTranslationUnit_Flags enum to 1 so it also parses
        # everything related to the preprocessor.
        # See:
        #   http://clang.llvm.org/doxygen/group__CINDEX__TRANSLATION__UNIT.html
        self.translation_unit = self.index.parse(self.filename, options=1)
        self.cursor = self.translation_unit.cursor

        self._setup_data_structure()
        self._sort_toplevel_nodes()
        self.parse_all_nodes()
        # Parse the external types 10 times. This is an arbitrary level but
        # external types might refer to types that are defined elsewhere.
        # Running this 10 times will allow the parser to go 10 levels deep
        # which should be enough in most cases.
        # for _ in xrange(10):
        #     self.parse_external_types()
        self.parse_external_types()


    def _setup_data_structure(self):
        """
        Create some dictionaries for internal data handling.
        """
        # While traversing through the ast, collect all occuring types and
        # store them in one central location to later process them.
        self.type_collection = []

        # Collect all used names, like struct names, union names, enum names,
        # function names, typedefs and so on to avoid creating duplicate names.
        self.used_names = []

        # Sort all top level cursors in one dictionary which will always
        # contain the cursor object.
        self.unparsed_nodes = {
            'typedefs': [],
            'functionprotos': [],
            'structs': [],
            'unions': [],
            'enums': [],
            'macro_definitions': [],
            'unsorted': []
        }

        # After they are parsed, store them in another dictionary.
        self.parsed_nodes = {
            'typedefs': [],
            'functionprotos': [],
            'structs': [],
            'unions': [],
            'enums': [],
            'macro_definitions': [],
            'unsorted': []
        }

    def _sort_toplevel_nodes(self):
        """
        Sort all toplevel nodes in the corresponding lists in
        self.unparsed_nodes.
        """
        # Loop through all top level nodes and sort them by CursorKind.
        for cursor in self.cursor.get_children():
            # Filter out all nodes that do not have their origin in a file in
            # the same directory as the root header file.
            if not cursor.location.file or \
                not (os.path.abspath(cursor.location.file.name) in \
                self.files_to_parse):
                continue
            # Get the kind of the current node and sort them in the
            # provided lists.
            kind = cursor.kind
            if kind == CursorKind.TYPEDEF_DECL:
                self.unparsed_nodes['typedefs'].append(cursor)
            elif kind == CursorKind.FUNCTION_DECL:
                self.unparsed_nodes['functionprotos'].append(cursor)
            elif kind == CursorKind.STRUCT_DECL:
                self.unparsed_nodes['structs'].append(cursor)
            elif kind == CursorKind.UNION_DECL:
                self.unparsed_nodes['unions'].append(cursor)
            elif kind == CursorKind.ENUM_DECL:
                self.unparsed_nodes['enums'].append(cursor)
            elif kind == CursorKind.MACRO_DEFINITION:
                self.unparsed_nodes['macro_definitions'].append(cursor)
            else:
                self.unparsed_nodes['unsorted'].append(cursor)

    def parse_all_nodes(self):
        """
        Parses all currently unparsed nodes in self.unparsed_nodes.
        """
        self.parse_macro_definition_nodes()
        self.parse_struct_nodes()
        self.parse_union_nodes()
        self.parse_enum_nodes()
        self.parse_function_prototype_nodes()

        # Figure out the already given names. Typedefs cannot use these again.
        # Mainly just important for e.g.
        #   struct Example;
        #   typedef struct Example Example;
        # which maps (in Cython) to
        #   cdef struct Example:
        #       pass
        # Therefore the typedef will be omitted in this case because it is not
        # needed (nor possible to assign) in Cython.
        self.type_names = []
        node_types = ['structs', 'unions', 'enums']
        for node_name in node_types:
            nodes = self.parsed_nodes[node_name]
            for node in nodes:
                self.type_names.append(node.node_name)

        # Typedef nodes need to be parsed at the end.
        self.parse_typedef_nodes()


    def parse_macro_definition_nodes(self):
        for node in self.unparsed_nodes['macro_definitions']:
            macro_node = MacroDefinitionNode(node, parser=self)
            # Only append define constants. Preprocessor macros are not
            # supported and likely never will be supported for conversion to
            # Cython header files. Types would need to be declared and that
            # cannot be done automatically.
            if macro_node.is_define_constant is True:
                self.parsed_nodes['macro_definitions'].append(macro_node)

    def parse_typedef_nodes(self):
        for t_node in self.unparsed_nodes['typedefs']:
            node = TypedefNode(t_node, parser=self)
            self.parsed_nodes['typedefs'].append(node)

    def parse_struct_nodes(self):
        for struct_node in self.unparsed_nodes['structs']:
            self.parsed_nodes['structs'].append(StructNode(struct_node, parser=self))

    def parse_union_nodes(self):
        for union_node in self.unparsed_nodes['unions']:
            self.parsed_nodes['unions'].append(UnionNode(union_node,
                                                         parser=self))

    def parse_enum_nodes(self):
        for enum_node in self.unparsed_nodes['enums']:
            self.parsed_nodes['enums'].append(EnumNode(enum_node, parser=self))

    def parse_function_prototype_nodes(self):
        for proto in self.unparsed_nodes['functionprotos']:
            self.parsed_nodes['functionprotos'].append(
                FunctionProtoNode(proto, parser=self))

    def parse_external_types(self):
        self.sorted_external_types = {}
        # Sort by origin file
        for e_type in self.type_collection:
            e_type = e_type.get_declaration()
            # Do not consider files that are part of the library and parsed
            # anyway.
            if e_type.location.file is None:
                continue
            filepath = os.path.abspath(e_type.location.file.name)
            if filepath in self.files_to_parse:
                continue
            if filepath not in self.sorted_external_types:
                self.sorted_external_types[filepath] = []
            if e_type not in self.sorted_external_types[filepath]:
                self.sorted_external_types[filepath].append(e_type)

    def render_external_types(self, file_object):
        for key, value in self.sorted_external_types.iteritems():
            filename = os.path.basename(key)
            file_object.write('cdef extern from "%s" nogil:\n' % filename)
            # XXX: Currently only works with typedef nodes, but I think that
            # covers most uses. Will raise a more or less meaningful error if
            # an unexpected node arrives.
            for node in value:
                node = TypedefNode(node, self, use_canonical_type=True)
                # It oftentimes a typedef to a struct or a union. This needs to
                # be handled.
                # XXX: Also handle other types.
                if node.original_type.kind == TypeKind.RECORD:
                    org_decl = node.original_type.get_declaration()
                    if org_decl.kind == CursorKind.STRUCT_DECL:
                        org_name = 'struct'
                    elif org_decl.kind == CursorKind.UNION_DECL:
                        org_name = 'union'
                    elif org_decl.kind == CursorKind.ENUM_DECL:
                        org_name = 'enum'
                    else:
                        raise NotImplementedError
                    file_object.write('%scdef %s %s:\n%s%spass\n' % \
                        (TAB, org_name, org_decl.spelling, TAB, TAB))
                # Write the actual typedef.
                file_object.write('%s%s\n' % (TAB, node.get_cython_string()))
            # Write one empty line at the end.
            file_object.write('\n')

    def render_cython_header(self, filename_or_object):
        if isinstance(filename_or_object, basestring):
            with open(filename_or_object, 'w') as file_object:
                self._render_cython_header(file_object)
            return
        self._render_cython_header(filename_or_object)

    def _render_cython_header(self, file_object):
        self.render_external_types(file_object)

        file_object.write('cdef extern from "%s" nogil:\n' % \
                          os.path.basename(self.filename))
        node_names = ['macro_definitions', 'enums', 'structs', 'unions',
                      'typedefs', 'functionprotos']
        for name in node_names:
            if len(self.parsed_nodes[name]) == 0:
                continue
            # file_object.write('#' + 78 * '=' + '\n')
            # file_object.write('# %s\n' % name.upper())
            for node in self.parsed_nodes[name]:
                if name == 'typedefs' and node.node_name in self.type_names:
                    continue
                cython_string = node.get_cython_string().splitlines(True)
                for line in cython_string:
                    file_object.write('%s%s' % (TAB, line))
                file_object.write('\n')
            file_object.write('\n')
