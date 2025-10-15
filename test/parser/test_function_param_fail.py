import unittest
from parser import Parser, ParserError
from scanner import Lexer
from parser.model import *
from utils.errors import clear_errors, errors_detected, has_error


class TestFunctionParamsError(unittest.TestCase):
    def setUp(self):
        self.lexer = Lexer()
        self.parser = Parser()
        clear_errors()

    def parse(self, code):
        tokens = self.lexer.tokenize(code)
        return self.parser.parse(tokens)

    def test_fun_missing_return_type(self):
        code = "main: function () = { }"
        self.parse(code)
        self.assertTrue(has_error(ParserError.INCOMPLETE_FUNCTION_DECLARATION))

    def test_fun_missing_param_type(self):
        code = "main: function integer (x) = { return x; }"
        self.parse(code)
        self.assertTrue(has_error(ParserError.MISSING_EXPRESSION))

    def test_fun_missing_param_name(self):
        code = "main: function integer (: integer) = { return 0; }"
        self.parse(code)
        self.assertTrue(has_error(ParserError.UNEXPECTED_COLON))

    def test_fun_missing_param_comma(self):
        code = "main: function integer (a: integer b: integer) = { return 0; }"
        self.parse(code)
        self.assertTrue(has_error(ParserError.UNEXPECTED_IDENTIFIER))

    def test_fun_missing_param_closing_paren(self):
        code = "main: function integer (a: integer, b: integer = { return 0; }"
        self.parse(code)
        self.assertTrue(has_error(ParserError.INVALID_ASSIGNMENT))

    def test_fun_missing_body(self):
        code = "main: function integer (a: integer, b: integer)"
        self.parse(code)
        self.assertTrue(has_error(ParserError.UNEXPECTED_EOF))
