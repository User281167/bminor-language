import unittest
from parser import Parser
from scanner import Lexer
from model import *


class TestBinaryExpression(unittest.TestCase):
    def setUp(self):
        self.lexer = Lexer()
        self.parser = Parser()

    def parse(self, code):
        tokens = self.lexer.tokenize(code)
        return self.parser.parse(tokens)

    def test_sub_expression(self):
        code = "x: integer = 3 - 5;"
        ast = self.parse(code)
        decl = ast.body[0]
        self.assertIsInstance(decl.value, BinOper)
        self.assertEqual(decl.value.oper, "-")
        self.assertIsInstance(decl.value.left, Integer)
        self.assertIsInstance(decl.value.right, Integer)

        self.assertEqual(decl.value.left.value, 3)
        self.assertEqual(decl.value.right.value, 5)

    def test_complex_sub_expression(self):
        code = "x: integer = 3 + (5 - 7);"
        ast = self.parse(code)
        decl = ast.body[0]
        self.assertIsInstance(decl.value, BinOper)
        self.assertEqual(decl.value.oper, "+")
        self.assertIsInstance(decl.value.left, Integer)
        self.assertIsInstance(decl.value.right, BinOper)

        self.assertEqual(decl.value.left.value, 3)
        self.assertEqual(decl.value.right.oper, "-")
        self.assertIsInstance(decl.value.right.left, Integer)
        self.assertIsInstance(decl.value.right.right, Integer)

        self.assertEqual(decl.value.right.left.value, 5)
        self.assertEqual(decl.value.right.right.value, 7)

    def test_minus_expression(self):
        code = "x: integer = 10 - 2;"
        ast = self.parse(code)
        decl = ast.body[0]
        self.assertIsInstance(decl.value, BinOper)
        self.assertEqual(decl.value.oper, "-")
        self.assertIsInstance(decl.value.left, Integer)
        self.assertIsInstance(decl.value.right, Integer)

        self.assertEqual(decl.value.left.value, 10)
        self.assertEqual(decl.value.right.value, 2)

    def test_complex_minus_expression(self):
        code = "x: integer = (10 - 2) - 3;"
        ast = self.parse(code)
        decl = ast.body[0]

        # expr - 3
        self.assertIsInstance(decl.value, BinOper)
        self.assertEqual(decl.value.oper, "-")
        self.assertIsInstance(decl.value.left, BinOper)
        self.assertIsInstance(decl.value.right, Integer)
        self.assertEqual(decl.value.right.value, 3)

        # 10 - 2
        self.assertEqual(decl.value.left.oper, "-")
        self.assertIsInstance(decl.value.left.left, Integer)
        self.assertIsInstance(decl.value.left.right, Integer)
        self.assertEqual(decl.value.left.left.value, 10)
        self.assertEqual(decl.value.left.right.value, 2)

    def test_multiply_expression(self):
        code = "x: integer = 4 * 5;"
        ast = self.parse(code)
        decl = ast.body[0]
        self.assertIsInstance(decl.value, BinOper)
        self.assertEqual(decl.value.oper, "*")
        self.assertIsInstance(decl.value.left, Integer)
        self.assertIsInstance(decl.value.right, Integer)

        self.assertEqual(decl.value.left.value, 4)
        self.assertEqual(decl.value.right.value, 5)

    def test_complex_multiply_expression(self):
        code = "x: integer = (4 * 5) * 2;"
        ast = self.parse(code)
        decl = ast.body[0]

        # expr * 2
        self.assertIsInstance(decl.value, BinOper)
        self.assertEqual(decl.value.oper, "*")
        self.assertIsInstance(decl.value.left, BinOper)
        self.assertIsInstance(decl.value.right, Integer)
        self.assertEqual(decl.value.right.value, 2)

        # 4 * 5
        self.assertEqual(decl.value.left.oper, "*")
        self.assertIsInstance(decl.value.left.left, Integer)
        self.assertIsInstance(decl.value.left.right, Integer)
        self.assertEqual(decl.value.left.left.value, 4)
        self.assertEqual(decl.value.left.right.value, 5)

    def test_divide_expression(self):
        code = "x: integer = 20 / 4;"
        ast = self.parse(code)
        decl = ast.body[0]
        self.assertIsInstance(decl.value, BinOper)
        self.assertEqual(decl.value.oper, "/")
        self.assertIsInstance(decl.value.left, Integer)
        self.assertIsInstance(decl.value.right, Integer)

        self.assertEqual(decl.value.left.value, 20)
        self.assertEqual(decl.value.right.value, 4)

    def test_complex_divide_expression(self):
        code = "x: integer = (20 / 4) / 2;"
        ast = self.parse(code)
        decl = ast.body[0]

        # expr / 2
        self.assertIsInstance(decl.value, BinOper)
        self.assertEqual(decl.value.oper, "/")
        self.assertIsInstance(decl.value.left, BinOper)
        self.assertIsInstance(decl.value.right, Integer)
        self.assertEqual(decl.value.right.value, 2)

        # 20 / 4
        self.assertEqual(decl.value.left.oper, "/")
        self.assertIsInstance(decl.value.left.left, Integer)
        self.assertIsInstance(decl.value.left.right, Integer)
        self.assertEqual(decl.value.left.left.value, 20)
        self.assertEqual(decl.value.left.right.value, 4)

    def test_triple_divide_expression(self):
        code = "x: integer = 100 / 5 / 2;"
        ast = self.parse(code)
        decl = ast.body[0]

        # (100 / 5) / 2
        self.assertIsInstance(decl.value, BinOper)
        self.assertEqual(decl.value.oper, "/")
        self.assertIsInstance(decl.value.left, BinOper)
        self.assertIsInstance(decl.value.right, Integer)
        self.assertEqual(decl.value.right.value, 2)

        # 100 / 5
        self.assertEqual(decl.value.left.oper, "/")
        self.assertIsInstance(decl.value.left.left, Integer)
        self.assertIsInstance(decl.value.left.right, Integer)
        self.assertEqual(decl.value.left.left.value, 100)
        self.assertEqual(decl.value.left.right.value, 5)

    def test_power_expression(self):
        code = "x: integer = 2 ^ 3;"
        ast = self.parse(code)
        decl = ast.body[0]
        self.assertIsInstance(decl.value, BinOper)
        self.assertEqual(decl.value.oper, "^")
        self.assertIsInstance(decl.value.left, Integer)
        self.assertIsInstance(decl.value.right, Integer)

        self.assertEqual(decl.value.left.value, 2)
        self.assertEqual(decl.value.right.value, 3)

    def test_complex_power_expression(self):
        code = "x: integer = 2 ^ (3 ^ 2);"
        ast = self.parse(code)
        decl = ast.body[0]

        # 2 ^ expr
        self.assertIsInstance(decl.value, BinOper)
        self.assertEqual(decl.value.oper, "^")
        self.assertIsInstance(decl.value.left, Integer)
        self.assertIsInstance(decl.value.right, BinOper)
        self.assertEqual(decl.value.left.value, 2)

        # 3 ^ 2
        self.assertEqual(decl.value.right.oper, "^")
        self.assertIsInstance(decl.value.right.left, Integer)
        self.assertIsInstance(decl.value.right.right, Integer)
        self.assertEqual(decl.value.right.left.value, 3)
        self.assertEqual(decl.value.right.right.value, 2)

    def test_triple_power_expression(self):
        code = "x: integer = 2 ^ 3 ^ 2;"
        ast = self.parse(code)
        decl = ast.body[0]

        # (2 ^ 3) ^ 2
        self.assertIsInstance(decl.value, BinOper)
        self.assertEqual(decl.value.oper, "^")
        self.assertIsInstance(decl.value.left, BinOper)
        self.assertIsInstance(decl.value.right, Integer)
        self.assertEqual(decl.value.right.value, 2)

        # 2 ^ 3
        self.assertEqual(decl.value.left.oper, "^")
        self.assertIsInstance(decl.value.left.left, Integer)
        self.assertIsInstance(decl.value.left.right, Integer)
        self.assertEqual(decl.value.left.left.value, 2)
        self.assertEqual(decl.value.left.right.value, 3)

    def test_modulo_expression(self):
        code = "x: integer = 10 % 3;"
        ast = self.parse(code)
        decl = ast.body[0]
        self.assertIsInstance(decl.value, BinOper)
        self.assertEqual(decl.value.oper, "%")
        self.assertIsInstance(decl.value.left, Integer)
        self.assertIsInstance(decl.value.right, Integer)

        self.assertEqual(decl.value.left.value, 10)
        self.assertEqual(decl.value.right.value, 3)

    def test_complex_modulo_expression(self):
        code = "x: integer = 10 % (7 % 2);"
        ast = self.parse(code)
        decl = ast.body[0]

        # 10 % expr
        self.assertIsInstance(decl.value, BinOper)
        self.assertEqual(decl.value.oper, "%")
        self.assertIsInstance(decl.value.left, Integer)
        self.assertIsInstance(decl.value.right, BinOper)
        self.assertEqual(decl.value.left.value, 10)

        # 7 % 2
        self.assertEqual(decl.value.right.oper, "%")
        self.assertIsInstance(decl.value.right.left, Integer)
        self.assertIsInstance(decl.value.right.right, Integer)
        self.assertEqual(decl.value.right.left.value, 7)
        self.assertEqual(decl.value.right.right.value, 2)

    def test_triple_modulo_expression(self):
        code = "x: integer = 10 % 7 % 2;"
        ast = self.parse(code)
        decl = ast.body[0]

        # (10 % 7) % 2
        self.assertIsInstance(decl.value, BinOper)
        self.assertEqual(decl.value.oper, "%")
        self.assertIsInstance(decl.value.left, BinOper)
        self.assertIsInstance(decl.value.right, Integer)
        self.assertEqual(decl.value.right.value, 2)

        # 10 % 7
        self.assertEqual(decl.value.left.oper, "%")
        self.assertIsInstance(decl.value.left.left, Integer)
        self.assertIsInstance(decl.value.left.right, Integer)
        self.assertEqual(decl.value.left.left.value, 10)
        self.assertEqual(decl.value.left.right.value, 7)
