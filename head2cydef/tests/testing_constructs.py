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
cdef extern from [[[FILENAME]]] nogil:
    enum: PI
    enum: long_macro
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
cdef extern from [[[FILENAME]]] nogil:
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
cdef extern from [[[FILENAME]]] nogil:
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
cdef extern from [[[FILENAME]]] nogil:
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
cdef extern from [[[FILENAME]]] nogil:
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
cdef extern from [[[FILENAME]]] nogil:
    ctypedef char c
    ctypedef char *cp
    ctypedef char carr[100]
    ctypedef c *arrayOfSixPointers[6]
    cdef struct tnode:
        pass
    ctypedef tnode *Treeptr
    cdef union tunion:
        pass
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
cdef extern from [[[FILENAME]]] nogil:
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
cdef extern from [[[FILENAME]]] nogil:
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
cdef extern from [[[FILENAME]]] nogil:
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
cdef extern from [[[FILENAME]]] nogil:
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
cdef extern from [[[FILENAME]]] nogil:
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
cdef extern from [[[FILENAME]]] nogil:
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
cdef extern from [[[FILENAME]]] nogil:
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
cdef extern from [[[FILENAME]]] nogil:
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
cdef extern from [[[FILENAME]]] nogil:
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
cdef extern from [[[FILENAME]]] nogil:
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
cdef extern from [[[FILENAME]]] nogil:
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
cdef extern from [[[FILENAME]]] nogil:
    cdef enum test_enum:
        member_a
        member_b
    ctypedef test_enum testEnum
    cdef enum otherEnum:
        item_one
        item_two
    cdef struct test_struct:
        float *member_a
        int member_b
    ctypedef test_struct testStruct
    cdef struct otherStruct:
        int item_one
        float item_two
    cdef union test_union:
        int member_a
        float member
    ctypedef test_union testUnion
    cdef union otherUnion:
        int item_one
        float item_two
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
cdef extern from [[[FILENAME]]] nogil:
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
cdef extern from [[[FILENAME]]] nogil:
    ctypedef float newFloat
    newFloat* doStuff(newFloat a, float *b)
""".strip()
)

# Typedef cast.
testing_pairs['typedef_cast'] = (
"""
typedef float (*func_point)(int param1, void* param2);
""".strip(),
"""
cdef extern from [[[FILENAME]]] nogil:
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
cdef extern from [[[FILENAME]]] nogil:
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
cdef extern from [[[FILENAME]]] nogil:
    cdef struct TestingStruct:
        long (*function_name)(TestingStruct* self_reference, long param_2)
""".strip()
)

testing_pairs['simple_external_typedef'] = (
"""
#include <stdint.h>
typedef int8_t Int8;
""".strip(),
"""
cdef extern from "stdint.h" nogil:
    ctypedef signed char int8_t

cdef extern from [[[FILENAME]]] nogil:
    ctypedef int8_t Int8
""".strip()
)

testing_pairs['void_func_pointer_in_struct'] = (
"""
struct SomeStruct {
    void (*void_func)();
    const char *const_pointer;
}
""".strip(),
"""
cdef extern from [[[FILENAME]]] nogil:
    cdef struct SomeStruct:
        void (*void_func)()
        char *const_pointer
""".strip()
)

testing_pairs['function_poiner_as_funtion_param'] = (
"""
int some_function (int *param_a, void (*function_pointer) (int, void *));
""".strip(),
"""
cdef extern from [[[FILENAME]]] nogil:
    int some_function(int *param_a, void (*function_pointer)(int, void*))
""".strip()
)

testing_pairs['complicated_extern_type'] = (
"""
#include <stdio.h>

FILE dummyFunc();
""".strip(),
"""
cdef extern from "stdio.h" nogil:
    cdef struct __sFILE:
        pass
    ctypedef __sFILE FILE

cdef extern from [[[FILENAME]]] nogil:
    FILE dummyFunc()
""".strip()
)

# Test a function pointer to a typedef of a previously unnamed enum.
testing_pairs['function_pointer_to_enum'] = (
"""
typedef enum
{
    RETRY,
    BREAK
} enumName;

typedef enumName (*function)(const float* data, void* other_data);
""".strip(),
"""
cdef extern from [[[FILENAME]]] nogil:
    cdef enum Enum_temp_random_[[RANDOMINT]]:
        RETRY
        BREAK
    ctypedef Enum_temp_random_[[RANDOMINT]] enumName
    ctypedef enumName (*function)(float* data, void* other_data)
""".strip()
)

# Nested structs and unions will be decomposed.
testing_pairs['nested_structs_and_unions'] = (
"""
typedef struct outer_struct {
    int field_1;
    union {
        struct
        {
            float *inner_struct_field_a;
            int inner_struct_field_b;
        } inner_struct;
    } inner_union;
} outerStruct;
""".strip(),
"""
cdef extern from [[[FILENAME]]] nogil:
    cdef struct Struct_temp_random_[[RANDOMINT]]:
        float *inner_struct_field_a
        int inner_struct_field_b
    cdef union Union_temp_random_[[RANDOMINT]]:
        Struct_temp_random_[[RANDOMINT]] inner_struct
    cdef struct outer_struct:
        int field_1
        Union_temp_random_[[RANDOMINT]] inner_union
    ctypedef outer_struct outerStruct
""".strip()
)

testing_pairs['test_correct_include_parsing'] = (
"""
#include <sys/types.h>
typedef off_t file_size_int;
""".strip(),
"""
cdef extern from "sys/types.h" nogil:
    ctypedef long long off_t

cdef extern from [[[FILENAME]]] nogil:
    ctypedef off_t file_size_int
""".strip()
)

# Test some issues with include va_list from stdarg.h
testing_pairs['test_including_va_list'] = (
"""
#include <stdarg.h>

int some_func(va_list param_1, int * param_2);
""".strip(),
"""
cdef extern from "stdarg.h" nogil:
    ctypedef void *va_list

cdef extern from [[[FILENAME]]] nogil:
    int some_func(va_list param_1, int *param_2)
""".strip()
)

# Test a formatting issue
testing_pairs['test_unsigned_formatting_issue'] = (
"""
struct test_struct {
    unsigned int * param_1;
    short int param_2;
}
void test_func(void (*func)(unsigned char param_1, int param_2));
void test_func_2(void (*func)(unsigned int param_1, int param_2));
""".strip(),
"""
cdef extern from [[[FILENAME]]] nogil:
    cdef struct test_struct:
        unsigned int *param_1
        short param_2
    void test_func(void (*func)(unsigned char param_1, int param_2))
    void test_func_2(void (*func)(unsigned int param_1, int param_2))
""".strip()
)
