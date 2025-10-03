import unittest
from parser import Parser
from scanner import Lexer
from model import *


class TestAssignment(unittest.TestCase):
    def setUp(self):
        self.lexer = Lexer()
        self.parser = Parser()

    def parse(self, code):
        tokens = self.lexer.tokenize(code)
        return self.parser.parse(tokens)

    # def test_assignment(self):
    #     code = "main: function void () = { a = 1; }"
    #     ast = self.parse(code)
    #     decl = ast.body[0]
    #     self.assertIsInstance(decl, VarDecl)
    #     self.assertEqual(decl.name, "a")
    #     self.assertEqual(decl.type.name, "integer")
    #     self.assertIsInstance(decl.value, Integer)
    #     self.assertEqual(decl.value.value, 1)

    #     self.assertEqual(self.parse("a = 1"), Assignment("a", 1))

    def test_assign_integer(self):
        code = "x: integer = 42;"
        ast = self.parse(code)
        decl = ast.body[0]
        self.assertIsInstance(decl, VarDecl)
        self.assertEqual(decl.name, "x")
        self.assertEqual(decl.type.name, "integer")
        self.assertIsInstance(decl.value, Integer)
        self.assertEqual(decl.value.value, 42)

    def test_assign_char(self):
        code = "c: char = 'a';"
        ast = self.parse(code)
        decl = ast.body[0]
        self.assertIsInstance(decl, VarDecl)
        self.assertEqual(decl.name, "c")
        self.assertEqual(decl.type.name, "char")
        self.assertIsInstance(decl.value, Char)
        self.assertEqual(decl.value.value, 'a')
        self.assertEqual(decl.value.type.name, 'char')

    def test_assign_float(self):
        code = "f: float = 3.14;"
        ast = self.parse(code)
        decl = ast.body[0]
        self.assertIsInstance(decl, VarDecl)
        self.assertEqual(decl.name, "f")
        self.assertEqual(decl.type.name, "float")
        self.assertIsInstance(decl.value, Float)
        self.assertAlmostEqual(decl.value.value, 3.14, places=7)
        self.assertEqual(decl.value.type.name, 'float')

    def test_assign_string(self):
        code = 's: string = "hello";'
        ast = self.parse(code)
        decl = ast.body[0]
        self.assertIsInstance(decl, VarDecl)
        self.assertEqual(decl.name, "s")
        self.assertEqual(decl.type.name, "string")
        self.assertIsInstance(decl.value, String)
        self.assertEqual(decl.value.value, 'hello')
        self.assertEqual(decl.value.type.name, 'string')

    def test_assign_boolean_true(self):
        code = "b: boolean = true;"
        ast = self.parse(code)
        decl = ast.body[0]
        self.assertIsInstance(decl, VarDecl)
        self.assertEqual(decl.name, "b")
        self.assertEqual(decl.type.name, "boolean")
        self.assertIsInstance(decl.value, Boolean)
        self.assertEqual(decl.value.value, True)
        self.assertEqual(decl.value.type.name, 'boolean')

    def test_assign_boolean_false(self):
        code = "b: boolean = false;"
        ast = self.parse(code)
        decl = ast.body[0]
        self.assertIsInstance(decl, VarDecl)
        self.assertEqual(decl.name, "b")
        self.assertEqual(decl.type.name, "boolean")
        self.assertIsInstance(decl.value, Boolean)
        self.assertEqual(decl.value.value, False)
        self.assertEqual(decl.value.type.name, 'boolean')

    def test_assign_boolean_var(self):
        code = "b: boolean = a;"
        ast = self.parse(code)
        decl = ast.body[0]
        self.assertIsInstance(decl, VarDecl)
        self.assertEqual(decl.name, "b")
        self.assertEqual(decl.type.name, "boolean")
        self.assertIsInstance(decl.value, VarLoc)
        self.assertEqual(decl.value.name, "a")

    def test_assign_char_var(self):
        code = "c: char = a;"
        ast = self.parse(code)
        decl = ast.body[0]
        self.assertIsInstance(decl, VarDecl)
        self.assertEqual(decl.name, "c")
        self.assertEqual(decl.type.name, "char")
        self.assertIsInstance(decl.value, VarLoc)
        self.assertEqual(decl.value.name, "a")

    def test_assign_float_var(self):
        code = "f: float = a;"
        ast = self.parse(code)
        decl = ast.body[0]
        self.assertIsInstance(decl, VarDecl)
        self.assertEqual(decl.name, "f")
        self.assertEqual(decl.type.name, "float")
        self.assertIsInstance(decl.value, VarLoc)
        self.assertEqual(decl.value.name, "a")

    def test_assign_string_var(self):
        code = 's: string = a;'
        ast = self.parse(code)
        decl = ast.body[0]
        self.assertIsInstance(decl, VarDecl)
        self.assertEqual(decl.name, "s")
        self.assertEqual(decl.type.name, "string")
        self.assertIsInstance(decl.value, VarLoc)
        self.assertEqual(decl.value.name, "a")

    def test_assign_boolean_var(self):
        code = "b: boolean = a;"
        ast = self.parse(code)
        decl = ast.body[0]
        self.assertIsInstance(decl, VarDecl)
        self.assertEqual(decl.name, "b")
        self.assertEqual(decl.type.name, "boolean")
        self.assertIsInstance(decl.value, VarLoc)
        self.assertEqual(decl.value.name, "a")

    def test_assign_char_var(self):
        code = "c: char = a;"
        ast = self.parse(code)
        decl = ast.body[0]
        self.assertIsInstance(decl, VarDecl)
        self.assertEqual(decl.name, "c")
        self.assertEqual(decl.type.name, "char")
        self.assertIsInstance(decl.value, VarLoc)
        self.assertEqual(decl.value.name, "a")

    def test_assign_string_var(self):
        code = "s: string = a;"
        ast = self.parse(code)
        decl = ast.body[0]
        self.assertIsInstance(decl, VarDecl)
        self.assertEqual(decl.name, "s")
        self.assertEqual(decl.type.name, "string")
        self.assertIsInstance(decl.value, VarLoc)
        self.assertEqual(decl.value.name, "a")
