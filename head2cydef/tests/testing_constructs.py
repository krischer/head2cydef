"""
Contains short C Code snippets and their corresponding Cython definition.
"""
# This dictionary will contain tuples of code snippets. The first item is the C
# code and the second item the corresponding Cython code. All pairs in this
# dictionary are tested automatically.
testing_pairs = {}

# define constants should be defines as dummy enums. Only simple define
# constants are translated to Cython code, macro functions are ignored.
testing_pairs['define_constants'] = (
"""
#define PI 2.71
# define long_macro something
#define DO(X) X*X
""".strip(),
"""
cdef enum PI:
    pass
cdef enum long_macro:
    pass
""".strip()
)

# A plain and simple structure.
testing_pairs['simple_struct'] = (
"""
struct testStruct {
    float *member_a;
    int member_b;
};
""".strip(),
"""
cdef struct testStruct:
    float *member_a
    int member_b
""".strip()
)

# Simple union.
testing_pairs['simple_union'] = (
"""
union testUnion {
    int *a;
    float b;
};
""".strip(),
"""
cdef union testUnion:
    int *a
    float b
""".strip()
)

# Some simple typedefs.
testing_pairs['simple_typedefs'] = (
"""
typedef int newInt;
typedef float newFloat;
typedef newInt newerInt;
typedef float *floatPointer;
typedef float **floatDoublePointer;
typedef newFloat *newFloatPointer;
typedef newFloat **newFloatDoublePointer;
""".strip(),
"""
ctypedef int newInt
ctypedef float newFloat
ctypedef newInt newerInt
ctypedef float *floatPointer
ctypedef float **floatDoublePointer
ctypedef newFloat *newFloatPointer
ctypedef newFloat **newFloatDoublePointer
""".strip()
)

# Arrays can also be typedefs.
testing_pairs['typedef_arrays'] = (
"""
typedef int intArrayFive[5];
typedef int intArrayX[161];
typedef int newInt;
typedef newInt newIntArray[5];
""".strip(),
"""
ctypedef int intArrayFive[5]
ctypedef int intArrayX[161]
ctypedef int newInt
ctypedef newInt newIntArray[5]
""".strip()
)

# Assorted more complicated typedefs, but still consisting of native types.
testing_pairs['more_complicated_typedefs'] = (
"""
typedef char c, *cp, carr[100];
typedef c *arrayOfSixPointers[6];
typedef struct tnode *Treeptr;
typedef union tunion *TreePointerUnion;
""".strip(),
"""
cdef struct tnode:
    pass

cdef union tunion:
    pass

ctypedef char c
ctypedef char *cp
ctypedef char carr[100]
ctypedef c *arrayOfSixPointers[6]
ctypedef tnode *Treeptr
ctypedef tunion *TreePointerUnion
""".strip()
)

# Test an empty struct
testing_pairs['empty_typedef_struct'] = (
"""
struct Dummy_struct;
typedef struct Dummy_struct Dummy_struct;
""".strip(),
"""
cdef struct Dummy_struct:
    pass
""".strip()
)

# A directly typecasted struct
testing_pairs['directly_typecasted_struct'] = (
"""
typedef struct {
    float *member_a;
    int member_b;
} testStruct;
""".strip(),
"""
cdef struct Struct_temp_random_[[RANDOMINT]]:
    float *member_a
    int member_b

ctypedef Struct_temp_random_[[RANDOMINT]] testStruct
""".strip()
)

# A typecasted and named struct.
testing_pairs['typecasted_and_named_struct'] = (
"""
typedef struct test_struct {
    float* member_a;
    int member_b;
} testStruct;
""".strip(),
"""
cdef struct test_struct:
    float *member_a
    int member_b

ctypedef test_struct testStruct
""".strip()
)

# A typecasted and named struct that both have the same name..
testing_pairs['typecasted_and_named_struct_same_name'] = (
"""
typedef struct testStruct {
    float *member_a;
    int member_b;
} testStruct;
""".strip(),
"""
cdef struct testStruct:
    float *member_a
    int member_b
""".strip()
)

# A directly typecasted union
testing_pairs['directly_typecasted_union'] = (
"""
typedef union {
    float *member_a;
    int member_b;
} testUnion;
""".strip(),
"""
cdef union Union_temp_random_[[RANDOMINT]]:
    float *member_a
    int member_b

ctypedef Union_temp_random_[[RANDOMINT]] testUnion
""".strip()
)

