import unittest
from parser import Parser
from parser.model import *

from scanner import Lexer
from semantic.checker import Check
from utils import clear_errors, errors_detected


class TestAssignmentBinary(unittest.TestCase):
    def setUp(self):
        self.lexer = Lexer()
        self.parser = Parser()
        clear_errors()

    def semantic(self, code):
        tokens = self.lexer.tokenize(code)
        ast = self.parser.parse(tokens)
        return Check.checker(ast)

    def assertBinary(self, code, expected_type, expected_oper, left_type, right_type):
        env = self.semantic(code)
        decl = env.get("x")
        self.assertIsInstance(decl.value, BinOper)
        self.assertEqual(decl.value.oper, expected_oper)
        self.assertIsInstance(decl.value.left, left_type)
        self.assertIsInstance(decl.value.right, right_type)
        self.assertEqual(decl.value.type.name, expected_type)

    # Integer arithmetic
    def test_integer_add(self):
        self.assertBinary("x: integer = 1 + 2;", "integer", "+", Integer, Integer)

    def test_integer_subtract(self):
        self.assertBinary("x: integer = 5 - 3;", "integer", "-", Integer, Integer)

    def test_integer_multiply(self):
        self.assertBinary("x: integer = 4 * 6;", "integer", "*", Integer, Integer)

    def test_integer_divide(self):
        self.assertBinary("x: integer = 8 / 2;", "integer", "/", Integer, Integer)

    def test_integer_modulo(self):
        self.assertBinary("x: integer = 9 % 4;", "integer", "%", Integer, Integer)

    # Integer comparisons
    def test_integer_less(self):
        self.assertBinary("x: boolean = 1 < 2;", "boolean", "<", Integer, Integer)

    def test_integer_less_equal(self):
        self.assertBinary("x: boolean = 3 <= 3;", "boolean", "<=", Integer, Integer)

    def test_integer_greater(self):
        self.assertBinary("x: boolean = 5 > 2;", "boolean", ">", Integer, Integer)

    def test_integer_greater_equal(self):
        self.assertBinary("x: boolean = 7 >= 7;", "boolean", ">=", Integer, Integer)

    def test_integer_equal(self):
        self.assertBinary("x: boolean = 10 == 10;", "boolean", "==", Integer, Integer)

    def test_integer_not_equal(self):
        self.assertBinary("x: boolean = 11 != 12;", "boolean", "!=", Integer, Integer)

    # Float arithmetic
    def test_float_add(self):
        self.assertBinary("x: float = 1.1 + 2.2;", "float", "+", Float, Float)

    def test_float_subtract(self):
        self.assertBinary("x: float = 5.5 - 3.3;", "float", "-", Float, Float)

    def test_float_multiply(self):
        self.assertBinary("x: float = 2.0 * 4.0;", "float", "*", Float, Float)

    def test_float_divide(self):
        self.assertBinary("x: float = 9.0 / 3.0;", "float", "/", Float, Float)

    def test_float_modulo(self):
        self.assertBinary("x: float = 7.5 % 2.5;", "float", "%", Float, Float)

    def test_complex_integer(self):
        code = "x: integer = 1 + 2 * 3 - 4 / 5;"
        env = self.semantic(code)
        decl = env.get("x")
        self.assertIsNotNone(decl)
        self.assertIsInstance(decl.value, BinOper)

    def test_complex_float(self):
        code = "x: float = 1.1 + 2.2 * 3.3 - 4.4 / 5.5;"
        env = self.semantic(code)
        decl = env.get("x")
        self.assertIsNotNone(decl)
        self.assertIsInstance(decl.value, BinOper)
        self.assertFalse(errors_detected())
