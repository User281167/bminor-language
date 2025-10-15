import unittest
from parser import Parser, ParserError
from scanner import Lexer
from parser.model import *
from utils.errors import clear_errors, has_error, errors_detected


class TestInvalidIfStmt(unittest.TestCase):
    def setUp(self):
        self.lexer = Lexer()
        self.parser = Parser()
        clear_errors()

    def parse(self, code):
        tokens = self.lexer.tokenize(code)
        return self.parser.parse(tokens)

    def test_if_missing_condition(self):
        code = """
        main: function void () = {
            if () {
                print 1;
            }
        }
        """
        self.parse(code)
        self.assertEqual(errors_detected(), 1)
        self.assertTrue(has_error(ParserError.MISSING_EXPRESSION))

    def test_if_missing_parenthesis(self):
        code = """
        main: function void () = {
            if true {
                print 1;
            }
        }
        """
        self.parse(code)
        self.assertTrue(has_error(ParserError.UNEXPECTED_TOKEN))

    def test_if_missing_opening_parenthesis(self):
        code = """
        main: function void () = {
            if true) {
                print 1;
            }
        }
        """
        self.parse(code)
        self.assertTrue(has_error(ParserError.UNEXPECTED_TOKEN))

    def test_if_missing_closing_parenthesis(self):
        code = """
        main: function void () = {
            if (true {
                print 1;
            }
        }
        """
        self.parse(code)
        self.assertTrue(has_error(ParserError.INVALID_STATEMENT))

    def test_else_without_if(self):
        code = """
        main: function void () = {
            else {
                print 1;
            }
        }
        """
        self.parse(code)
        self.assertTrue(has_error(ParserError.UNEXPECTED_TOKEN))

    def test_if_with_invalid_condition(self):
        code = """
        main: function void () = {
            if (1 +) {
                print 1;
            }
        }
        """
        self.parse(code)
        self.assertTrue(has_error(ParserError.MISSING_EXPRESSION))

    def test_if_with_invalid_operator(self):
        code = """
        main: function void () = {
            if (true := false) {
                print 1;
            }
        }
        """
        self.parse(code)
        self.assertTrue(has_error(ParserError.UNEXPECTED_COLON))
