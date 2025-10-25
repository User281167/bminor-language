from enum import Enum


class LexerError(Enum):
    ILLEGAL_CHARACTER = "Illegal character"
    UNEXPECTED_TOKEN = "Unexpected token"
    MALFORMED_INTEGER = "Malformed integer"
    MALFORMED_FLOAT = "Malformed real number"
    MALFORMED_STRING = "Malformed string"
    MALFORMED_CHAR = "Malformed character literal"
    INVALID_ID = "Invalid identifier"

    TOO_LONG_STRING = "String literal too long"
