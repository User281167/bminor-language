from errors import errors_detected, clear_errors
import unittest
from parser import Parser
from scanner import Lexer
from model import *
from errors import errors_detected


class TestArrayFailingCases(unittest.TestCase):
    def setUp(self):
        self.lexer = Lexer()
        self.parser = Parser()
        clear_errors

    def parse(self, code):
        clear_errors()
        tokens = self.lexer.tokenize(code)
        return self.parser.parse(tokens)

#     # ========== SYNTAX ERRORS ==========

    def test_missing_array_keyword(self):
        code = "a: [5] integer = {1, 2, 3};"
        self.parse(code)
        self.assertNotEqual(
            errors_detected(), 0, "Se esperaba error por falta de palabra clave 'array'")

    def test_missing_square_brackets(self):
        code = "a: array 5 integer = {1, 2, 3};"
        self.parse(code)
        self.assertNotEqual(errors_detected(), 0,
                            "Se esperaba error por falta de corchetes")

    def test_missing_size_in_brackets(self):
        code = "a: array [] integer = {1, 2, 3};"
        self.parse(code)
        self.assertNotEqual(
            errors_detected(), 0, "Se esperaba error por falta de tamaño en corchetes")

    def test_missing_equals_sign(self):
        code = "a: array [5] integer {1, 2, 3};"
        self.parse(code)
        self.assertNotEqual(errors_detected(), 0,
                            "Se esperaba error por falta de signo '='")

    def test_missing_curly_braces(self):
        code = "a: array [5] integer = 1, 2, 3;"
        self.parse(code)
        self.assertNotEqual(errors_detected(), 0,
                            "Se esperaba error por falta de llaves")

    def test_missing_semicolon(self):
        code = "a: array [5] integer = {1, 2, 3}"
        self.parse(code)
        self.assertNotEqual(errors_detected(), 0,
                            "Se esperaba error por falta de punto y coma")

    def test_array_with_missing_comma_separator(self):
        code = "a: array [3] integer = {1 2, 3};"
        self.parse(code)
        self.assertNotEqual(errors_detected(), 0,
                            "Se esperaba error por separador de coma faltante")

    def test_array_with_trailing_comma(self):
        code = "a: array [2] integer = {1, 2,};"
        self.parse(code)
        self.assertNotEqual(errors_detected(), 0,
                            "Se esperaba error por coma final")

    def test_array_with_extra_comma(self):
        code = "a: array [2] integer = {1, , 2};"
        self.parse(code)
        self.assertNotEqual(errors_detected(), 0,
                            "Se esperaba error por coma extra")
