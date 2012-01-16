"""
Contains short C Code snippets and their corresponding Cython definition.

The main reason that these are in an extra file is that indents in the Cython
code are vital and they are just a mess to preserve if the strings were put in
a normal function (which is already has an indention level of at least one).
"""

# Some simple typedefs
simple_typedefs = """
typedef int newInt;
typedef float newFloat;
typedef newInt newerInt;
""".strip()
simple_typedefs_cython = """
ctypedef int newInt
ctypedef float newFloat
ctypedef newInt newerInt
""".strip()


# A simple and plain structure.
simple_struct = """
struct testStruct {
    float* member_a;
    int member_b;
};
""".strip()
simple_struct_cython = """
cdef struct testStruct:
    float* member_a
    int member_b
""".strip()


# A directly typecasted struct
typedef_struct_version_1 = """
typedef struct {
    float* member_a;
    int member_b;
} testStruct;
""".strip()
typedef_struct_version_1_cython = """
ctypedef struct testStruct:
    float* member_a
    int member_b
""".strip()


# A typecasted and named struct.
typedef_struct_version_2 = """
typedef struct test_struct {
    float* member_a;
    int member_b;
} testStruct;
""".strip()
typedef_struct_version_2_cython = """
cdef struct test_struct:
    float* member_a
    int member_b
ctypedef test_struct testStruct
""".strip()


# A typecasted and named struct that both have the same name..
typedef_struct_version_3 = """
typedef struct testStruct {
    float* member_a;
    int member_b;
} testStruct;
""".strip()
typedef_struct_version_3_cython = """
cdef struct testStruct:
    float* member_a
    int member_b
""".strip()


# Some function prototypes.
function_prototypes = """
char** test_method(int* a, double d);
int add(double ada, float* bda);
float* mult(float aa, int bb);
double** dmult(double a, float b);
""".strip()
# Some function prototypes.
function_prototypes_cython = """
char** test_method(int* a, double d)
int add(double ada, float* bda)
float* mult(float aa, int bb)
double** dmult(double a, float b)
""".strip()


# Simple union.
simple_union = """
union testUnion {
    int* a;
    float b;
};
""".strip()
simple_union_cython = """
cdef union testUnion:
    int* a
    float b
""".strip()


# A directly typecasted union
typedef_union_version_1 = """
typedef union {
    float* member_a;
    int member_b;
} testUnion;
""".strip()
typedef_union_version_1_cython = """
ctypedef union testUnion:
    float* member_a
    int member_b
""".strip()


# A typecasted and named union.
typedef_union_version_2 = """
typedef union test_union {
    float* member_a;
    int member_b;
} testUnion;
""".strip()
typedef_union_version_2_cython = """
cdef union test_union:
    float* member_a
    int member_b
ctypedef test_union testUnion
""".strip()


# A typecasted and named union that both have the same name..
typedef_union_version_3 = """
typedef union testUnion {
    float* member_a;
    int member_b;
} testUnion;
""".strip()
typedef_union_version_3_cython = """
cdef union testUnion:
    float* member_a
    int member_b
""".strip()

# A simple enum.
simple_enum = """
enum week {
    Mon,
    Tue,
    Wen,
    Thu,
    Fri,
    Sat,
    Sun
};
""".strip()
simple_enum_cython = """
cdef enum week:
    Mon
    Tue
    Wen
    Thu
    Fri
    Sat
    Sun
""".strip()


# A directly typecasted enum
typedef_enum_version_1 = """
typedef enum {
    member_a,
    member_b
} testEnum;
""".strip()
typedef_enum_version_1_cython = """
ctypedef enum testEnum:
    member_a
    member_b
""".strip()


# A typecasted and named enum.
typedef_enum_version_2 = """
typedef enum test_enum {
    member_a,
    member_b
} testEnum;
""".strip()
typedef_enum_version_2_cython = """
cdef enum test_enum:
    member_a
    member_b
ctypedef test_enum testEnum
""".strip()


# A typecasted and named union that both have the same name..
typedef_enum_version_3 = """
typedef enum testEnum {
    member_a,
    member_b
} testEnum;
""".strip()
typedef_enum_version_3_cython = """
cdef enum testEnum:
    member_a
    member_b
""".strip()


# A typedeffed type in a function
typedef_in_function = """
typedef float newFloat;
newFloat* doStuff(newFloat a, float* b);
""".strip()
typedef_in_function_cython = """
ctypedef float newFloat
newFloat* doStuff(newFloat a, float* b)
""".strip()


# typedef'ed and normal struct, unions and enums
typedefed_and_normal_constructs = """
typedef struct test_struct {
    int member_a;
    double member_b;
} testStruct;
struct otherStruct {
    int item_one;
    float item_two;
}

typedef union test_union {
    int member_a;
    float member;
} testUnion;
union otherUnion {
    int item_one;
    float item_two;
}

typedef enum test_enum {
    member_a,
    member_b
} testEnum;
enum otherEnum {
    item_one,
    item_two
}
""".strip()


# define constants should be defines as dummy enums. Only simple define
# constants are translated to Cython code.
define_constants = """
#define PI 2.71
# define long_macro something
#define DO(X) X*X
""".strip()
define_constants_cython = """
cdef enum PI:
    pass
cdef enum long_macro:
    pass
""".strip()


# Function pointer typedef.
typedef_function_pointer = """
typedef float (*func_point)(int param1, void* param2);
""".strip()
typedef_function_pointer_cython = """
ctypedef float (*func_point)(int param1, void* param2)
""".strip()


# Arrays can also be typedefs.
typedef_array = """
typedef int intArrayFive[5];
""".strip()
typedef_array_cython = """
ctypedef int intArrayFive[5]
""".strip()


# function pointers in structs
function_pointer_struct = """
struct FPStruct {
    void (*Function) (float* func_param);
    int other_member;
};
""".strip()
function_pointer_struct_cython = """
cdef struct FPStruct:
    void (*Function) (float* func_param)
    int other_member
""".strip()


# Test an empty struct
empty_typedef_struct = """
struct SDL_mutex;
typedef struct SDL_mutex SDL_mutex;
""".strip()
empty_typedef_struct_cython = """
cdef struct SDL_mutex:
    pass
""".strip()

# Self referencing struct in function pointer that is a member of the struct.
self_referencing_struct = """
typedef struct TestingStruct
{
    long (*function_name) (struct TestingStruct* self_reference, long param_2);
} TestingStruct;
""".strip()
self_referencing_struct_cython = """
cdef struct TestingStruct:
    long (*function_name) (TestingStruct* self_reference, long param_2)
""".strip()
