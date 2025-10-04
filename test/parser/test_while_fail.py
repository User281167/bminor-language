import unittest
from parser import Parser, ParserError
from scanner import Lexer
from model import *
from errors import errors_detected, clear_errors, has_error


class TestWhileLoopError(unittest.TestCase):
    def setUp(self):
        self.lexer = Lexer()
        self.parser = Parser()
        clear_errors()

    def parse(self, code):
        tokens = self.lexer.tokenize(code)
        return self.parser.parse(tokens)

    def test_while_missing_open_paren(self):
        code = """
        main: function void () = {
            while x < 10) {
                print x;
            }
        }
        """
        self.parse(code)
        self.assertTrue(has_error(ParserError.UNEXPECTED_IDENTIFIER))

    def test_while_missing_close_paren(self):
        code = """
        main: function void () = {
            while (x < 10 {
                print x;
            }
        }
        """
        self.parse(code)
        self.assertTrue(has_error(ParserError.INVALID_STATEMENT))

    # def test_while_with_non_boolean_condition(self):
    # error semantic
    #     code = """
    #     main: function void () = {
    #         while ("hello") {
    #             print x;
    #         }
    #     }
    #     """
    #     self.parse(code)
    #     self.assertTrue(errors_detected())
    #     # self.assertTrue(has_error(SemanticError.INVALID_CONDITION_TYPE))

    def test_while_unclosed_body(self):
        code = """
        main: function void () = {
            while (x < 10) {
                print x;
        }
        """
        self.parse(code)
        self.assertTrue(has_error(ParserError.UNEXPECTED_EOF))

    def test_while_with_empty_statement(self):
        code = """
        main: function void () = {
            while (x < 10);
        }
        """
        self.parse(code)
        self.assertTrue(has_error(ParserError.MISSING_STATEMENT))
