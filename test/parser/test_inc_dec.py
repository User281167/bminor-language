import unittest
from parser import Parser
from scanner import Lexer
from model import *


class TestIncDec(unittest.TestCase):
    def setUp(self):
        self.lexer = Lexer()
        self.parser = Parser()

    def parse(self, code):
        tokens = self.lexer.tokenize(code)
        print([t.type for t in tokens])
        return self.parser.parse(tokens)

    # def test_basic_inc(self):
        # code = 'main: function void () = { }'
        # ast = self.parse(code)
        # decl = ast.body[0]
        # self.assertEqual(decl, Increment(VarLoc('x')))