# A typecasted and named union.
testing_pairs['typecasted_and_named_union'] = (
"""
typedef union test_union {
    float *member_a;
    int member_b;
} testUnion;
""".strip(),
"""
cdef union test_union:
    float *member_a
    int member_b

ctypedef test_union testUnion
""".strip()
)

# A typecasted and named union that both have the same name..
testing_pairs['typedef_union_same_name'] = (
"""
typedef union testUnion {
    float *member_a;
    int member_b;
} testUnion;
""".strip(),
"""
cdef union testUnion:
    float *member_a
    int member_b
""".strip()
)

# A simple enum.
testing_pairs['simple_enum'] = (
"""
enum week {
    Mon,
    Tue,
    Wen,
    Thu,
    Fri,
    Sat,
    Sun
};
""".strip(),
"""
cdef enum week:
    Mon
    Tue
    Wen
    Thu
    Fri
    Sat
    Sun
""".strip()
)

# A directly typecasted enum
testing_pairs['directly_typecasted_enum'] = (
"""
typedef enum {
    member_a,
    member_b
} testEnum;
""".strip(),
"""
cdef enum Enum_temp_random_[[RANDOMINT]]:
    member_a
    member_b

ctypedef Enum_temp_random_[[RANDOMINT]] testEnum
""".strip()
)

# A typecasted and named enum.
testing_pairs['typedef_enum'] = (
"""
typedef enum test_enum {
    member_a,
    member_b
} testEnum;
""".strip(),
"""
cdef enum test_enum:
    member_a
    member_b

ctypedef test_enum testEnum
""".strip()
)

# A typecasted and named enum that both have the same name..
testing_pairs['typedef_and_enum_with_same_name'] = (
"""
typedef enum testEnum {
    member_a,
    member_b
} testEnum;
""".strip(),
"""
cdef enum testEnum:
    member_a
    member_b
""".strip()
)

# typedef'ed and normal struct, unions and enums
testing_pairs['typedefed_and_normal_constructs'] = (
"""
typedef enum test_enum {
    member_a,
    member_b
} testEnum;

enum otherEnum {
    item_one,
    item_two
};

typedef struct test_struct {
    float* member_a;
    int member_b;
} testStruct;

struct otherStruct {
    int item_one;
    float item_two;
};

typedef union test_union {
    int member_a;
    float member;
} testUnion;

union otherUnion {
    int item_one;
    float item_two;
};
""".strip(),
"""
cdef enum test_enum:
    member_a
    member_b
cdef enum otherEnum:
    item_one
    item_two

cdef struct test_struct:
    float *member_a
    int member_b
cdef struct otherStruct:
    int item_one
    float item_two

cdef union test_union:
    int member_a
    float member
cdef union otherUnion:
    int item_one
    float item_two

ctypedef test_enum testEnum
ctypedef test_struct testStruct
ctypedef test_union testUnion
""".strip()
)

# Some function prototypes.
testing_pairs['function_prototypes'] = (
"""
char** test_method(int *a, double d);
int add(double ada, float *bda);
float* mult(float aa, int bb);
double** dmult(double a, float b);
""".strip(),
"""
char** test_method(int *a, double d)
int add(double ada, float *bda)
float* mult(float aa, int bb)
double** dmult(double a, float b)
""".strip()
)

# A typedeffed type in a function
testing_pairs['typedef_type_in_function'] = (
"""
typedef float newFloat;
newFloat* doStuff(newFloat a, float* b);
""".strip(),
"""
ctypedef float newFloat

newFloat* doStuff(newFloat a, float* b)
""".strip()
)

# Typedef cast.
testing_pairs['typedef_cast'] = (
"""
typedef float (*func_point)(int param1, void* param2);
""".strip(),
"""
ctypedef float (*func_point)(int param1, void* param2)
""".strip()
)

# function pointers in structs
testing_pairs['function_pointer_struct'] = (
"""
struct FPStruct {
    void (*Function) (float* func_param, int other_param);
    int other_member;
};
""".strip(),
"""
cdef struct FPStruct:
    void (*Function)(float* func_param, int other_param)
    int other_member
""".strip()
)

# Self referencing struct in function pointer that is a member of the struct.
testing_pairs['self_referencing_struct'] = (
"""
typedef struct TestingStruct
{
    long (*function_name) (struct TestingStruct* self_reference, long param_2);
} TestingStruct;
""".strip(),
"""
cdef struct TestingStruct:
    long (*function_name)(TestingStruct* self_reference, long param_2)
""".strip()
)
