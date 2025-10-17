import unittest
from parser import Parser
from parser.model import *

from scanner import Lexer
from semantic.checker import Check, SemanticError
from utils import clear_errors, error, errors_detected, has_error


class TestFunctionDeclarations(unittest.TestCase):
    def setUp(self):
        self.lexer = Lexer()
        self.parser = Parser()
        clear_errors()

    def semantic(self, code):
        tokens = self.lexer.tokenize(code)
        ast = self.parser.parse(tokens)
        return Check.checker(ast)

    def test_main_function_void(self):
        code = "main: function void();"
        env = self.semantic(code)
        self.assertIn("main", env)
        func = env.get("main")
        self.assertEqual(func.name, "main")
        self.assertEqual(func.return_type.name, "void")
        self.assertEqual(len(func.params), 0)
        self.assertFalse(errors_detected())
        self.assertEqual(func.scope, "global")

    def test_function_with_integer_param(self):
        code = "neg: function void(x: integer);"
        env = self.semantic(code)
        func = env.get("neg")
        self.assertEqual(func.name, "neg")
        self.assertEqual(len(func.params), 1)
        param = func.params[0]
        self.assertEqual(param.name, "x")
        self.assertEqual(param.type.name, "integer")
        self.assertIn("x", func.env)
        self.assertFalse(errors_detected())

    def test_function_with_two_params(self):
        code = "sum: function void(x: integer, y: float);"
        env = self.semantic(code)
        self.assertIn("sum", env)
        func = env.get("sum")
        self.assertEqual(func.name, "sum")
        self.assertEqual(func.return_type.name, "void")
        self.assertEqual(len(func.params), 2)
        self.assertEqual(func.params[0].name, "x")
        self.assertEqual(func.params[0].type.name, "integer")
        self.assertEqual(func.params[1].name, "y")
        self.assertEqual(func.params[1].type.name, "float")
        self.assertFalse(errors_detected())

    def test_function_with_multiple_params(self):
        code = "sum: function void(a: integer, b: float);"
        env = self.semantic(code)
        func = env.get("sum")

        self.assertEqual(func.name, "sum")
        self.assertEqual(len(func.params), 2)

        self.assertEqual(func.params[0].name, "a")
        self.assertEqual(func.params[0].type.name, "integer")

        self.assertEqual(func.params[1].name, "b")
        self.assertEqual(func.params[1].type.name, "float")
        self.assertFalse(errors_detected())

        self.assertIn("a", func.env)
        self.assertIn("b", func.env)
        self.assertFalse(errors_detected())

    def test_function_with_char_and_string(self):
        code = "display: function void(c: char, s: string);"
        env = self.semantic(code)
        func = env.get("display")

        self.assertEqual(func.name, "display")

        self.assertEqual(func.params[0].type.name, "char")
        self.assertEqual(func.params[1].type.name, "string")

        self.assertIn("c", func.env)
        self.assertIn("s", func.env)
        self.assertFalse(errors_detected())

    # def test_function_with_array_param(self):
    #     code = "sumArray: function void(arr: array [] integer);"
    #     env = self.semantic(code)
    #     func = env.get("sumArray")
    #     param = func.params[0]

    #     self.assertEqual(param.name, "arr")
    #     self.assertEqual(param.type.name, "array")
    #     self.assertEqual(param.type.subtype.name, "integer")
    #     self.assertEqual(param.scope, "function sumArray")
    #     self.assertIn("arr", func.env)
    #     self.assertFalse(errors_detected())
