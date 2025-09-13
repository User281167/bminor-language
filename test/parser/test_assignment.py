import unittest
from parser import Parser
from scanner import Lexer
from model import *
from errors import errors_detected


class TestAssignment(unittest.TestCase):
    def setUp(self):
        self.lexer = Lexer()
        self.parser = Parser()

    def parse(self, code):
        tokens = self.lexer.tokenize(code)
        return self.parser.parse(tokens)

    def test_integer_assignment(self):
        code = "x: integer = 42;"
        ast = self.parse(code)
        decl = ast.body[0]
        self.assertIsInstance(decl, VarDecl)
        self.assertEqual(decl.name, "x")
        self.assertEqual(decl.type.name, "integer")
        self.assertIsInstance(decl.value, Integer)
        self.assertEqual(decl.value.value, 42)

    def test_integer_declaration(self):
        code = "x: integer;"
        ast = self.parse(code)
        decl = ast.body[0]
        self.assertIsInstance(decl, VarDecl)
        self.assertEqual(decl.name, "x")
        self.assertEqual(decl.type.name, "integer")
        self.assertEqual(decl.value, None)

    def test_char_assignment(self):
        code = "c: char = 'a';"
        ast = self.parse(code)
        decl = ast.body[0]
        self.assertIsInstance(decl, VarDecl)
        self.assertEqual(decl.name, "c")
        self.assertEqual(decl.type.name, "char")
        self.assertIsInstance(decl.value, Char)
        self.assertEqual(decl.value.value, 'a')

    def test_char_declaration(self):
        code = "c: char;"
        ast = self.parse(code)
        decl = ast.body[0]
        self.assertIsInstance(decl, VarDecl)
        self.assertEqual(decl.name, "c")
        self.assertEqual(decl.type.name, "char")
        self.assertEqual(decl.value, None)

    def test_float_assignment(self):
        code = "f: float = 3.14;"
        ast = self.parse(code)
        decl = ast.body[0]
        self.assertIsInstance(decl, VarDecl)
        self.assertEqual(decl.name, "f")
        self.assertEqual(decl.type.name, "float")
        self.assertIsInstance(decl.value, Float)
        self.assertAlmostEqual(decl.value.value, 3.14, places=7)

    def test_float_declaration(self):
        code = "f: float;"
        ast = self.parse(code)
        decl = ast.body[0]
        self.assertIsInstance(decl, VarDecl)
        self.assertEqual(decl.name, "f")
        self.assertEqual(decl.type.name, "float")
        self.assertEqual(decl.value, None)

    def test_string_assignment(self):
        code = 's: string = "hello";'
        ast = self.parse(code)
        decl = ast.body[0]
        self.assertIsInstance(decl, VarDecl)
        self.assertEqual(decl.name, "s")
        self.assertEqual(decl.type.name, "string")
        self.assertIsInstance(decl.value, String)
        self.assertEqual(decl.value.value, 'hello')

    def test_string_declaration(self):
        code = "s: string;"
        ast = self.parse(code)
        decl = ast.body[0]
        self.assertIsInstance(decl, VarDecl)
        self.assertEqual(decl.name, "s")
        self.assertEqual(decl.type.name, "string")
        self.assertEqual(decl.value, None)

    def test_boolean_assignment_true(self):
        code = "b: boolean = true;"
        ast = self.parse(code)
        decl = ast.body[0]
        self.assertIsInstance(decl, VarDecl)
        self.assertEqual(decl.name, "b")
        self.assertEqual(decl.type.name, "boolean")
        self.assertIsInstance(decl.value, Boolean)
        self.assertEqual(decl.value.value, True)

    def test_boolean_assignment_false(self):
        code = "b: boolean = false;"
        ast = self.parse(code)
        decl = ast.body[0]
        self.assertIsInstance(decl, VarDecl)
        self.assertEqual(decl.name, "b")
        self.assertEqual(decl.type.name, "boolean")
        self.assertIsInstance(decl.value, Boolean)
        self.assertEqual(decl.value.value, False)

    def test_boolean_declaration(self):
        code = "b: boolean;"
        ast = self.parse(code)
        decl = ast.body[0]
        self.assertIsInstance(decl, VarDecl)
        self.assertEqual(decl.name, "b")
        self.assertEqual(decl.type.name, "boolean")
        self.assertEqual(decl.value, None)
