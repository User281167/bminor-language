import unittest
from parser import Parser
from scanner import Lexer
from parser.model import *
from semantic.checker import Check


class TestAssignmentUnary(unittest.TestCase):
    def setUp(self):
        self.lexer = Lexer()
        self.parser = Parser()

    def semantic(self, code):
        tokens = self.lexer.tokenize(code)
        ast = self.parser.parse(tokens)
        return Check.checker(ast)

    def assertUnary(
        self, code, expected_type, expected_oper, expected_value_type, expected_value
    ):
        env = self.semantic(code)
        decl = env.get("x")
        self.assertIsInstance(decl.value, UnaryOper)
        self.assertEqual(decl.value.oper, expected_oper)
        self.assertIsInstance(decl.value.expr, expected_value_type)
        self.assertEqual(decl.value.expr.value, expected_value)
        self.assertEqual(decl.value.type.name, expected_type)

    def test_unary_plus_integer(self):
        self.assertUnary("x: integer = +42;", "integer", "+", Integer, 42)

    def test_unary_minus_integer(self):
        self.assertUnary("x: integer = -7;", "integer", "-", Integer, 7)

    def test_unary_plus_float(self):
        self.assertUnary("x: float = +3.14;", "float", "+", Float, 3.14)

    def test_unary_minus_float(self):
        self.assertUnary("x: float = -2.5;", "float", "-", Float, 2.5)

    def test_unary_not_true(self):
        self.assertUnary("x: boolean = !true;", "boolean", "!", Boolean, True)

    def test_unary_not_false(self):
        self.assertUnary("x: boolean = !false;", "boolean", "!", Boolean, False)

    def test_nested_unary_integer(self):
        env = self.semantic("x: integer = -(-42);")
        decl = env.get("x")
        self.assertIsInstance(decl.value, UnaryOper)
        self.assertEqual(decl.value.oper, "-")
        self.assertIsInstance(decl.value.expr, UnaryOper)
        self.assertEqual(decl.value.expr.oper, "-")
        self.assertIsInstance(decl.value.expr.expr, Integer)
        self.assertEqual(decl.value.expr.expr.value, 42)

    def test_nested_unary_float(self):
        env = self.semantic("x: float = +(-3.5);")
        decl = env.get("x")
        self.assertIsInstance(decl.value, UnaryOper)
        self.assertEqual(decl.value.oper, "+")
        self.assertIsInstance(decl.value.expr, UnaryOper)
        self.assertEqual(decl.value.expr.oper, "-")
        self.assertIsInstance(decl.value.expr.expr, Float)
        self.assertEqual(decl.value.expr.expr.value, 3.5)

    def test_unary_zero_integer(self):
        env = self.semantic("x: integer = +0;")
        decl = env.get("x")
        self.assertIsInstance(decl.value, UnaryOper)
        self.assertEqual(decl.value.oper, "+")
        self.assertIsInstance(decl.value.expr, Integer)
        self.assertEqual(decl.value.expr.value, 0)

        # self.assertUnary("x: integer = -0;", "integer", "-", Integer, 0)

    def test_unary_zero_float(self):
        self.assertUnary("x: float = +0.0;", "float", "+", Float, 0.0)
