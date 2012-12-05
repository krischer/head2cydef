# head2cydef - Autocreate Cython definition files

**head2cydef** translates C header files to corresponding Cython definition files
which are then used to call C libraries from Cython.

It leverages the Python bindings of the [clang](http://clang.llvm.org/)
compiler and is therefore able to deal with all kinds of shenanigans like
extensive macro usage and compiler specific functions. It can furthermore
follow dependencies across multiple typedefs and is very stable in regards to
syntax parsing. It could also be used to create Cython definition files for C++
headers, although this is not implemented yet.

## Installation
Currently tested with Python 2.7. First make sure the following dependencies are installed:

* clang (Short explanation and installation instructions can be found [here](https://github.com/krischer/head2cydef/blob/master/README.md))
* colorama (Only needed for the tests)


Clone the repository

```bash
git clone https://github.com/krischer/head2cydef.git
cd head2cydef
```

and then

```bash
pip install .
or
python setup.py install
```

## Usage

```python
>>> import head2cydef
>>> c_file = head2cydef.CFileParser("some_header_file.h")
>>> c_file.render_cython_header("some_header_file.pyx")
```

## Example Output

* [OpenGL](https://gist.github.com/4219796)
* [SDL](https://gist.github.com/4219808)
* [libmseed](https://gist.github.com/4219818)

## Testing

To run the tests, simply execute the `test/test_head2cydef.py` file. It
basically takes all tuples defined in `tests/testing_constructs.py` and checks
that the output of each block is correct. Each block has the style of a C
header file with the corresponding expected output in a Cython header file.
