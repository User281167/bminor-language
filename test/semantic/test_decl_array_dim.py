import unittest
from parser import Parser
from scanner import Lexer
from parser.model import *
from semantic.checker import Check
from utils import errors_detected, clear_errors


class TestArrayDeclMultiDimension(unittest.TestCase):
    def setUp(self):
        self.lexer = Lexer()
        self.parser = Parser()
        clear_errors()

    def semantic(self, code):
        tokens = self.lexer.tokenize(code)
        ast = self.parser.parse(tokens)
        return Check.checker(ast)

    def test_array_decl(self):
        code = "x: array [1] array [2] integer;"
        env = self.semantic(code)
        self.assertTrue(errors_detected())
