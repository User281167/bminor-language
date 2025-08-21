from pip._vendor.tomli._parser import ILLEGAL_BASIC_STR_CHARS
import sly
import logging
from enum import Enum
logger = logging.getLogger('lexer')

# Error class help to follow logs in test


class LexerError(Enum):
    ILLEGAL_CHARACTER = 'Illegal character'
    UNEXPECTED_TOKEN = 'Unexpected token'
    MALFORMED_INTEGER = 'Malformed integer'
    MALFORMED_REAL = 'Malformed real number'
    MALFORMED_STRING = 'Malformed string'
    MALFORMED_CHAR = 'Malformed character literal'


class Lexer(sly.Lexer):
    tokens = {
        ID,
        INTEGER, REAL, STRING, CHAR,
    }

    literals = '+-*/%^=()[]{}:l,;'
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

    @_(r'\d+')
    def INTEGER(self, t):
        try:
            t.value = int(t.value)
        except ValueError:
            logger.error(
                f"{LexerError.MALFORMED_INTEGER}: '{t.value}' at line {self.lineno}")
            t.type = 'ILLEGAL_CHARACTER'
        return t

    def error(self, t):
        print(f"Illegal character '{t.value[0]}' at line {self.lineno}")
        logger.error(
            f"{LexerError.ILLEGAL_CHARACTER}: '{t.value[0]}' at line {self.lineno}")
        self.index += 1
