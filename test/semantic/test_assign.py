import unittest
from parser import Parser
from parser.model import *

from scanner import Lexer
from semantic.checker import Check


class TestAssignment(unittest.TestCase):
    def setUp(self):
        self.lexer = Lexer()
        self.parser = Parser()

    def semantic(self, code):
        tokens = self.lexer.tokenize(code)
        ast = self.parser.parse(tokens)
        return Check.checker(ast)

    def test_assign_integer(self):
        code = "x: integer = 42;"
        env = self.semantic(code)
        decl = env.get("x")
        self.assertEqual(decl.type.name, "integer")
        self.assertIsInstance(decl.value, Integer)
        self.assertEqual(decl.value.value, 42)

    def test_assign_float(self):
        code = "pi: float = 3.14;"
        env = self.semantic(code)
        decl = env.get("pi")
        self.assertEqual(decl.type.name, "float")
        self.assertIsInstance(decl.value, Float)
        self.assertAlmostEqual(decl.value.value, 3.14)

    def test_assign_string(self):
        code = 'msg: string = "hello";'
        env = self.semantic(code)
        decl = env.get("msg")
        self.assertEqual(decl.type.name, "string")
        self.assertIsInstance(decl.value, String)
        self.assertEqual(decl.value.value, "hello")

    def test_assign_char(self):
        code = "letter: char = 'a';"
        env = self.semantic(code)
        decl = env.get("letter")
        self.assertEqual(decl.type.name, "char")
        self.assertIsInstance(decl.value, Char)
        self.assertEqual(decl.value.value, "a")

    def test_assign_boolean_true(self):
        code = "flag: boolean = true;"
        env = self.semantic(code)
        decl = env.get("flag")
        self.assertEqual(decl.type.name, "boolean")
        self.assertIsInstance(decl.value, Boolean)
        self.assertTrue(decl.value.value)

    def test_assign_boolean_false(self):
        code = "flag: boolean = false;"
        env = self.semantic(code)
        decl = env.get("flag")
        self.assertEqual(decl.type.name, "boolean")
        self.assertIsInstance(decl.value, Boolean)
        self.assertFalse(decl.value.value)

    def test_assign_negative_integer(self):
        code = "neg: integer = 7;"
        env = self.semantic(code)
        decl = env.get("neg")
        self.assertEqual(decl.type.name, "integer")
        self.assertIsInstance(decl.value, Integer)
        self.assertEqual(decl.value.value, 7)

    def test_assign_zero_float(self):
        code = "zero: float = 0.0;"
        env = self.semantic(code)
        decl = env.get("zero")
        self.assertEqual(decl.type.name, "float")
        self.assertIsInstance(decl.value, Float)
        self.assertEqual(decl.value.value, 0.0)

    def test_assign_empty_string(self):
        code = 'empty: string = "";'
        env = self.semantic(code)
        decl = env.get("empty")
        self.assertEqual(decl.type.name, "string")
        self.assertIsInstance(decl.value, String)
        self.assertEqual(decl.value.value, "")

    def test_assign_escape_char(self):
        code = r"newline: char = '\n';"
        env = self.semantic(code)
        decl = env.get("newline")
        self.assertEqual(decl.type.name, "char")
        self.assertIsInstance(decl.value, Char)
        self.assertEqual(decl.value.value, "\\n")
