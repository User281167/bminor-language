import unittest
from parser import Parser, ParserError
from parser.model import *

from scanner import Lexer
from utils.errors import clear_errors, errors_detected, has_error


class TestComparisonError(unittest.TestCase):
    def setUp(self):
        self.lexer = Lexer()
        self.parser = Parser()
        clear_errors()

    def parse(self, code):
        tokens = self.lexer.tokenize(code)
        return self.parser.parse(tokens)

    def test_eq_no_operands(self):
        code = "b: boolean = ==;"
        self.parse(code)
        self.assertEqual(errors_detected(), 1)
        self.assertTrue(has_error(ParserError.MISSING_EXPRESSION))

    def test_bad_neq(self):
        code = "b: boolean = 5 !== 3;"
        self.parse(code)
        self.assertEqual(errors_detected(), 1)
        self.assertTrue(has_error(ParserError.INVALID_ASSIGNMENT))

    def test_less_no_operands(self):
        code = "b: boolean = 5 <;"
        self.parse(code)
        self.assertEqual(errors_detected(), 1)
        self.assertTrue(has_error(ParserError.MISSING_STATEMENT))

    def test_greater_no_operands(self):
        code = "b: boolean =  > 3;"
        self.parse(code)
        self.assertEqual(errors_detected(), 1)
        self.assertTrue(has_error(ParserError.MISSING_EXPRESSION))

    def test_bad_branches(self):
        code = "b: boolean = (==);"
        self.parse(code)
        self.assertEqual(errors_detected(), 1)
        self.assertTrue(has_error(ParserError.MISSING_EXPRESSION))

    def test_bad_less_eq(self):
        code = "b: boolean = 5 <== 3;"
        self.parse(code)
        self.assertEqual(errors_detected(), 1)
        self.assertTrue(has_error(ParserError.INVALID_ASSIGNMENT))
