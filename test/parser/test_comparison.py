import unittest
from parser import Parser
from scanner import Lexer
from parser.model import *


class TestComparison(unittest.TestCase):
    def setUp(self):
        self.lexer = Lexer()
        self.parser = Parser()

    def parse(self, code):
        tokens = self.lexer.tokenize(code)
        return self.parser.parse(tokens)

    def test_equality_comparison(self):
        code = "b: boolean = 5 == 5;"
        ast = self.parse(code)
        decl = ast.body[0]
        self.assertIsInstance(decl, VarDecl)
        self.assertEqual(decl.name, "b")
        self.assertIsInstance(decl.value, BinOper)
        self.assertEqual(decl.value.oper, "==")
        self.assertEqual(decl.value.left.value, 5)
        self.assertEqual(decl.value.right.value, 5)

    def test_equality_comparison_vars(self):
        code = "b: boolean = a == b;"
        ast = self.parse(code)
        decl = ast.body[0]
        self.assertIsInstance(decl, VarDecl)
        self.assertEqual(decl.name, "b")

        self.assertIsInstance(decl.value, BinOper)
        self.assertEqual(decl.value.oper, "==")

        self.assertIsInstance(decl.value.left, VarLoc)
        self.assertEqual(decl.value.left.name, "a")
        self.assertEqual(decl.value.right.name, "b")

    def test_inequality_comparison(self):
        code = "b: boolean = 5 != a;"
        ast = self.parse(code)
        decl = ast.body[0]
        self.assertIsInstance(decl, VarDecl)
        self.assertEqual(decl.name, "b")
        self.assertIsInstance(decl.value, BinOper)
        self.assertEqual(decl.value.oper, "!=")
        self.assertEqual(decl.value.left.value, 5)

        self.assertIsInstance(decl.value.right, VarLoc)
        self.assertEqual(decl.value.right.name, "a")

    def test_less_than_comparison(self):
        code = "b: boolean = 3 < 5;"
        ast = self.parse(code)
        decl = ast.body[0]
        self.assertIsInstance(decl, VarDecl)
        self.assertEqual(decl.name, "b")
        self.assertIsInstance(decl.value, BinOper)
        self.assertEqual(decl.value.oper, "<")
        self.assertEqual(decl.value.left.value, 3)
        self.assertEqual(decl.value.right.value, 5)

    def test_less_than_vars(self):
        code = "b: boolean = a < b;"
        ast = self.parse(code)
        decl = ast.body[0]
        self.assertIsInstance(decl, VarDecl)
        self.assertEqual(decl.name, "b")

        self.assertIsInstance(decl.value, BinOper)
        self.assertEqual(decl.value.oper, "<")

        self.assertIsInstance(decl.value.left, VarLoc)
        self.assertEqual(decl.value.left.name, "a")
        self.assertEqual(decl.value.right.name, "b")

    def test_less_equal_comparison(self):
        code = "b: boolean = 5 <= 5;"
        ast = self.parse(code)
        decl = ast.body[0]
        self.assertIsInstance(decl, VarDecl)
        self.assertEqual(decl.name, "b")
        self.assertIsInstance(decl.value, BinOper)
        self.assertEqual(decl.value.oper, "<=")
        self.assertEqual(decl.value.left.value, 5)
        self.assertEqual(decl.value.right.value, 5)

    def test_less_equal_vars(self):
        code = "b: boolean = a <= b;"
        ast = self.parse(code)
        decl = ast.body[0]
        self.assertIsInstance(decl, VarDecl)
        self.assertEqual(decl.name, "b")

        self.assertIsInstance(decl.value, BinOper)
        self.assertEqual(decl.value.oper, "<=")

        self.assertIsInstance(decl.value.left, VarLoc)
        self.assertEqual(decl.value.left.name, "a")
        self.assertEqual(decl.value.right.name, "b")

    def test_greater_than_comparison(self):
        code = "b: boolean = 7 > 3;"
        ast = self.parse(code)
        decl = ast.body[0]
        self.assertIsInstance(decl, VarDecl)
        self.assertEqual(decl.name, "b")
        self.assertIsInstance(decl.value, BinOper)
        self.assertEqual(decl.value.oper, ">")
        self.assertEqual(decl.value.left.value, 7)
        self.assertEqual(decl.value.right.value, 3)

    def test_greater_equal_comparison(self):
        code = "b: boolean = 5 >= 5;"
        ast = self.parse(code)
        decl = ast.body[0]
        self.assertIsInstance(decl, VarDecl)
        self.assertEqual(decl.name, "b")
        self.assertIsInstance(decl.value, BinOper)
        self.assertEqual(decl.value.oper, ">=")
        self.assertEqual(decl.value.left.value, 5)
        self.assertEqual(decl.value.right.value, 5)

    def test_greater_equal_vars(self):
        code = "b: boolean = a >= b;"
        ast = self.parse(code)
        decl = ast.body[0]
        self.assertIsInstance(decl, VarDecl)
        self.assertEqual(decl.name, "b")

        self.assertIsInstance(decl.value, BinOper)
        self.assertEqual(decl.value.oper, ">=")

        self.assertIsInstance(decl.value.left, VarLoc)
        self.assertEqual(decl.value.left.name, "a")
        self.assertEqual(decl.value.right.name, "b")

    def test_multi_equality(self):
        # el parser lo acepta aunque puede ser un problema para el semántico
        code = "b: boolean = 1 == 2 == 3;"
        ast = self.parse(code)
        decl = ast.body[0]
        self.assertIsInstance(decl, VarDecl)

        self.assertIsInstance(decl.value, BinOper)
        self.assertEqual(decl.value.oper, "==")

        self.assertIsInstance(decl.value.left, BinOper)
        self.assertEqual(decl.value.left.oper, "==")
        self.assertEqual(decl.value.left.left.value, 1)
        self.assertEqual(decl.value.left.right.value, 2)

        self.assertIsInstance(decl.value.right, Integer)
        self.assertEqual(decl.value.right.value, 3)

    def test_eq_char(self):
        code = "b: boolean = 'a' == 'b';"
        ast = self.parse(code)
        decl = ast.body[0]
        self.assertIsInstance(decl, VarDecl)
        self.assertEqual(decl.name, "b")
        self.assertIsInstance(decl.value, BinOper)
        self.assertEqual(decl.value.oper, "==")
        self.assertEqual(decl.value.left.value, "a")
        self.assertEqual(decl.value.right.value, "b")

    def test_string_vars(self):
        # error semántico
        code = "b: string = a == b;"
        ast = self.parse(code)
        decl = ast.body[0]
        self.assertIsInstance(decl, VarDecl)
        self.assertEqual(decl.name, "b")

        self.assertIsInstance(decl.value, BinOper)
        self.assertEqual(decl.value.oper, "==")

        self.assertIsInstance(decl.value.left, VarLoc)
        self.assertEqual(decl.value.left.name, "a")
        self.assertEqual(decl.value.right.name, "b")
