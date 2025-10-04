import unittest
from parser import Parser, ParserError
from scanner import Lexer
from model import *
from errors import errors_detected, clear_errors, has_error


class TestForLoopError(unittest.TestCase):
    def setUp(self):
        self.lexer = Lexer()
        self.parser = Parser()
        clear_errors()

    def parse(self, code):
        tokens = self.lexer.tokenize(code)
        return self.parser.parse(tokens)

    def test_for_outside_function(self):
        code = "for (i = 0; i < 10; i = i + 1) { print i; }"
        self.parse(code)
        self.assertTrue(has_error(ParserError.UNEXPECTED_TOKEN))

    def test_for_unclosed_body(self):
        code = """
        main: function void () = {
            for (i = 0; i < 10; i = i + 1) {
                print i;
        }
        """
        self.parse(code)
        self.assertTrue(has_error(ParserError.UNEXPECTED_EOF))

    def test_for_with_one_expression(self):
        code = """
        main: function void () = {
            for (i = 0;) { print i; }
        }
        """
        self.parse(code)
        self.assertTrue(has_error(ParserError.MISSING_EXPRESSION))

    def test_for_with_extra_expression(self):
        code = """
        main: function void () = {
            for (i = 0; i < 10; i = i + 1; x = 5) { print i; }
        }
        """
        self.parse(code)
        self.assertTrue(has_error(ParserError.MISSING_STATEMENT))

    def test_for_with_empty_body(self):
        code = """
        main: function void () = {
            for (i = 0; i < 10; i = i + 1);
        }
        """
        self.parse(code)
        self.assertTrue(has_error(ParserError.MISSING_STATEMENT))

    def test_for_missing_closing_paren(self):
        code = """
        main: function void () = {
            for (i = 0; i < 10; i = i + 1 { print i; }
        }
        """
        self.parse(code)
        self.assertTrue(has_error(ParserError.INVALID_STATEMENT))

    def test_for_missing_semicolon(self):
        code = """
        main: function void () = {
            for (i = 0 i < 10; i = i + 1) { print i; }
        }
        """
        self.parse(code)
        self.assertTrue(has_error(ParserError.UNEXPECTED_IDENTIFIER))
