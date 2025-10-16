from enum import Enum


class SemanticError(Enum):
    MISMATCHING_TYPES = "Mismatching types"
    MISMATCH_ASSIGNMENT = "Mismatch assignment"
    MISMATCH_DECLARATION = "Mismatch declaration"
    MISMATCH_FUNCTION_CALL = "Mismatch function call"

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


print(SemanticError.MISMATCHING_TYPES)
