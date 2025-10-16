import unittest
from parser import Parser
from scanner import Lexer
from parser.model import *
from semantic.checker import Check
from utils import errors_detected


class TestLogicalOperators(unittest.TestCase):
    def setUp(self):
        self.lexer = Lexer()
        self.parser = Parser()

    def semantic(self, code):
        tokens = self.lexer.tokenize(code)
        ast = self.parser.parse(tokens)
        return Check.checker(ast)

    def assertLogical(self, code, expected_oper):
        env = self.semantic(code)
        decl = env.get("x")
        self.assertIsInstance(decl.value, BinOper)
        self.assertEqual(decl.value.oper, expected_oper)
        self.assertIsInstance(decl.value.left, Boolean)
        self.assertIsInstance(decl.value.right, Boolean)
        self.assertEqual(decl.type.name, "boolean")
        self.assertEqual(decl.value.type.name, "boolean")

    def test_boolean_and(self):
        self.assertLogical("x: boolean = true && false;", "LAND")

    def test_boolean_or(self):
        self.assertLogical("x: boolean = true || false;", "LOR")

    def test_boolean_and_true_true(self):
        self.assertLogical("x: boolean = true && true;", "LAND")

    def test_boolean_or_false_false(self):
        self.assertLogical("x: boolean = false || false;", "LOR")

    def test_boolean_or_true_false(self):
        self.assertLogical("x: boolean = true || false;", "LOR")

    def test_complex(self):
        code = "x: boolean = (true || false) && (true || false);"
        env = self.semantic(code)
        decl = env.get("x")
        self.assertIsNotNone(decl)
        self.assertIsInstance(decl.value, BinOper)
        self.assertFalse(errors_detected())

    def test_complex_with_comp(self):
        code = "x: boolean = 3.2 == 3.2 && (true || false) && (2 == 2);"
        env = self.semantic(code)
        decl = env.get("x")
        self.assertIsNotNone(decl)
        self.assertIsInstance(decl.value, BinOper)
        self.assertFalse(errors_detected())
