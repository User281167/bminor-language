import unittest
from parser import Parser, ParserError
from scanner import Lexer
from parser.model import *
from utils.errors import errors_detected, clear_errors, has_error


class TestDoWhileLoopError(unittest.TestCase):
    def setUp(self):
        self.lexer = Lexer()
        self.parser = Parser()

    def parse(self, code):
        tokens = self.lexer.tokenize(code)
        return self.parser.parse(tokens)

    def test_do_while_missing_semicolon(self):
        code = """
        main: function void () = {
            do {
                print x;
            } while (x < 10)
        }
        """
        self.parse(code)
        self.assertTrue(errors_detected())
        self.assertTrue(has_error(ParserError.INVALID_STATEMENT))

    def test_do_while_missing_open_paren(self):
        code = """
        main: function void () = {
            do {
                print x;
            } while x < 10);
        }
        """
        self.parse(code)
        self.assertTrue(errors_detected())
        self.assertTrue(has_error(ParserError.UNEXPECTED_IDENTIFIER))

    def test_do_while_missing_close_paren(self):
        code = """
        main: function void () = {
            do {
                print x;
            } while (x < 10;
        }
        """
        self.parse(code)
        self.assertTrue(errors_detected())
        self.assertTrue(has_error(ParserError.MISSING_STATEMENT))

    def test_do_while_empty_condition(self):
        code = """
        main: function void () = {
            do {
                print x;
            } while ();
        }
        """
        self.parse(code)
        self.assertTrue(errors_detected())
        self.assertTrue(has_error(ParserError.MISSING_EXPRESSION))

    def test_do_while_without_braces(self):
        code = """
        main: function void () = {
            do print x; while (x < 10);
        }
        """
        self.parse(code)
        self.assertTrue(errors_detected())
        self.assertTrue(has_error(ParserError.INVALID_STATEMENT))

    # def test_do_while_non_boolean_condition(self):
    #     # semantic error
    #     code = """
    #     main: function void () = {
    #         do {
    #             print x;
    #         } while ("hello");
    #     }
    #     """
    #     ast = self.parse(code)
    #     decl = ast.body[0]
    #     self.assertIsInstance(decl, DoWhileStmt)

    def test_misspelled_while_keyword(self):
        code = """
        main: function void () = {
            whle (x < 10) {
                print x;
            }
        }
        """
        self.parse(code)
        self.assertTrue(errors_detected())
        self.assertTrue(has_error(ParserError.INVALID_STATEMENT))

    def test_do_while_wrong_order(self):
        code = """
        main: function void () = {
            while (x < 10) do {
                print x;
            };
        }
        """
        self.parse(code)
        self.assertTrue(errors_detected())
        self.assertTrue(has_error(ParserError.INVALID_STATEMENT))

    def test_do_without_while(self):
        code = """
        main: function void () = {
            do {
                print x;
            }
        }
        """
        self.parse(code)
        self.assertTrue(errors_detected())
        self.assertTrue(has_error(ParserError.INVALID_STATEMENT))
