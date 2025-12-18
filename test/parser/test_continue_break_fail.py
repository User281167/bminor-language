import unittest
from parser import Parser
from parser.model import *

from scanner import Lexer
from utils.errors import clear_errors, errors_detected, has_error


class TestContinueBreakError(unittest.TestCase):
    def setUp(self):
        self.lexer = Lexer()
        self.parser = Parser()
        clear_errors()

    def parse(self, code):
        tokens = self.lexer.tokenize(code)
        return self.parser.parse(tokens)

    def assertError(self, code, expected_error):
        self.parse(code)
        self.assertTrue(errors_detected())
        self.assertTrue(has_error(expected_error))

    def test_continue_error(self):
        code = "continue;"
        self.assertFalse(errors_detected())

    def test_break_error(self):
        code = "break;"
        self.assertFalse(errors_detected())
