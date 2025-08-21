from pip._vendor.tomli._parser import ILLEGAL_BASIC_STR_CHARS
import sly
from enum import Enum
import logging

lexer_logger = logging.getLogger('lexer')


class LexerError(Enum):
    # Error class help to follow logs in test

    ILLEGAL_CHARACTER = 'Illegal character'
    UNEXPECTED_TOKEN = 'Unexpected token'
    MALFORMED_INTEGER = 'Malformed integer'
    MALFORMED_FLOAT = 'Malformed real number'
    MALFORMED_STRING = 'Malformed string'
    MALFORMED_CHAR = 'Malformed character literal'


class TokenType(Enum):
    ID = 'ID'
    INTEGER = 'INTEGER'
    FLOAT = 'FLOAT'
    STRING = 'STRING'
    CHAR = 'CHAR'
    INCREMENT = 'INCREMENT'
    DECREMENT = 'DECREMENT'

    # Keywords
    ARRAY_KEY = 'ARRAY_KEY'
    AUTO_KEY = 'AUTO_KEY'
    BOOLEAN_KEY = 'BOOLEAN_KEY'
    CHAR_KEY = 'CHAR_KEY'
    ELSE_KEY = 'ELSE_KEY'
    FALSE_KEY = 'FALSE_KEY'
    FLOAT_KEY = 'FLOAT_KEY'
    FOR_KEY = 'FOR_KEY'
    FUNCTION_KEY = 'FUNCTION_KEY'
    IF_KEY = 'IF_KEY'
    INTEGER_KEY = 'INTEGER_KEY'
    PRINT_KEY = 'PRINT_KEY'
    RETURN_KEY = 'RETURN_KEY'
    STRING_KEY = 'STRING_KEY'
    TRUE_KEY = 'TRUE_KEY'
    VOID_KEY = 'VOID_KEY'
    WHILE_KEY = 'WHILE_KEY'


class Lexer(sly.Lexer):
    tokens = {
        ID,
        INTEGER,
        FLOAT,
        STRING,
        CHAR,
        INCREMENT,
        DECREMENT,
        # keywords
        ARRAY_KEY,
        AUTO_KEY,
        BOOLEAN_KEY,
        CHAR_KEY,
        ELSE_KEY,
        FALSE_KEY,
        FLOAT_KEY,
        FOR_KEY,
        FUNCTION_KEY,
        IF_KEY,
        INTEGER_KEY,
        PRINT_KEY,
        RETURN_KEY,
        STRING_KEY,
        TRUE_KEY,
        VOID_KEY,
        WHILE_KEY
    }

    literals = '+-*/%^=()[]{}:,;'
    ignore = ' \t\r'

    ID = r'[_a-zA-Z]\w*'
    INCREMENT = r'\+\+'
    DECREMENT = r'--'

    ID['array'] = ARRAY_KEY
    ID['auto'] = AUTO_KEY
    ID['boolean'] = BOOLEAN_KEY
    ID['char'] = CHAR_KEY
    ID['else'] = ELSE_KEY
    ID['false'] = FALSE_KEY
    ID['float'] = FLOAT_KEY
    ID['for'] = FOR_KEY
    ID['function'] = FUNCTION_KEY
    ID['if'] = IF_KEY
    ID['integer'] = INTEGER_KEY
    ID['print'] = PRINT_KEY
    ID['return'] = RETURN_KEY
    ID['string'] = STRING_KEY
    ID['true'] = TRUE_KEY
    ID['void'] = VOID_KEY
    ID['while'] = WHILE_KEY

    @_(r'\n+')
    def ignored_newline(self, t):
        self.lineno += t.value.count('\n')

    @_(r'//.*')
    def ignored_cpp_comment(self, t):
        self.lineno += 1

    @_(r'/\*(.|\n)*\*/')
    def ignore_comment(self, t):
        self.lineno = t.value.count('\n')

    @_(r'\d+\.\d*([eE][+-]?\d+)?',     # e.g., 3.14, 2.0e10
       r'\.\d+([eE][+-]?\d+)?',        # e.g., .42, .42e1
       r'\d+[eE][+-]?\d+')             # e.g., 2e10
    def FLOAT(self, t):
        try:
            t.value = float(t.value)
        except ValueError:
            msg = f"{LexerError.MALFORMED_FLOAT.value}: '{t.value}' at line {self.lineno}"
            print(msg)
            lexer_logger.error(msg)
            t.type = LexerError.MALFORMED_FLOAT
        return t

    @_(r'\d+')
    def INTEGER(self, t):
        try:
            t.value = int(t.value)
        except ValueError:
            msg = f"{LexerError.MALFORMED_INTEGER.value}: '{t.value}' at line {self.lineno}"
            print(msg)
            lexer_logger.error(msg)
            t.type = LexerError.MALFORMED_INTEGER
        return t

    def error(self, t):
        msg = f"{LexerError.ILLEGAL_CHARACTER.value}: '{t.value[0]}' at line {self.lineno}"
        print(msg)
        lexer_logger.error(msg)
        self.index += 1
