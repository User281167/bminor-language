import unittest
from parser import Parser
from parser.model import *

from scanner import Lexer
from semantic import Check, SemanticError
from utils import clear_errors, errors_detected, has_error


class TestConstant(unittest.TestCase):
    def setUp(self):
        self.lexer = Lexer()
        self.parser = Parser()
        clear_errors()

    def semantic(self, code):
        tokens = self.lexer.tokenize(code)
        ast = self.parser.parse(tokens)
        return Check.checker(ast)

    def assertError(self, code, expected_error):
        self.semantic(code)
        self.assertTrue(errors_detected())
        self.assertTrue(has_error(expected_error))

    def test_const_integer(self):
        code = "x: constant = 42;"
        env = self.semantic(code)
        decl = env.get("x")
        self.assertFalse(errors_detected())
        self.assertEqual(decl.type.name, "integer")
        self.assertIsInstance(decl.value, Integer)
        self.assertEqual(decl.value.value, 42)

    def test_const_float(self):
        code = "x: constant = 3.14;"
        env = self.semantic(code)
        decl = env.get("x")
        self.assertFalse(errors_detected())
        self.assertEqual(decl.type.name, "float")
        self.assertIsInstance(decl.value, Float)
        self.assertAlmostEqual(decl.value.value, 3.14)

    def test_const_array_int(self):
        code = "x: constant = {1, 2, 3};"
        env = self.semantic(code)
        decl = env.get("x")
        self.assertFalse(errors_detected())
        self.assertIsInstance(decl.type, ArrayType)
        self.assertIsInstance(decl.type.base, SimpleType)
        self.assertEqual(decl.type.base.name, "integer")

    def test_const_from_fun(self):
        code = "f: function integer(); x: constant = f();"
        env = self.semantic(code)
        decl = env.get("x")
        self.assertFalse(errors_detected())
        self.assertIsInstance(decl.type, SimpleType)
        self.assertEqual(decl.type.name, "integer")

    def test_defined_const(self):
        code = "x: constant = 42; y: constant = x;"
        env = self.semantic(code)
        decl = env.get("y")
        self.assertFalse(errors_detected())
        self.assertEqual(decl.type.name, "integer")
        self.assertIsInstance(decl.value, VarLoc)

    def test_const_fun(self):
        code = "fn: function float(); x: constant = fn(); "
        env = self.semantic(code)
        decl = env.get("x")
        self.assertFalse(errors_detected())
        self.assertEqual(decl.type.name, "float")

    def test_error_redefined_const(self):
        code = "x: constant = 42; main: function void() = {x = 42;}"
        self.assertError(code, SemanticError.CONSTANT_ASSIGNMENT)

    def test_error_redefined_array(self):
        code = "x: constant = 42; a: array [3] integer = {1, 2, 3}; main: function void() = {x = a;}"
        self.assertError(code, SemanticError.CONSTANT_ASSIGNMENT)

    def test_error_redefined_func(self):
        code = "x: constant = 'a'; fn: function float(); main: function void() = {x = fn();}"
        self.assertError(code, SemanticError.CONSTANT_ASSIGNMENT)
