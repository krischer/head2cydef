from colorama import init, Fore, Back, Style
import difflib
import doctest
import inspect
import os
import re
from StringIO import StringIO
import tempfile
import unittest

from head2cydef import CFileParser
from head2cydef import nodes
import testing_constructs
from testing_constructs import testing_pairs

init()

class HeaderToCythonTestCase(unittest.TestCase):
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
        Style.RESET_ALL

    def writeToTempFile(self, string):
        with open(self.temp_file, 'w') as file_object:
            file_object.write(string)

    def test_testingConstructs(self):
        print '%i code pairs tested' % len(testing_pairs.keys())
        for key, value in testing_pairs.iteritems():
            c_code = value[0]
            cython_code = value[1]
            self.writeToTempFile(c_code)
            # Parse the file.
            parser = CFileParser(self.temp_file)
            output_object = StringIO()
            parser.render_cython_header(output_object)
            output_object.seek(0, 0)
            output = output_object.read().strip()

            # Randomly created struct/unions/enums names are possible. These will
            # have the names
            #   Struct_temp_random_[[RANDOMINT]]
            #   Union_temp_random_[[RANDOMINT]]
            #   Enum_temp_random_[[RANDOMINT]]
            # in the reference Cython output. These will need to be replaced.
            struct_replacements = \
                    re.findall(r"Struct_temp_random_[0-9]{6}", output)
            union_replacements = \
                    re.findall(r"Union_temp_random_[0-9]{6}", output)
            enum_replacements = \
                    re.findall(r"Enum_temp_random_[0-9]{6}", output)
            if struct_replacements:
            #   Struct_temp_random_[[RANDOMINT]]
                cython_code = cython_code.replace(
                    "Struct_temp_random_[[RANDOMINT]]", struct_replacements[0])
            if union_replacements:
                cython_code = cython_code.replace(
                    "Union_temp_random_[[RANDOMINT]]", union_replacements[0])
            if enum_replacements:
                cython_code = cython_code.replace(
                    "Enum_temp_random_[[RANDOMINT]]", enum_replacements[0])

            # Use a custom assert method to print a meaningful and verbose
            # error message to facilitate debugging. Make it colorful because
            # it is needed quite a lot during development and just makes things
            # easier to spot.
            try:
                assert(output == cython_code)
            except AssertionError:
                d = difflib.Differ()
                diff = d.compare(output.splitlines(), cython_code.splitlines())
                diff = list(diff)

                print Fore.BLUE
                print '=' * 80
                print '=' * 80, Fore.RESET
                print 'Error in test construct:', Fore.GREEN, key, Fore.BLUE
                print '_' * 80, Fore.YELLOW
                print 'C code:', Fore.RESET
                print c_code, Fore.BLUE
                print '_' * 80, Fore.YELLOW
                print 'Expected cython code:', Fore.RESET
                print cython_code, Fore.BLUE
                print '_' * 80, Fore.YELLOW
                print 'Received cython code (- needs to go, + to get there):', Fore.RESET

                for line in diff:
                    if line.startswith('  '):
                        print Back.GREEN, Fore.WHITE, line[2:], Style.RESET_ALL
                    elif line.startswith('+ ') or \
                         line.startswith('- '):
                        print Back.RED, Fore.WHITE, line, Style.RESET_ALL
                print Fore.RESET, Back.RESET

                print Fore.BLUE
                print '=' * 80, Fore.BLUE
                print '=' * 80, Fore.RESET
                raise Exception


# Launch this files unit tests and the modules doctests.
if __name__ == '__main__':

    unittest_suite = \
        unittest.TestLoader().loadTestsFromTestCase(HeaderToCythonTestCase)
    doctest_suite = unittest.TestSuite()
    doctest_suite.addTest(doctest.DocTestSuite(nodes))

    alltests = unittest.TestSuite([unittest_suite, doctest_suite])
    unittest.main(defaultTest='alltests')
