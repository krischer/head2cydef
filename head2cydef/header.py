from clang.cindex import TypeKind

TAB = 4 * ' '

# Map the clang.cindex.TypeKinds to how it would be written in Code. Not all
# types are exposed yet.
# Most descriptive comments are from the clang documentation:
# http://fossies.org/dox/clang-3.0/Type_8h_source.html
TYPE_KIND_MAP = {
    # 'TypeKind.INVALID':
    # 'TypeKind.UNEXPOSED':

    TypeKind.VOID: 'void',

    # This is bool and/or _Bool.
    #TypeKind.BOOL

    # This is 'char' for targets where char is unsigned.
    TypeKind.CHAR_U: 'unsigned char',

    # This is explicitly qualified unsigned char.
    # XXX: What is the difference betwenn this and the previous one?
    TypeKind.UCHAR: 'unsigned char',

    # This is 'char16_t' for C++.
    # TypeKind.CHAR16: ,

    # This is 'char32_t' for C++.
    # TypeKind.CHAR32: ,

    TypeKind.USHORT: 'unsigned short',
    TypeKind.UINT: 'unsigned int',
    TypeKind.ULONG: 'unsigned long',
    TypeKind.ULONGLONG: 'unsigned long long',

    #  __uint128_t
    # TypeKind.UINT128': ,

    # This is 'char' for targets where char is signed.
    TypeKind.CHAR_S: 'char',

    # This is explicitly qualified signed char.
    # XXX: Again not really sure what the difference between this one and the
    # previous one is.
    TypeKind.SCHAR: 'signed char',

    # This is 'wchar_t' for C++.
    # TypeKind.WCHAR: ,

    TypeKind.SHORT: 'short',
    TypeKind.INT: 'int',
    TypeKind.LONG: 'long',
    TypeKind.LONGLONG: 'long long',

    # __int128_t
    # TypeKind.INT128: ,
    TypeKind.FLOAT: 'float',
    TypeKind.DOUBLE: 'double',
    TypeKind.LONGDOUBLE: 'long double',

    # This is the type of C++0x 'nullptr'.
    # TypeKind.NULLPTR: ,

    # TypeKind.OVERLOAD: ,
    # TypeKind.DEPENDENT: ,
    # TypeKind.OBJCID: ,
    # TypeKind.OBJCCLASS: ,
    # TypeKind.OBJCSEL: ,

    # TypeKind.COMPLEX: ,
    # TypeKind.POINTER: ,
    # TypeKind.BLOCKPOINTER: ,
    # TypeKind.LVALUEREFERENCE: ,
    # TypeKind.RVALUEREFERENCE: ,
    # TypeKind.RECORD: ,
    # TypeKind.ENUM: ,
    # TypeKind.TYPEDEF: ,
    # TypeKind.OBJCINTERFACE: ,
    # TypeKind.OBJCOBJECTPOINTER: ,
    # TypeKind.FUNCTIONNOPROTO: ,
    # TypeKind.FUNCTIONPROTO: ,
    # TypeKind.CONSTANTARRAY: ,
}
