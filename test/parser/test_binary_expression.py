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

    # def test_binary_expression(self):
    #     code = "x: integer = 3 + 5;"
    #     ast = self.parse(code)
    #     decl = ast.body[0]
    #     self.assertIsInstance(decl.value, BinOper)
    #     self.assertEqual(decl.value.op, "+")
    #     self.assertIsInstance(decl.value.left, Integer)
    #     self.assertIsInstance(decl.value.right, Integer)
