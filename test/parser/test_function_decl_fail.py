import unittest
from parser import Parser, ParserError
from scanner import Lexer
from model import *
from errors import errors_detected, clear_errors, has_error


class TestFunctionDeclError(unittest.TestCase):
    def setUp(self):
        self.lexer = Lexer()
        self.parser = Parser()
        clear_errors()

    def parse(self, code):
        tokens = self.lexer.tokenize(code)
        return self.parser.parse(tokens)

    def test_fun_invalid_name(self):
        code = "123myFunc: function integer () = { }"
        self.parse(code)
        self.assertEqual(errors_detected(), 1)
        self.assertTrue(has_error(ParserError.UNEXPECTED_TOKEN))

    def test_fun_invalid_name_num(self):
        code = "123: function integer () = { }"
        self.parse(code)
        self.assertEqual(errors_detected(), 1)
        self.assertTrue(has_error(ParserError.UNEXPECTED_TOKEN))

    def test_fun_invalid_function_without_name(self):
        code = "function integer () = { }"
        self.parse(code)
        self.assertEqual(errors_detected(), 1)
        self.assertTrue(has_error(ParserError.UNEXPECTED_TOKEN))

    def test_fun_invalid_function_without_param_decl(self):
        code = "main: function integer = { }"
        self.parse(code)
        self.assertEqual(errors_detected(), 1)
        self.assertTrue(has_error(ParserError.INVALID_ASSIGNMENT))

    def test_fun_invalid_function_without_body(self):
        code = "main: function integer ()"
        self.parse(code)
        self.assertEqual(errors_detected(), 1)
        self.assertTrue(has_error(ParserError.UNEXPECTED_EOF))

    def test_fun_invalid_function_without_return_type(self):
        code = "main: function () = { }"
        self.parse(code)
        self.assertEqual(errors_detected(), 1)
        self.assertTrue(has_error(ParserError.INCOMPLETE_FUNCTION_DECLARATION))

    def test_fun_no_two_dots(self):
        code = "main function integer () = { }"
        self.parse(code)
        self.assertEqual(errors_detected(), 1)
        self.assertTrue(has_error(ParserError.UNEXPECTED_TOKEN))

    def test_fun_invalid_return_type(self):
        code = "main: function int () = { }"
        self.parse(code)
        self.assertEqual(errors_detected(), 1)
        self.assertTrue(has_error(ParserError.SYNTAX_ERROR))
