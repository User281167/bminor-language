import unittest
from parser import Parser, ParserError
from scanner import Lexer
from parser.model import *
from utils.errors import errors_detected, clear_errors, has_error


class TestExpressionErrors(unittest.TestCase):
    def setUp(self):
        clear_errors()
        self.lexer = Lexer()
        self.parser = Parser()

    def parse(self, code):
        clear_errors()
        tokens = self.lexer.tokenize(code)
        return self.parser.parse(tokens)

    # ========== SYNTAX ERRORS ==========

    def test_missing_operand(self):
        code = "x: integer = 5 + ;"
        self.parse(code)
        self.assertNotEqual(errors_detected(), 0,
                            "Se esperaba error por operando faltante")
        self.assertTrue(has_error(ParserError.MISSING_STATEMENT))

    def test_missing_operator(self):
        code = "x: integer = 5 3;"
        self.parse(code)
        self.assertNotEqual(errors_detected(), 0,
                            "Se esperaba error por operador faltante")
        self.assertTrue(has_error(ParserError.UNEXPECTED_TOKEN))

    def test_unmatched_parentheses(self):
        code = "x: integer = (5 + 3;"
        self.parse(code)
        self.assertNotEqual(errors_detected(), 0,
                            "Se esperaba error por paréntesis no balanceados")
        # por paréntesis sin cerrar
        self.assertTrue(has_error(ParserError.MISSING_STATEMENT))

    def test_missing_semicolon_in_expression(self):
        code = "x: integer = 5 + 3"
        self.parse(code)
        self.assertNotEqual(errors_detected(), 0,
                            "Se esperaba error por punto y coma faltante")
        self.assertTrue(has_error(ParserError.UNEXPECTED_EOF))

    def test_invalid_float_literal(self):
        code = "f: float = 3.14.5;"
        self.parse(code)
        self.assertNotEqual(errors_detected(), 0,
                            "Se esperaba error por literal float inválido")
        self.assertTrue(has_error(ParserError.UNEXPECTED_TOKEN))

    def test_invalid_scientific_notation(self):
        code = "f: float = 3.14e;"
        self.parse(code)
        self.assertNotEqual(
            errors_detected(), 0, "Se esperaba error por notación científica inválida")
        self.assertTrue(has_error(ParserError.UNEXPECTED_IDENTIFIER))
