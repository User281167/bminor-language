from enum import Enum


class SemanticError(Enum):
    UNKNOWN = "Unknown error"

    MISMATCH_ASSIGNMENT = "Mismatch assignment"
    MISMATCH_DECLARATION = "Mismatch declaration"

    CONSTANT_ASSIGNMENT = "Cannot assign to constant"

    UNDECLARED_VARIABLE = "Undeclared variable"
    UNDECLARED_ARRAY = "Undeclared array"

    VOID_VARIABLE = "Void variable"
    VOID_ARRAY = "Void array"

    MISMATCH_ARRAY_ASSIGNMENT = "Mismatch array assignment"
    ARRAY_SIZE_MUST_BE_INTEGER = "Array size must be integer"
    ARRAY_SIZE_MUST_BE_POSITIVE = "Array size must be positive"
    ARRAY_SIZE_MISMATCH = "Array size mismatch"
    ARRAY_INDEX_MUST_BE_INTEGER = "Array index must be integer"
    ARRAY_EXPECTED = "Array expected"
    MULTI_DIMENSIONAL_ARRAYS = "Multi-dimensional arrays are not supported"
    ARRAY_NOT_SUPPORTED_SIZE = (
        "Array not supported size in function parameters or return type"
    )

    INDEX_MUST_BE_POSITIVE = "Index must be integer positive"
    INDEX_OUT_OF_BOUNDS = "Index out of bounds"

    INVALID_UNARY_OP = "Invalid unary operator"
    INVALID_BINARY_OP = "Invalid binary operator"

    UNARY_OP_TYPE = "Unary operator type"
    BINARY_OP_TYPE = "Binary operator type"
    BINARY_ARRAY_OP = "Binary array operator"

    INVALID_INCREMENT = "Invalid increment"
    INVALID_DECREMENT = "Invalid decrement"

    REDEFINE_VARIABLE_TYPE = "Redeclare variable type"
    REDEFINE_VARIABLE = "Redeclare variable"

    REDEFINE_FUNCTION_TYPE = "Redeclare function type"
    REDEFINE_FUNCTION = "Redeclare function"

    REDEFINE_PARAMETER_TYPE = "Redeclare parameter type"
    REDEFINE_PARAMETER = "Redeclare parameter"

    IF_CONDITION_MUST_BE_BOOLEAN = "If condition must be boolean"

    LOOP_CONDITION_MUST_BE_BOOLEAN = "Loop condition must be boolean"
    BREAK_OUT_OF_LOOP = "Break out of loop"
    CONTINUE_OUT_OF_LOOP = "Continue out of loop"

    FUNCTION_USED_AS_VALUE = "Function used as value"
    UNDEFINED_FUNCTION = "Undefined function"
    IS_NOT_FUNCTION = "Is not function"
    INVALID_FUNCTION_DECLARATION = "Invalid function declaration"

    WRONG_NUMBER_OF_ARGUMENTS = "Wrong number of arguments"
    MISMATCH_ARGUMENT_TYPE = "Mismatch argument type"

    VOID_PARAMETER = "Void parameter"

    RETURN_TYPE_MISMATCH = "Return type mismatch"
    RETURN_OUT_OF_FUNCTION = "Return out of function"
    RETURN_IN_VOID_FUNCTION = "Return in void function"

    PRINT_VOID_EXPRESSION = "Print void expression"
    PRINT_ARRAY_NOT_ALLOWED = "Cannot print array"

    DIVIDE_BY_ZERO = "Divide by zero"
