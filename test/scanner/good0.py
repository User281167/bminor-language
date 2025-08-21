
import unittest
import sys
import os


from scanner import Lexer


class TestComments(unittest.TestCase):
    def setUp(self):
        self.lexer = Lexer()

    def test_valid_cpp_comment(self):
        test_input = "/*/ This is a valid C++ comment\n"
        tokens = list(self.lexer.tokenize(test_input))

        self.assertEqual(len(tokens), 0)
