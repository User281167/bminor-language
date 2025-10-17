import unittest
from parser import Parser
from parser.model import *

from scanner import Lexer


class TestUnaryExpression(unittest.TestCase):
    def setUp(self):
        self.lexer = Lexer()
        self.parser = Parser()

    def parse(self, code):
        tokens = self.lexer.tokenize(code)
        return self.parser.parse(tokens)

    def test_unary_minus_expression(self):
        code = "x: integer = -5;"
        ast = self.parse(code)
        decl = ast.body[0]
        self.assertIsInstance(decl.value, UnaryOper)
        self.assertEqual(decl.value.oper, "-")
        self.assertIsInstance(decl.value.expr, Integer)
        self.assertEqual(decl.value.expr.value, 5)

    def test_unary_plus_expression(self):
        code = "x: integer = +5;"
        ast = self.parse(code)
        decl = ast.body[0]
        self.assertIsInstance(decl.value, UnaryOper)
        self.assertEqual(decl.value.oper, "+")
        self.assertIsInstance(decl.value.expr, Integer)
        self.assertEqual(decl.value.expr.value, 5)

    def test_unary_not_expression(self):
        code = "x: boolean = !true;"
        ast = self.parse(code)
        decl = ast.body[0]
        self.assertIsInstance(decl.value, UnaryOper)
        self.assertEqual(decl.value.oper, "!")
        self.assertIsInstance(decl.value.expr, Boolean)
        self.assertEqual(decl.value.expr.value, True)
