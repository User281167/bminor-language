import unittest
from parser import Parser
from scanner import Lexer
from model import *


class TestDeclarations(unittest.TestCase):
    def setUp(self):
        self.lexer = Lexer()
        self.parser = Parser()

    def parse(self, code):
        tokens = self.lexer.tokenize(code)
        return self.parser.parse(tokens)

    def test_var_decl(self):
        code = "x : integer = 42;"
        ast = self.parse(code)
        decl = ast.body[0]
        self.assertIsInstance(decl, VarDecl)
        self.assertEqual(decl.name, "x")
        self.assertEqual(decl.type.name, "integer")
        self.assertIsInstance(decl.value, Integer)
        self.assertEqual(decl.value.value, 42)

    def test_array_decl(self):
        code = "arr : array [3] integer = { 1, 2, 3 };"
        ast = self.parse(code)
        print("==================AST=================")
        print(ast)
        decl = ast.body[0]
        self.assertIsInstance(decl, ArrayDecl)
        self.assertEqual(decl.name, "arr")
        self.assertEqual(decl.type.base.name, "integer")
        self.assertEqual(decl.size.value, 3)
        self.assertEqual(len(decl.value), 3)
        self.assertTrue(all(isinstance(v, Integer) for v in decl.value))

    # def test_func_decl(self):
    #     code = """
    #     sum : FUNCTION INTEGER (a: INTEGER, b: INTEGER) = {
    #         RETURN a + b;
    #     }
    #     """
    #     ast = self.parse(code)
    #     decl = ast.body[0]
    #     self.assertIsInstance(decl, FuncDecl)
    #     self.assertEqual(decl.name, "sum")
    #     self.assertEqual(decl.return_type.name, "integer")
    #     self.assertEqual(len(decl.params), 2)
    #     self.assertEqual(decl.params[0].name, "a")
    #     self.assertEqual(decl.params[1].type.name, "integer")
    #     self.assertEqual(len(decl.body), 1)
    #     self.assertIsInstance(decl.body[0], ReturnStmt)
