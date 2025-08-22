import sly

from enum import Enum
import logging
import sys

lexer_logger = logging.getLogger('lexer')


def print_error(msg):
    print(msg, file=sys.stderr)
    lexer_logger.error(msg)


class LexerError(Enum):
    # Error types help to follow logs in test

    ILLEGAL_CHARACTER = 'Illegal character'
    UNEXPECTED_TOKEN = 'Unexpected token'
    MALFORMED_INTEGER = 'Malformed integer'
    MALFORMED_FLOAT = 'Malformed real number'
    MALFORMED_STRING = 'Malformed string'
    MALFORMED_CHAR = 'Malformed character literal'


class TokenType(Enum):
    ID = 'ID'
    INTEGER_LITERAL = 'INTEGER_LITERAL'
    FLOAT_LITERAL = 'FLOAT_LITERAL'
    STRING_LITERAL = 'STRING_LITERAL'
    CHAR_LITERAL = 'CHAR_LITERAL'

    # Keywords
    ARRAY = 'ARRAY'
    AUTO = 'AUTO'
    BOOLEAN = 'BOOLEAN'
    CHAR = 'CHAR'
    ELSE = 'ELSE'
    FALSE = 'FALSE'
    FLOAT = 'FLOAT'
    FOR = 'FOR'
    FUNCTION = 'FUNCTION'
    IF = 'IF'
    INTEGER = 'INTEGER'
    PRINT = 'PRINT'
    RETURN = 'RETURN'
    STRING = 'STRING'
    TRUE = 'TRUE'
    VOID = 'VOID'
    WHILE = 'WHILE'


class OperatorType(Enum):
    LT = 'LT'
    LE = 'LE'
    GT = 'GT'
    GE = 'GE'
    EQ = 'EQ'
    NE = 'NE'
    LAND = 'LAND'
    LOR = 'LOR'
    INCREMENT = 'INCREMENT'
    DECREMENT = 'DECREMENT'


class LiteralType(Enum):
    PLUS = '+'
    MINUS = '-'
    STAR = '*'
    SLASH = '/'
    PERCENT = '%'
    CARET = '^'
    EQUAL = '='
    LPAREN = '('
    RPAREN = ')'
    LBRACKET = '['
    RBRACKET = ']'
    LBRACE = '{'
    RBRACE = '}'
    COLON = ':'
    COMMA = ','
    SEMICOLON = ';'
    BANG = '!'


class Lexer(sly.Lexer):
    # Dynamically collect
    tokens = {token.name for token in TokenType}
    tokens |= {op.name for op in OperatorType}

    literals = {lit.value for lit in LiteralType}
    ignore = ' \t\r'

    ID = r'[a-zA-Z_][a-zA-Z0-9_]*'

    # Keywords
    ID['array'] = ARRAY
    ID['auto'] = AUTO
    ID['boolean'] = BOOLEAN
    ID['char'] = CHAR
    ID['else'] = ELSE
    ID['false'] = FALSE
    ID['float'] = FLOAT
    ID['for'] = FOR
    ID['function'] = FUNCTION
    ID['if'] = IF
    ID['integer'] = INTEGER
    ID['print'] = PRINT
    ID['return'] = RETURN
    ID['string'] = STRING
    ID['true'] = TRUE
    ID['void'] = VOID
    ID['while'] = WHILE

    # Operators
    INCREMENT = r'\+\+'
    DECREMENT = r'--'
    LE = r'<='
    LT = r'<'
    GE = r'>='
    GT = r'>'
    EQ = r'=='
    NE = r'!='
    LAND = r'&&'
    LOR = r'\`'

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
    def FLOAT_LITERAL(self, t):
        try:
            t.value = float(t.value)
        except ValueError:
            print_error(
                f"{LexerError.MALFORMED_FLOAT.value}: '{t.value}' at line {self.lineno}")
            t.type = LexerError.MALFORMED_FLOAT
        return t

    @_(r'\d+')
    def INTEGER_LITERAL(self, t):
        try:
            t.value = int(t.value)
        except ValueError:
            print_error(
                f"{LexerError.MALFORMED_INTEGER.value}: '{t.value}' at line {self.lineno}"
            )
            t.type = LexerError.MALFORMED_INTEGER
        return t

    def error(self, t):
        print_error(
            f"{LexerError.ILLEGAL_CHARACTER.value}: '{t.value[0]}' at line {self.lineno}"
        )
        self.index += 1
        # print(t.type, t.value)
        # t.type = LexerError.ILLEGAL_CHARACTER
        # return t
