from enum import Enum


class SemanticError(Enum):
    MISMATCHING_TYPES = "Mismatching types"
    MISMATCH_ASSIGNMENT = "Mismatch assignment"
    MISMATCH_DECLARATION = "Mismatch declaration"
    MISMATCH_FUNCTION_CALL = "Mismatch function call"

    VOID_VARIABLE = "Void variable"
    VOID_ARRAY = "Void array"

    MISMATCH_ARRAY_ASSIGNMENT = "Mismatch array assignment"
    ARRAY_SIZE_MUST_BE_INTEGER = "Array size must be integer"
    ARRAY_SIZE_MUST_BE_POSITIVE = "Array size must be positive"
    ARRAY_SIZE_MISMATCH = "Array size mismatch"

    INVALID_UNARY_OP = "Invalid unary operator"
    INVALID_BINARY_OP = "Invalid binary operator"

    UNARY_OP_TYPE = "Unary operator type"
    BINARY_OP_TYPE = "Binary operator type"

    UNKNOWN = "Unknown error"

    INMUTABLE_ASSIGNMENT = "Inmutable assignment"
    UNDECLARED_VARIABLE = "Undeclared variable"
    UNDECLARED_FUNCTION = "Undeclared function"
    UNDECLARED_TYPE = "Undeclared type"
    UNDECLARED_ARRAY = "Undeclared array"
    UNDECLARED_ARRAY_TYPE = "Undeclared array type"

    REDEFINE_VARIABLE_TYPE = "Redeclare variable type"
    REDEFINE_VARIABLE = "Redeclare variable"

    REDEFINE_FUNCTION_TYPE = "Redeclare function type"
    REDEFINE_FUNCTION = "Redeclare function"

    REDEFINE_PARAMETER_TYPE = "Redeclare parameter type"
    REDEFINE_PARAMETER = "Redeclare parameter"

    MULTI_DIMENSIONAL_ARRAYS = "Multi-dimensional arrays are not supported"

    VOID_PARAMETER = "Void parameter"
