from errors import errors_detected, clear_errors
import unittest
from parser import Parser
from scanner import Lexer
from model import *


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

    def test_missing_operator(self):
        code = "x: integer = 5 3;"
        self.parse(code)
        self.assertNotEqual(errors_detected(), 0,
                            "Se esperaba error por operador faltante")

    def test_unmatched_parentheses(self):
        code = "x: integer = (5 + 3;"
        self.parse(code)
        self.assertNotEqual(errors_detected(), 0,
                            "Se esperaba error por paréntesis no balanceados")

    def test_invalid_operator_sequence(self):
        code = "x: integer = 5 + + 3;"
        self.parse(code)
        self.assertNotEqual(
            errors_detected(), 0, "Se esperaba error por secuencia de operadores inválida")

    def test_missing_semicolon_in_expression(self):
        code = "x: integer = 5 + 3"
        self.parse(code)
        self.assertNotEqual(errors_detected(), 0,
                            "Se esperaba error por punto y coma faltante")

    def test_invalid_float_literal(self):
        code = "f: float = 3.14.5;"
        self.parse(code)
        self.assertNotEqual(errors_detected(), 0,
                            "Se esperaba error por literal float inválido")

    def test_invalid_scientific_notation(self):
        code = "f: float = 3.14e;"
        self.parse(code)
        self.assertNotEqual(
            errors_detected(), 0, "Se esperaba error por notación científica inválida")

    def test_plus_unary_negation_with_expression(self):
        code = "x: float = pi - +(3 + 2);"
        self.parse(code)

        # invalid syntax for unary negation
        self.assertGreater(errors_detected(), 0)
