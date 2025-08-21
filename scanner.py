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


class Lexer(sly.Lexer):
    tokens = {
        TokenType.ID.value,
        TokenType.INTEGER.value,
        TokenType.FLOAT.value,
        TokenType.STRING.value,
        TokenType.CHAR.value
    }

    literals = '+-*/%^=()[]{}:,;'
    ignore = ' \t\r'

    ID = r'[_a-zA-Z]\w*'

    @_(r'\n+')
    def ignored_newline(self, t):
        self.lineno += t.value.count('\n')

    @_(r'//.*')
    def ignored_cpp_comment(self, t):
        self.lineno += 1

    @_(r'/\*(.|\n)*\*/')
    def ignore_comment(self, t):
        self.lineno = t.value.count('\n')

    @_(r'\d+\.\d*([eE][+-]?\d+)?'     # e.g., 3.14, 2.0e10
       r'|\.\d+([eE][+-]?\d+)?'       # e.g., .42, .42e1
       r'|\d+[eE][+-]?\d+')           # e.g., 2e10
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
