import unittest
from parser import Parser
from scanner import Lexer
from parser.model import *
from semantic.checker import Check
from utils import errors_detected, clear_errors


class TestAssignmentComparisons(unittest.TestCase):
    def setUp(self):
        self.lexer = Lexer()
        self.parser = Parser()
        clear_errors()

    def semantic(self, code):
        tokens = self.lexer.tokenize(code)
        ast = self.parser.parse(tokens)
        return Check.checker(ast)

    def assertComparison(self, code, expected_oper, left_type, right_type):
        env = self.semantic(code)
        self.assertFalse(errors_detected())
        decl = env.get("x")
        self.assertIsInstance(decl.value, BinOper)
        self.assertEqual(decl.value.oper, expected_oper)
        self.assertIsInstance(decl.value.left, left_type)
        self.assertIsInstance(decl.value.right, right_type)
        self.assertEqual(decl.type.name, "boolean")
        self.assertEqual(decl.value.type.name, "boolean")

    # Integer comparisons
    def test_integer_less(self):
        self.assertComparison("x: boolean = 1 < 2;", "<", Integer, Integer)

    def test_integer_less_equal(self):
        self.assertComparison("x: boolean = 3 <= 3;", "<=", Integer, Integer)

    def test_integer_greater(self):
        self.assertComparison("x: boolean = 5 > 2;", ">", Integer, Integer)

    def test_integer_greater_equal(self):
        self.assertComparison("x: boolean = 7 >= 7;", ">=", Integer, Integer)

    def test_integer_equal(self):
        self.assertComparison("x: boolean = 10 == 10;", "==", Integer, Integer)

    def test_integer_not_equal(self):
        self.assertComparison("x: boolean = 11 != 12;", "!=", Integer, Integer)

    # Float comparisons
    def test_float_less(self):
        self.assertComparison("x: boolean = 1.1 < 2.2;", "<", Float, Float)

    def test_float_less_equal(self):
        self.assertComparison("x: boolean = 3.3 <= 3.3;", "<=", Float, Float)

    def test_float_greater(self):
        self.assertComparison("x: boolean = 5.5 > 2.2;", ">", Float, Float)

    def test_float_greater_equal(self):
        self.assertComparison("x: boolean = 7.7 >= 7.7;", ">=", Float, Float)

    def test_float_equal(self):
        self.assertComparison("x: boolean = 10.0 == 10.0;", "==", Float, Float)

    def test_float_not_equal(self):
        self.assertComparison("x: boolean = 11.1 != 12.2;", "!=", Float, Float)

    def test_boolean_equal(self):
        self.assertComparison("x: boolean = true == true;", "==", Boolean, Boolean)

    def test_boolean_not_equal(self):
        self.assertComparison("x: boolean = true != false;", "!=", Boolean, Boolean)
