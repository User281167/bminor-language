import unittest
from parser import Parser, ParserError
from scanner import Lexer
from parser.model import *
from utils.errors import errors_detected, clear_errors, has_error


class TestAssignmentFailingCases(unittest.TestCase):
    def setUp(self):
        self.lexer = Lexer()
        self.parser = Parser()

    def parse(self, code):
        clear_errors()
        tokens = self.lexer.tokenize(code)
        return self.parser.parse(tokens)

    def test_missing_colon_syntax_error(self):
        # Código inválido: falta ':' en la declaración
        code = "x integer = 5;"
        self.parse(code)
        self.assertNotEqual(
            errors_detected(),
            0,
            "Se esperaba al menos un error por sintaxis (falta ':')",
        )
        self.assertTrue(has_error(ParserError.UNEXPECTED_TOKEN))

    def test_unterminated_string_literal(self):
        # Código inválido: cadena sin terminar
        code = 's: string = "hello;'
        self.parse(code)
        self.assertNotEqual(
            errors_detected(), 0, "Se esperaba error por cadena sin terminar"
        )
        self.assertTrue(has_error(ParserError.MALFORMED_STRING))

    def test_invalid_char_literal(self):
        # Código inválido: literal de char con más de un carácter
        code = "c: char = 'ab';"
        self.parse(code)
        self.assertNotEqual(
            errors_detected(), 0, "Se esperaba error por literal char inválido"
        )
        self.assertTrue(has_error(ParserError.MALFORMED_CHAR))

    def test_invalid_float_literal(self):
        # Código inválido: literal de float con más de un punto
        code = "f: float = 1.2.3;"
        self.parse(code)
        self.assertNotEqual(
            errors_detected(), 0, "Se esperaba error por literal float inválido"
        )
        self.assertTrue(has_error(ParserError.UNEXPECTED_TOKEN))
