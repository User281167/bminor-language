import sly

from enum import Enum
import logging
import sys

lexer_logger = logging.getLogger('lexer')


class LexerError(Enum):
    # Error types help to follow logs in test

    ILLEGAL_CHARACTER = 'Illegal character'
    UNEXPECTED_TOKEN = 'Unexpected token'
    MALFORMED_INTEGER = 'Malformed integer'
    MALFORMED_FLOAT = 'Malformed real number'
    MALFORMED_STRING = 'Malformed string'
    MALFORMED_CHAR = 'Malformed character literal'
    INVALID_ID = 'Invalid identifier'


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

    @_(r'\n+')
    def ignored_newline(self, t):
        self.lineno += t.value.count('\n')

    @_(r'//.*')
    def ignored_cpp_comment(self, t):
        pass

    @_(r'/\*(?:[^*]|\*(?!/))*\*/')
    def ignore_comment(self, t):
        self.lineno += t.value.count('\n')

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

    @_(r'[a-zA-Z_][a-zA-Z0-9_]*')
    def ID(self, t):
        if (len(t.value) > 255):
            lexer_logger.error(
                f"{LexerError.INVALID_ID.value}: '{t.value}' exceeds max length of 255 at line {t.lineno} column {t.index + 1}")
            t.type = LexerError.INVALID_ID.value

        return t

    @_(r"'(\\[abefnrtv0'\"\\]|\\x[0-9a-fA-F]{2}|[\x20-\x7E])'")
    def CHAR_LITERAL(self, t):
        content = t.value[1:-1]  # remove single quotes

        # Validación adicional para \x
        if len(content) == 4 and content.startswith('\\x'):
            try:
                hex_val = int(content[2:4], 16)
                # allow ASCII printable (32-126)
                if not (32 <= hex_val <= 126):
                    lexer_logger.error(
                        f"{LexerError.MALFORMED_CHAR.value}: hex value out of ASCII range {t.value} at line {t.lineno} column {t.index + 1}"
                    )
                    t.type = LexerError.MALFORMED_CHAR.value
            except ValueError:
                lexer_logger.error(
                    f"{LexerError.MALFORMED_CHAR.value}: invalid hex escape {t.value} at line {t.lineno} column {t.index + 1}"
                )
                t.type = LexerError.MALFORMED_CHAR.value

        if len(content) == 1 and content[0] == '\\':
            lexer_logger.error(
                f"{LexerError.MALFORMED_CHAR.value}: incomplete escape sequence {t.value} at line {t.lineno} column {t.index + 1}"
            )
            t.type = LexerError.MALFORMED_CHAR.value

        return t

    # exclude single \ and single "
    @_(r'"((\\[abefnrtv0\'"\\]|\\x[0-9a-fA-F]{2}|[\x20-\x21\x23-\x5B\x5D-\x7E])*)"')
    def STRING_LITERAL(self, t):
        if (len(t.value) - 2 > 255):  # no count ""
            lexer_logger.error(
                f"{LexerError.MALFORMED_STRING.value}: '{t.value}' exceeds max length of 255 at line {t.lineno} column {t.index + 1}")
            t.type = LexerError.MALFORMED_STRING.value

        return t

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

    @_(r'\d+\.\d*([eE][+-]?\d+)?',     # e.g., 3.14, 2.0e10
       r'\.\d+([eE][+-]?\d+)?',        # e.g., .42, .42e1
       r'\d+[eE][+-]?\d+')             # e.g., 2e10
    def FLOAT_LITERAL(self, t):
        t.value = float(t.value)
        return t

    @_(r'\d+')
    def INTEGER_LITERAL(self, t):
        t.value = int(t.value)
        return t

    def error(self, t):
        char = t.value[0]
        value = t.value

        # get column error position
        line_start = self.text.rfind('\n', 0, t.index) + 1
        column = t.index - line_start + 1

        # determine error type
        if char in [lit.value for lit in LiteralType] or char == '.':
            error_type = LexerError.UNEXPECTED_TOKEN
        elif char == '\'':
            error_type = LexerError.MALFORMED_CHAR
        elif char == '"':
            error_type = LexerError.MALFORMED_STRING
        else:
            error_type = LexerError.ILLEGAL_CHARACTER

        lexer_logger.error(
            f"{error_type.value}: '{char}' at line {t.lineno} column {column}"
        )

        t.type = error_type.value
        t.value = t.value[0]
        self.index += 1
        return t
