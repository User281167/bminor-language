import unittest
from parser import Parser
from parser.model import *

from scanner import Lexer
from semantic.checker import Check
from utils import errors_detected
from utils.errors import clear_errors


class TestArrayDeclaration(unittest.TestCase):
    def setUp(self):
        self.lexer = Lexer()
        self.parser = Parser()
        clear_errors()

    def semantic(self, code):
        tokens = self.lexer.tokenize(code)
        ast = self.parser.parse(tokens)
        return Check.checker(ast)

    def assertArray(self, code, expected_type, expected_size):
        env = self.semantic(code)
        self.assertFalse(errors_detected())
        decl = env.get("x")
        self.assertIsNotNone(decl)
        self.assertEqual(decl.type.base.name, expected_type)
        self.assertEqual(decl.type.size.value, expected_size)
        self.assertEqual(len(decl.value), expected_size)

    def test_array_integer_single(self):
        self.assertArray("x: array [1] integer = {1};", "integer", 1)

    def test_array_integer_multiple(self):
        self.assertArray("x: array [3] integer = {1, 2, 3};", "integer", 3)

    def test_array_float(self):
        self.assertArray("x: array [2] float = {3.14, 2.71};", "float", 2)

    def test_array_char(self):
        self.assertArray("x: array [3] char = {'a', 'b', 'c'};", "char", 3)

    def test_array_string(self):
        self.assertArray('x: array [2] string = {"hello", "world"};', "string", 2)

    def test_array_boolean(self):
        self.assertArray("x: array [2] boolean = {true, false};", "boolean", 2)

    def test_array_empty_integer(self):
        self.assertArray("x: array [0] integer = {};", "integer", 0)

    def test_array_empty_string(self):
        self.assertArray("x: array [0] string = {};", "string", 0)

    def test_array_single_char(self):
        self.assertArray("x: array [1] char = {'x'};", "char", 1)

    def test_array_single_boolean(self):
        self.assertArray("x: array [1] boolean = {true};", "boolean", 1)

    def test_array_single_string(self):
        self.assertArray('x: array [1] string = {"ok"};', "string", 1)

    def test_array_single_float(self):
        self.assertArray("x: array [1] float = {0.0};", "float", 1)

    def test_array_size_variable(self):
        code = "a: integer = 3; x: array [a] integer = {1, 2, 3};"
        env = self.semantic(code)
        self.assertFalse(errors_detected())
        decl = env.get("x")
        self.assertIsNotNone(decl)

    def test_array_size_unary(self):
        code = "x: array [+3] integer = {1, 2, 3};"
        env = self.semantic(code)
        self.assertFalse(errors_detected())
        decl = env.get("x")
        self.assertIsNotNone(decl)

    def test_array_size_unary_loc(self):
        code = "a: integer = +3; x: array [a] integer = {1, 2, 3};"
        env = self.semantic(code)
        self.assertFalse(errors_detected())
        decl = env.get("x")
        self.assertIsNotNone(decl)

    def test_array_size_binary(self):
        code = "x: array [1 + 2] integer = {1, 2, 3};"
        env = self.semantic(code)
        self.assertFalse(errors_detected())
        decl = env.get("x")
        self.assertIsNotNone(decl)

    def test_array_size_ternary(self):
        # error en ejecución
        code = "x: array [1 + 2 - 3] integer = {1, 2, 3};"
        env = self.semantic(code)
        self.assertFalse(errors_detected())
        decl = env.get("x")
        self.assertIsNotNone(decl)
