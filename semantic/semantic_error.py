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

    INDEX_MUST_BE_INTEGER = "Index must be integer"
    INDEX_MUST_BE_POSITIVE = "Index must be positive"
    INDEX_OUT_OF_BOUNDS = "Index out of bounds"

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

    ARRAY_EXPECTED = "Array expected"

    MULTI_DIMENSIONAL_ARRAYS = "Multi-dimensional arrays are not supported"

    VOID_PARAMETER = "Void parameter"

    ARRAY_INDEX_MUST_BE_INTEGER = "Array index must be integer"

    ARRAY_NOT_SUPPORTED_SIZE = (
        "Array not supported size in function parameters or return type"
    )

    IS_NOT_FUNCTION = "Is not function"
    UNDEFINED_FUNCTION = "Undefined function"
    FUNCTION_CALL_ARGUMENT_MISMATCH = "Function call argument mismatch"
    WRONG_NUMBER_OF_ARGUMENTS = "Wrong number of arguments"
    MISMATCH_ARGUMENT_TYPE = "Mismatch argument type"

    RETURN_TYPE_MISMATCH = "Return type mismatch"
    RETURN_OUT_OF_FUNCTION = "Return out of function"
    RETURN_TYPE_NOT_SUPPORTED = "Return type not supported"
    RETURN_IN_VOID_FUNCTION = "Return in void function"

    BREAK_OUT_OF_LOOP = "Break out of loop"
    CONTINUE_OUT_OF_LOOP = "Continue out of loop"

    PRINT_VOID_EXPRESSION = "Print void expression"
    PRINT_ARRAY_NOT_ALLOWED = "Cannot print array"

    IF_CONDITION_MUST_BE_BOOLEAN = "If condition must be boolean"

    BINARY_ARRAY_OP = "Binary array operator"

    LOOP_CONDITION_MUST_BE_BOOLEAN = "Loop condition must be boolean"

    INVALID_INCREMENT = "Invalid increment"
    INVALID_DECREMENT = "Invalid decrement"
