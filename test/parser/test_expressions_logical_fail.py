import unittest
from parser import Parser, ParserError
from scanner import Lexer
from model import *
from errors import errors_detected, clear_errors, has_error


class TestLogicalExpressionsErrors(unittest.TestCase):
    def setUp(self):
        clear_errors()
        self.lexer = Lexer()
        self.parser = Parser()

    def parse(self, code):
        tokens = self.lexer.tokenize(code)
        return self.parser.parse(tokens)

    # ========== LOGICAL EXPRESSIONS ==========

    def test_or_bad_ope(self):
        code = "x: boolean = true or 1"
        ast = self.parse(code)
        self.assertTrue(errors_detected())
        self.assertTrue(has_error(ParserError.UNEXPECTED_IDENTIFIER))

    def test_lor_bad_operands(self):
        code = "x: boolean = ` 1"
        ast = self.parse(code)
        self.assertTrue(errors_detected())
        self.assertTrue(has_error(ParserError.MISSING_EXPRESSION))

    def test_empty_not(self):
        code = "x: boolean = !;"
        ast = self.parse(code)
        self.assertTrue(errors_detected())
        self.assertTrue(has_error(ParserError.MISSING_STATEMENT))

    def test_lor_no_operands(self):
        code = "x: boolean = `;"
        ast = self.parse(code)
        self.assertTrue(errors_detected())
        self.assertTrue(has_error(ParserError.MISSING_EXPRESSION))

    def test_land_no_operands(self):
        code = "x: boolean = &&;"
        ast = self.parse(code)
        self.assertTrue(errors_detected())
        self.assertTrue(has_error(ParserError.MISSING_EXPRESSION))

    def test_bad_ope(self):
        code = "x: boolean = true || && false;"
        ast = self.parse(code)
        self.assertTrue(errors_detected())
        self.assertTrue(has_error(ParserError.UNSUPPORTED_OPERATOR))

    def test_bad_grouping(self):
        code = "x: boolean = (true || && false);"
        ast = self.parse(code)
        self.assertTrue(errors_detected())
        self.assertTrue(has_error(ParserError.UNSUPPORTED_OPERATOR))

    def test_bad_ope_type(self):
        code = "x: boolean = true ^^ false;"
        ast = self.parse(code)
        self.assertTrue(errors_detected())
        self.assertTrue(has_error(ParserError.SYNTAX_ERROR))

    def test_bad_not_in_end(self):
        code = "x: boolean = a!;"
        ast = self.parse(code)
        self.assertTrue(errors_detected())
        self.assertTrue(has_error(ParserError.INVALID_NOT))

    def test_bad_not_in_middle(self):
        code = "x: boolean = a ! b;"
        ast = self.parse(code)
        self.assertTrue(errors_detected())
        self.assertTrue(has_error(ParserError.INVALID_NOT))

    def test_no_support_bitwise_and(self):
        code = "x: boolean = a & b;"
        ast = self.parse(code)
        self.assertTrue(errors_detected())
        self.assertTrue(has_error(ParserError.UNSUPPORTED_OPERATOR))

    def test_no_support_bitwise_or(self):
        code = "x: boolean = a | b;"
        ast = self.parse(code)
        self.assertTrue(errors_detected())
        self.assertTrue(has_error(ParserError.UNSUPPORTED_OPERATOR))

    def test_no_support_bitwise_not(self):
        code = "x: boolean = ~a;"
        ast = self.parse(code)
        self.assertTrue(errors_detected())
        self.assertTrue(has_error(ParserError.UNSUPPORTED_OPERATOR))
