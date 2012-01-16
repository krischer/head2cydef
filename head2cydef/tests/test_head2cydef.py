import inspect
import os
import tempfile
import unittest

from head2cydef import CFileParser
import testing_constructs


class TestHeaderToCython(unittest.TestCase):
    def setUp(self):
        self.data_path = os.path.join(
            os.path.split(inspect.getfile(inspect.currentframe()))[0],
            'test_files')
        # Most tests require a temporary file. Create a filename here.
        temp_file = tempfile.NamedTemporaryFile(delete=False)
        self.temp_file = temp_file.name + '.c'
        temp_file.close()

    def tearDown(self):
        # Delete the temp file after every test run.
        if os.path.exists(self.temp_file):
            os.remove(self.temp_file)

    def writeToTempFile(self, string):
        with open(self.temp_file, 'w') as file_object:
            file_object.write(string)

    def test_structParsingAndConversion(self):
        """
        Test the parsing and conversion of a simple struct.
        """
        self.writeToTempFile(testing_constructs.simple_struct)
        c_parser = CFileParser(self.temp_file)
        # This should contain exactly one struct.
        self.assertEqual(len(c_parser.unparsed_nodes['structs']), 1)
        # Parse the nodes.
        # The C output in this case should be identical to the input.
        struct_node = c_parser.parsed_nodes['structs'][0]
        self.assertEqual(struct_node.get_C_string(),
                         testing_constructs.simple_struct)
        # Test the created Cython code against the manually converted one.
        self.assertEqual(struct_node.get_cython_string(),
                         testing_constructs.simple_struct_cython)

    def test_directlyTypedefedStructParsingAndConversion(self):
        """
        Test the parsing and conversion of a directly typedefed struct.
        """
        self.writeToTempFile(testing_constructs.typedef_struct_version_1)
        c_parser = CFileParser(self.temp_file)
        # This should contain exactly one typedef.
        self.assertEqual(len(c_parser.unparsed_nodes['typedefs']), 1)
        # Parse the nodes.
        # The C output in this case should be identical to the input.
        t_node = c_parser.parsed_nodes['typedefs'][0]
        self.assertEqual(t_node.get_C_string(),
                         testing_constructs.typedef_struct_version_1)
        # Test the created Cython code against the manually converted one.
        self.assertEqual(t_node.get_cython_string(),
                         testing_constructs.typedef_struct_version_1_cython)

    def test_typedefedStructParsingAndConversion(self):
        """
        Test the parsing and conversion of a typedefed struct.
        """
        self.writeToTempFile(testing_constructs.typedef_struct_version_2)
        c_parser = CFileParser(self.temp_file)
        # This should contain exactly one typedef.
        self.assertEqual(len(c_parser.unparsed_nodes['typedefs']), 1)
        # Parse the nodes.
        # The C output in this case should be identical to the input.
        t_node = c_parser.parsed_nodes['typedefs'][0]
        self.assertEqual(t_node.get_C_string(),
                         testing_constructs.typedef_struct_version_2)
        # Test the created Cython code against the manually converted one.
        self.assertEqual(t_node.get_cython_string(),
                         testing_constructs.typedef_struct_version_2_cython)

    def test_typedefedStructSameNameParsingAndConversion(self):
        """
        Test the parsing and conversion of a typedefed struct that has the same
        name for the typedef and the struct.
        """
        self.writeToTempFile(testing_constructs.typedef_struct_version_3)
        c_parser = CFileParser(self.temp_file)
        # This should contain exactly one typedef.
        self.assertEqual(len(c_parser.unparsed_nodes['typedefs']), 1)
        # Parse the nodes.
        # The C output in this case should be identical to the input.
        t_node = c_parser.parsed_nodes['typedefs'][0]
        self.assertEqual(t_node.get_C_string(),
                         testing_constructs.typedef_struct_version_3)
        # Test the created Cython code against the manually converted one.
        self.assertEqual(t_node.get_cython_string(),
                         testing_constructs.typedef_struct_version_3_cython)


    def test_functionPrototypes(self):
        """
        Tests conversion of functionprototypes.
        """
        self.writeToTempFile(testing_constructs.function_prototypes)
        c_parser = CFileParser(self.temp_file)
        # This should contain exactly one typedef.
        self.assertEqual(len(c_parser.unparsed_nodes['functionprotos']), 4)
        # Parse the nodes.
        # The C output in this case should be identical to the input.
        c_strings = testing_constructs.function_prototypes.split('\n')
        cy_strings = testing_constructs.function_prototypes_cython.split('\n')
        for _i, node in enumerate(c_parser.parsed_nodes['functionprotos']):
            self.assertEqual(node.get_C_string(),
                             c_strings[_i])
            # Test the created Cython code against the manually converted one.
            self.assertEqual(node.get_cython_string(),
                             cy_strings[_i])

    def test_simpleTypedefs(self):
        """
        Tests the conversion of simple typedefs.
        """
        self.writeToTempFile(testing_constructs.simple_typedefs)
        c_parser = CFileParser(self.temp_file)
        # This should contain exactly one typedef.
        self.assertEqual(len(c_parser.unparsed_nodes['typedefs']), 3)
        # Parse the nodes.
        # The C output in this case should be identical to the input.
        c_strings = testing_constructs.simple_typedefs.split('\n')
        cy_strings = testing_constructs.simple_typedefs_cython.split('\n')
        for _i, node in enumerate(c_parser.parsed_nodes['typedefs']):
            self.assertEqual(node.get_C_string(),
                             c_strings[_i])
            # Test the created Cython code against the manually converted one.
            self.assertEqual(node.get_cython_string(),
                             cy_strings[_i])

    def test_simpleUnion(self):
        """
        Tests the conversion of a simple union.
        """
        self.writeToTempFile(testing_constructs.simple_union)
        c_parser = CFileParser(self.temp_file)
        # This should contain exactly one struct.
        self.assertEqual(len(c_parser.unparsed_nodes['unions']), 1)
        # Parse the nodes.
        # The C output in this case should be identical to the input.
        union_node = c_parser.parsed_nodes['unions'][0]
        self.assertEqual(union_node.get_C_string(),
                         testing_constructs.simple_union)
        # Test the created Cython code against the manually converted one.
        self.assertEqual(union_node.get_cython_string(),
                         testing_constructs.simple_union_cython)

    def test_directlyTypedefedUnion(self):
        """
        Test the parsing and conversion of a directly typedefed union.
        """
        self.writeToTempFile(testing_constructs.typedef_union_version_1)
        c_parser = CFileParser(self.temp_file)
        # This should contain exactly one typedef.
        self.assertEqual(len(c_parser.unparsed_nodes['typedefs']), 1)
        # Parse the nodes.
        # The C output in this case should be identical to the input.
        t_node = c_parser.parsed_nodes['typedefs'][0]
        self.assertEqual(t_node.get_C_string(),
                         testing_constructs.typedef_union_version_1)
        # Test the created Cython code against the manually converted one.
        self.assertEqual(t_node.get_cython_string(),
                         testing_constructs.typedef_union_version_1_cython)

    def test_typedefedUnion(self):
        """
        Test the parsing and conversion of a typedefed union.
        """
        self.writeToTempFile(testing_constructs.typedef_union_version_2)
        c_parser = CFileParser(self.temp_file)
        # This should contain exactly one typedef.
        self.assertEqual(len(c_parser.unparsed_nodes['typedefs']), 1)
        # Parse the nodes.
        # The C output in this case should be identical to the input.
        t_node = c_parser.parsed_nodes['typedefs'][0]
        self.assertEqual(t_node.get_C_string(),
                         testing_constructs.typedef_union_version_2)
        # Test the created Cython code against the manually converted one.
        self.assertEqual(t_node.get_cython_string(),
                         testing_constructs.typedef_union_version_2_cython)

    def test_typedefedUnionSameName(self):
        """
        Test the parsing and conversion of a typedefed union that has the same
        name for the typedef and the union.
        """
        self.writeToTempFile(testing_constructs.typedef_union_version_3)
        c_parser = CFileParser(self.temp_file)
        # This should contain exactly one typedef.
        self.assertEqual(len(c_parser.unparsed_nodes['typedefs']), 1)
        # Parse the nodes.
        # The C output in this case should be identical to the input.
        t_node = c_parser.parsed_nodes['typedefs'][0]
        self.assertEqual(t_node.get_C_string(),
                         testing_constructs.typedef_union_version_3)
        # Test the created Cython code against the manually converted one.
        self.assertEqual(t_node.get_cython_string(),
                         testing_constructs.typedef_union_version_3_cython)

    def test_simpleEnun(self):
        """
        Tests the conversion of a simple enum.
        """
        self.writeToTempFile(testing_constructs.simple_enum)
        c_parser = CFileParser(self.temp_file)
        # This should contain exactly one struct.
        self.assertEqual(len(c_parser.unparsed_nodes['enums']), 1)
        # Parse the nodes.
        # The C output in this case should be identical to the input.
        enum_node = c_parser.parsed_nodes['enums'][0]
        self.assertEqual(enum_node.get_C_string(),
                         testing_constructs.simple_enum)
        # Test the created Cython code against the manually converted one.
        self.assertEqual(enum_node.get_cython_string(),
                         testing_constructs.simple_enum_cython)

    def test_directlyTypedefedEnum(self):
        """
        Test the parsing and conversion of a directly typedefed enum.
        """
        self.writeToTempFile(testing_constructs.typedef_enum_version_1)
        c_parser = CFileParser(self.temp_file)
        # This should contain exactly one typedef.
        self.assertEqual(len(c_parser.unparsed_nodes['typedefs']), 1)
        # Parse the nodes.
        # The C output in this case should be identical to the input.
        t_node = c_parser.parsed_nodes['typedefs'][0]
        self.assertEqual(t_node.get_C_string(),
                         testing_constructs.typedef_enum_version_1)
        # Test the created Cython code against the manually converted one.
        self.assertEqual(t_node.get_cython_string(),
                         testing_constructs.typedef_enum_version_1_cython)

    def test_typedefedEnum(self):
        """
        Test the parsing and conversion of a typedefed enum.
        """
        self.writeToTempFile(testing_constructs.typedef_enum_version_2)
        c_parser = CFileParser(self.temp_file)
        # This should contain exactly one typedef.
        self.assertEqual(len(c_parser.unparsed_nodes['typedefs']), 1)
        # Parse the nodes.
        # The C output in this case should be identical to the input.
        t_node = c_parser.parsed_nodes['typedefs'][0]
        self.assertEqual(t_node.get_C_string(),
                         testing_constructs.typedef_enum_version_2)
        # Test the created Cython code against the manually converted one.
        self.assertEqual(t_node.get_cython_string(),
                         testing_constructs.typedef_enum_version_2_cython)

    def test_typedefedEnumSameName(self):
        """
        Test the parsing and conversion of a typedefed enum that has the same
        name for the typedef and the enum.
        """
        self.writeToTempFile(testing_constructs.typedef_enum_version_3)
        c_parser = CFileParser(self.temp_file)
        # This should contain exactly one typedef.
        self.assertEqual(len(c_parser.unparsed_nodes['typedefs']), 1)
        # Parse the nodes.
        # The C output in this case should be identical to the input.
        t_node = c_parser.parsed_nodes['typedefs'][0]
        self.assertEqual(t_node.get_C_string(),
                         testing_constructs.typedef_enum_version_3)
        # Test the created Cython code against the manually converted one.
        self.assertEqual(t_node.get_cython_string(),
                         testing_constructs.typedef_enum_version_3_cython)

    def test_typedefsInFunctions(self):
        """
        Test if a typedef in a function gets parsed correctly.
        """
        self.writeToTempFile(testing_constructs.typedef_in_function)
        c_parser = CFileParser(self.temp_file)
        # This should contain exactly one typedef.
        self.assertEqual(len(c_parser.unparsed_nodes['typedefs']), 1)
        self.assertEqual(len(c_parser.unparsed_nodes['functionprotos']), 1)
        # Parse the nodes.
        # The C output in this case should be identical to the input.
        t_node = c_parser.parsed_nodes['typedefs'][0]
        self.assertEqual(t_node.get_C_string(),
                         testing_constructs.typedef_in_function.split('\n')[0])
        func_node = c_parser.parsed_nodes['functionprotos'][0]
        self.assertEqual(func_node.get_C_string(),
                 testing_constructs.typedef_in_function.split('\n')[1])
        # Test the created Cython code against the manually converted one.
        self.assertEqual(t_node.get_cython_string(),
                 testing_constructs.typedef_in_function_cython.split('\n')[0])
        self.assertEqual(func_node.get_cython_string(),
                 testing_constructs.typedef_in_function_cython.split('\n')[1])

    def test_filteringOfTypedefedStructsEnumsUnions(self):
        """
        A typedef'ed struct, union or enum will (due a debatable design choice)
        be parsed and completely handled by the typedef.
        In clang they also appear seperately as structs, unions or enums. These
        duplicates have to be removed.
        """
        # For structs.
        self.writeToTempFile(testing_constructs.typedef_struct_version_2)
        c_parser = CFileParser(self.temp_file)
        # Before the nodes are actually parsed, struct and typedef are both
        # available.
        self.assertEqual(len(c_parser.unparsed_nodes['typedefs']), 1)
        self.assertEqual(len(c_parser.unparsed_nodes['structs']), 1)
        # Parse the nodes.
        # After parsing all nodes the struct should be removed.
        self.assertEqual(len(c_parser.parsed_nodes['typedefs']), 1)
        self.assertEqual(len(c_parser.parsed_nodes['structs']), 0)

        # For unions.
        self.writeToTempFile(testing_constructs.typedef_union_version_2)
        c_parser = CFileParser(self.temp_file)
        # Before the nodes are actually parsed, struct and typedef are both
        # available.
        self.assertEqual(len(c_parser.unparsed_nodes['typedefs']), 1)
        self.assertEqual(len(c_parser.unparsed_nodes['unions']), 1)
        # Parse the nodes.
        # After parsing all nodes the struct should be removed.
        self.assertEqual(len(c_parser.parsed_nodes['typedefs']), 1)
        self.assertEqual(len(c_parser.parsed_nodes['unions']), 0)

        # For enums.
        self.writeToTempFile(testing_constructs.typedef_enum_version_2)
        c_parser = CFileParser(self.temp_file)
        # Before the nodes are actually parsed, struct and typedef are both
        # available.
        self.assertEqual(len(c_parser.unparsed_nodes['typedefs']), 1)
        self.assertEqual(len(c_parser.unparsed_nodes['enums']), 1)
        # Parse the nodes.
        # After parsing all nodes the struct should be removed.
        self.assertEqual(len(c_parser.parsed_nodes['typedefs']), 1)
        self.assertEqual(len(c_parser.parsed_nodes['enums']), 0)

    def test_filteringOfTypedefedStructsEnumsUnions_2(self):
        """
        A typedef'ed struct, union or enum will (due a debatable design choice)
        be parsed and completely handled by the typedef.
        In clang they also appear seperately as structs, unions or enums. These
        duplicates have to be removed.

        Second test for this that tests that the other structs, enums and
        unions are left untouched.
        """
        self.writeToTempFile(testing_constructs.typedefed_and_normal_constructs)
        c_parser = CFileParser(self.temp_file)
        # Before the nodes are actually parsed, structs, enums, unions and
        # typedefs are available.
        self.assertEqual(len(c_parser.unparsed_nodes['typedefs']), 3)
        self.assertEqual(len(c_parser.unparsed_nodes['structs']), 2)
        self.assertEqual(len(c_parser.unparsed_nodes['enums']), 2)
        self.assertEqual(len(c_parser.unparsed_nodes['unions']), 2)
        # Parse the nodes.
        # After parsing all nodes the struct should be removed.
        self.assertEqual(len(c_parser.parsed_nodes['typedefs']), 3)
        self.assertEqual(len(c_parser.parsed_nodes['structs']), 1)
        self.assertEqual(len(c_parser.parsed_nodes['enums']), 1)
        self.assertEqual(len(c_parser.parsed_nodes['unions']), 1)

    def test_defineConstants(self):
        """
        Define constants should be converted to dummy enum definitions.
        """
        self.writeToTempFile(testing_constructs.define_constants)
        c_parser = CFileParser(self.temp_file)
        # Check if the macros are actually read.
        self.assertEqual(len(c_parser.unparsed_nodes['unsorted']), 0)
        self.assertEqual(len(c_parser.unparsed_nodes['macro_definitions']), 3)
        # Parse the nodes.
        # True macros should be filtered out.
        self.assertEqual(len(c_parser.parsed_nodes['macro_definitions']), 2)
        nodes = c_parser.parsed_nodes['macro_definitions']
        cython_string = '\n'.join([_i.get_cython_string() for _i in nodes])
        self.assertEqual(cython_string,
                         testing_constructs.define_constants_cython)

    def test_functionPointerTypedefs(self):
        """
        """
        self.writeToTempFile(testing_constructs.typedef_function_pointer)
        c_parser = CFileParser(self.temp_file)
        self.assertEqual(len(c_parser.unparsed_nodes['typedefs']), 1)
        # Parse the nodes.
        node = c_parser.parsed_nodes['typedefs'][0]
        self.assertEqual(node.get_C_string(),
                         testing_constructs.typedef_function_pointer)
        self.assertEqual(node.get_cython_string(),
                         testing_constructs.typedef_function_pointer_cython)

    def test_arrayTypedefs(self):
        """
        Arrays can also be typedefs.
        """
        self.writeToTempFile(testing_constructs.typedef_array)
        c_parser = CFileParser(self.temp_file)
        self.assertEqual(len(c_parser.unparsed_nodes['typedefs']), 1)
        # Parse the nodes.
        node = c_parser.parsed_nodes['typedefs'][0]
        self.assertEqual(node.get_C_string(),
                         testing_constructs.typedef_array)
        self.assertEqual(node.get_cython_string(),
                         testing_constructs.typedef_array_cython)

    def test_functionPointersInStructs(self):
        """
        """
        self.writeToTempFile(testing_constructs.function_pointer_struct)
        c_parser = CFileParser(self.temp_file)
        self.assertEqual(len(c_parser.unparsed_nodes['structs']), 1)
        node = c_parser.parsed_nodes['structs'][0]
        self.assertEqual(node.get_C_string(),
                         testing_constructs.function_pointer_struct)
        self.assertEqual(node.get_cython_string(),
                         testing_constructs.function_pointer_struct_cython)

    def test_emptyTypedefStruct(self):
        """
        """
        self.writeToTempFile(testing_constructs.empty_typedef_struct)
        c_parser = CFileParser(self.temp_file)
        self.assertEqual(len(c_parser.unparsed_nodes['structs']), 1)
        self.assertEqual(len(c_parser.unparsed_nodes['typedefs']), 1)
        self.assertEqual(len(c_parser.parsed_nodes['structs']), 0)
        self.assertEqual(len(c_parser.parsed_nodes['typedefs']), 1)
        node = c_parser.parsed_nodes['typedefs'][0]
        self.assertEqual(node.get_cython_string(),
                         testing_constructs.empty_typedef_struct_cython)

    def test_selfReferencingStruct(self):
        """
        """
        self.writeToTempFile(testing_constructs.self_referencing_struct)
        c_parser = CFileParser(self.temp_file)
        self.assertEqual(len(c_parser.unparsed_nodes['structs']), 1)
        self.assertEqual(len(c_parser.unparsed_nodes['typedefs']), 1)
        self.assertEqual(len(c_parser.parsed_nodes['structs']), 0)
        self.assertEqual(len(c_parser.parsed_nodes['typedefs']), 1)
        node = c_parser.parsed_nodes['typedefs'][0]
        self.assertEqual(node.get_cython_string(),
                         testing_constructs.self_referencing_struct_cython)



if __name__ == '__main__':
    unittest.main()
