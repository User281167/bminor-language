"""
Lexer para lenguaje b-minor usando SLY (Simple Lexer in Python).

Este archivo define:
- Tipos de tokens y operadores mediante Enum.
- Reglas léxicas para identificar literales, identificadores, palabras clave y operadores.
- Validaciones específicas para caracteres, cadenas, enteros y flotantes.
- Manejo de errores léxicos con mensajes detallados y registro mediante logging.

Convenciones:
- Los identificadores no deben exceder los 255 caracteres.
- Las cadenas y caracteres se validan según rangos ASCII imprimibles.
- Se utiliza un logger interno para registrar errores con formato estandarizado.
"""


import sly
import logging

from .lexer_errors import LexerError
from .lexer_type import TokenType, OperatorType, LiteralType

MAX_ID_LENGTH = 255


class Lexer(sly.Lexer):
    tokens = {token.name for token in TokenType}
    tokens |= {token.name for token in OperatorType}

    literals = {lit.value for lit in LiteralType}
    ignore = ' \t\r'

    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger('lexer')

    def log_error(self, error_type, token, message=None):
        value = token.value[0:5]

        if '\n' in value:
            value = value[:value.index('\n')]

        column = token.index - self.text.rfind('\n', 0, token.index) + 1
        msg = f"{error_type.value}: {value} {message or ''} at line {token.lineno} column {column}"
        self.logger.error(msg)
        token.type = error_type.value
        token.value = token.value[0]
        self.index += 1
        return token

    @_(r'\n+')
    def ignored_newline(self, t):
        self.lineno += t.value.count('\n')

    @_(r'//.*')
    def ignored_cpp_comment(self, t):
        pass

    @_(r'/\*(?:[^*]|\*(?!/))*\*/')
    def ignore_comment(self, t):
        self.lineno += t.value.count('\n')

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
    ID['do'] = DO

    @_(r'[a-zA-Z_][a-zA-Z0-9_]*')
    def ID(self, t):
        if len(t.value) > MAX_ID_LENGTH:
            return self.log_error(LexerError.INVALID_ID, t, f"exceeds max length of {MAX_ID_LENGTH}")
        return t

    @_(r"'(\\[abefnrtv0'\"\\]|\\x[0-9a-fA-F]{2}|[\x20-\x7E])'")
    def CHAR_LITERAL(self, t):
        content = t.value[1:-1]

        # validación extra para caracteres especiales, formato de escape o hexadecimal
        if len(content) == 4 and content.startswith('\\x'):
            try:
                hex_val = int(content[2:], 16)

                if not (32 <= hex_val <= 126):
                    return self.log_error(LexerError.MALFORMED_CHAR, t, "hex value out of ASCII range")
            except ValueError:
                return self.log_error(LexerError.MALFORMED_CHAR, t, "invalid hex value")
        elif len(content) == 1 and content[0] == '\\':
            return self.log_error(LexerError.MALFORMED_CHAR, t, "incomplete escape sequence")

        return t

    @_(r'"((\\[abefnrtv0\'"\\]|\\x[0-9a-fA-F]{2}|[\x20-\x21\x23-\x5B\x5D-\x7E])*)"')
    def STRING_LITERAL(self, t):
        if len(t.value) - 2 > MAX_ID_LENGTH:
            return self.log_error(LexerError.MALFORMED_STRING, t, f"exceeds max length of {MAX_ID_LENGTH}")
        return t

    INC = r'\+\+'
    DEC = r'--'
    LE = r'<='
    LT = r'<'
    GE = r'>='
    GT = r'>'
    EQ = r'=='
    NE = r'!='
    LAND = r'&&'
    LOR = r'\|\|'

    @_(r'\d+\.\d+([eE][+-]?\d+)?',     # 3.14, 2.71e10
        r'\.\d+([eE][+-]?\d+)?',       # .42, .42e1
        r'\d+[eE][+-]?\d+')            # 2e10
    def FLOAT_LITERAL(self, t):
        t.value = float(t.value)
        return t

    @_(r'\d+')
    def INTEGER_LITERAL(self, t):
        t.value = int(t.value)
        return t

    def error(self, t):
        char = t.value[0]

        if char in [lit.value for lit in LiteralType] or char == '.':
            error_type = LexerError.UNEXPECTED_TOKEN
        elif char == '\'':
            error_type = LexerError.MALFORMED_CHAR
        elif char == '\\':
            error_type = LexerError.MALFORMED_CHAR
        elif char == '"':
            error_type = LexerError.MALFORMED_STRING
        else:
            error_type = LexerError.ILLEGAL_CHARACTER

        return self.log_error(error_type, t)
