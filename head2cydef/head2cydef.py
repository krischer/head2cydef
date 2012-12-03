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

        # Get all includes.
        self.includes = []
        for _i in self.translation_unit.get_includes():
            # if os.path.abspath(_i.location.file.name) in self.files_to_parse \
            #    and os.path.abspath(_i.include.name) not in self.files_to_parse:
            self.includes.append(_i)
        # Get the exact include statement.
        # XXX: I could not find a way to do this within clang. Is there one?
        self.include_map = {}
        for inc in self.includes:
            # Open the file to read the correct line.
            with open(inc.location.file.name, 'r') as open_file:
                line_of_interest = inc.location.line
                for _i, line in enumerate(open_file):
                    if _i + 1 < line_of_interest:
                        continue
                    elif _i + 1 == line_of_interest:
                        include_line = line
                        break
                    else:
                        break
            # XXX: Replace with regex!
            include_line = include_line.replace('#', '')
            include_line = include_line.replace('include', '')
            include_line = include_line.replace('<', '')
            include_line = include_line.replace('>', '')
            include_line = include_line.replace('"', '')
            # XXX: What is this include_next thing??
            #      Maybe something llvm exclusive?
            include_line = include_line.replace('_next', '')
            include_line = include_line.replace('"', '').strip()

            include_filename = os.path.abspath(inc.include.name)
            if include_filename in self.include_map:
                if self.include_map[include_filename] != include_line:
                    msg = 'Includes referencing same file included with ' + \
                          'different statements.'
                    raise Exeption(msg)
            else:
                self.include_map[include_filename] = include_line
            # if 'next' in self.include_map[include_filename]:
            #     from IPython.core.debugger import Tracer; Tracer()()

        self._setup_data_structure()
        self._sort_toplevel_nodes()
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

        self.all_parsed_nodes = []
        self.unsorted_nodes = []

    def _sort_toplevel_nodes(self):
        """
        Sort all toplevel nodes in the corresponding lists in
        self.unparsed_nodes.
        """
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
                self.all_parsed_nodes.append(TypedefNode(cursor, parser=self))
            elif kind == CursorKind.FUNCTION_DECL:
                self.all_parsed_nodes.append(FunctionProtoNode(cursor,
                                                               parser=self))
            elif kind == CursorKind.STRUCT_DECL:
                node = StructNode(cursor, parser=self)
                self.type_names.append(node.node_name)
                self.all_parsed_nodes.append(node)
            elif kind == CursorKind.UNION_DECL:
                node = UnionNode(cursor, parser=self)
                self.type_names.append(node.node_name)
                self.all_parsed_nodes.append(node)
            elif kind == CursorKind.ENUM_DECL:
                node = EnumNode(cursor, parser=self)
                self.type_names.append(node.node_name)
                self.all_parsed_nodes.append(node)
            elif kind == CursorKind.MACRO_DEFINITION:
                node = MacroDefinitionNode(cursor, parser=self)
                # Only append #define constants and no macros. These need to be
                # defined by hand due to unresolvable type issues.
                if node.is_define_constant is True:
                    self.all_parsed_nodes.append(node)
            else:
                self.unsorted_nodes.append(cursor)

    def parse_external_types(self):
        self.sorted_external_types = {}
        # Sort by origin file
        for e_type in self.type_collection:
            e_type = e_type.get_declaration()
            # Do not consider files that are part of the library and parsed
            # anyway.
            if e_type.location.file is None:
                continue
            include_path = e_type.location.file.name
            if os.path.abspath(include_path) in self.files_to_parse:
                continue
            if include_path not in self.sorted_external_types:
                self.sorted_external_types[include_path] = []
            if e_type not in self.sorted_external_types[include_path]:
                self.sorted_external_types[include_path].append(e_type)

    def render_external_types(self, file_object):
        for key, value in self.sorted_external_types.iteritems():
            try:
                self.include_map[key]
            except:
                from IPython.core.debugger import Tracer; Tracer()()
            file_object.write('cdef extern from "%s" nogil:\n' % \
                              self.include_map[key])
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

    def render_va_list_header(self, filename_or_object):
        """
        The va_list type is implementation specific. The current way should
        work with gcc and is untested with other compilers. va_start, va_end,
        ... are currently not supported because they are probably not used very
        much in C header files.
        """
        if not hasattr(self, 'is_va_list_used') or not self.is_va_list_used:
            return
        filename_or_object.write('cdef extern from "stdarg.h" nogil:\n' + \
                                 '%sctypedef void *va_list\n\n' % TAB)

    def _render_cython_header(self, file_object):
        self.render_external_types(file_object)
        self.render_va_list_header(file_object)

        file_object.write('cdef extern from "%s" nogil:\n' % \
                          os.path.basename(self.filename))
        for node in self.all_parsed_nodes:
            # Do not typedef already defined names. Mainly occurring if some
            # structure has the same name as a typedef to it.
            if isinstance(node, TypedefNode) and node.node_name in \
                self.type_names:
                continue
            cython_string = node.get_cython_string().splitlines(True)
            for line in cython_string:
                file_object.write('%s%s' % (TAB, line))
            file_object.write('\n')
