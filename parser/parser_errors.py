from enum import Enum


class ParserError(Enum):
    SYNTAX_ERROR = "Syntax error"
    INVALID_ASSIGNMENT = "Invalid assignment"
    UNEXPECTED_TOKEN = "Unexpected token"
    UNEXPECTED_IDENTIFIER = "Unexpected identifier"
    UNEXPECTED_EOF = "Unexpected end of file, expected close expression or statement"
    MISSING_EXPRESSION = "Missing expression"
    INVALID_INC_DEC = "Invalid increment/decrement usage"
    UNSUPPORTED_OPERATOR = "Unsupported operator"
    MISSING_STATEMENT = "Missing statement"
    INVALID_NOT = "Invalid not usage"
    MALFORMED_STRING = "Expected string literal"
    MALFORMED_CHAR = "Expected character literal"
    UNEXPECTED_COLON = "Unexpected colon expected identifier or type"
    INVALID_ARRAY_SYNTAX = "Invalid array access syntax"
    INCOMPLETE_FUNCTION_DECLARATION = "Incomplete function declaration"
    INVALID_STATEMENT = "Invalid statement"
