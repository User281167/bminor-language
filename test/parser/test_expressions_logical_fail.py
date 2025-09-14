from errors import errors_detected, clear_errors
import unittest
from parser import Parser
from scanner import Lexer
from model import *
from errors import errors_detected


class TestLogicalExpressionsErrors(unittest.TestCase):
    def setUp(self):
        clear_errors()
        self.lexer = Lexer()
        self.parser = Parser()

    def parse(self, code):
        tokens = self.lexer.tokenize(code)
        return self.parser.parse(tokens)

    # ========== LOGICAL EXPRESSIONS ==========

    def test_or_bad_ope(self):
        code = "x: boolean = true or 1"
        ast = self.parse(code)
        self.assertTrue(errors_detected())

    def test_lor_bad_operands(self):
        code = "x: boolean = ` 1"
        ast = self.parse(code)
        self.assertTrue(errors_detected())

    def test_empty_not(self):
        code = "x: boolean = !;"
        ast = self.parse(code)
        self.assertTrue(errors_detected())

    def test_lor_no_operands(self):
        code = "x: boolean = `;"
        ast = self.parse(code)
        self.assertTrue(errors_detected())

    def test_land_no_operands(self):
        code = "x: boolean = &&;"
        ast = self.parse(code)
        self.assertTrue(errors_detected())

    def test_bad_ope(self):
        code = "x: boolean = true || && false;"
        ast = self.parse(code)
        self.assertTrue(errors_detected())

    def test_bad_grouping(self):
        code = "x: boolean = (true || && false);"
        ast = self.parse(code)
        self.assertTrue(errors_detected())

    def test_bad_ope_type(self):
        code = "x: boolean = true ^^ false;"
        ast = self.parse(code)
        self.assertTrue(errors_detected())

    def test_bad_not_in_end(self):
        code = "x: boolean = a!;"
        ast = self.parse(code)
        self.assertTrue(errors_detected())

    def test_bad_not_in_middle(self):
        code = "x: boolean = a ! b;"
        ast = self.parse(code)
        self.assertTrue(errors_detected())

    def test_no_support_bitwise_and(self):
        code = "x: boolean = a & b;"
        ast = self.parse(code)
        self.assertTrue(errors_detected())

    def test_no_support_bitwise_or(self):
        code = "x: boolean = a | b;"
        ast = self.parse(code)
        self.assertTrue(errors_detected())

    def test_no_support_bitwise_xor(self):
        code = "x: boolean = a ^ b;"
        ast = self.parse(code)
        # debe dar exponentes
        self.assertFalse(errors_detected())

        decl = ast.body[0]
        self.assertIsInstance(decl.value, BinOper)
        self.assertEqual(decl.value.oper, "^")

    def test_no_support_bitwise_not(self):
        code = "x: boolean = ~a;"
        ast = self.parse(code)
        self.assertTrue(errors_detected())
