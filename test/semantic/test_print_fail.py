import unittest
from parser import Parser, ParserError
from parser.model import *

from scanner import Lexer
from semantic.checker import Check, SemanticError
from utils import clear_errors, errors_detected, has_error


class TestPrintErrors(unittest.TestCase):
    def setUp(self):
        self.lexer = Lexer()
        self.parser = Parser()
        clear_errors()

    def semantic(self, code):
        tokens = self.lexer.tokenize(code)
        ast = self.parser.parse(tokens)
        return Check.checker(ast)

    def assertError(self, code, expected_error):
        self.semantic(code)
        self.assertTrue(errors_detected())
        self.assertTrue(has_error(expected_error))

    def test_print_undefined_variable(self):
        code = """
        main: function void() = {
            print x;
        }
        """
        self.assertError(code, SemanticError.UNDECLARED_VARIABLE)

    def test_print_void_literal(self):
        code = """
        main: function void() = {
            print void;
        }
        """
        # self.assertError(code, SemanticError.CANNOT_PRINT_VOID)

        # syntax error
        self.assertError(code, ParserError.UNEXPECTED_TOKEN)

    def test_print_void_function_call(self):
        code = """
        doSomething: function void() = {
            return;
        }

        main: function void() = {
            print doSomething;
        }
        """
        self.assertError(code, SemanticError.PRINT_VOID_EXPRESSION)

    def test_print_array_variable(self):
        code = """
        arr: array [3] integer = {1, 2, 3};

        main: function void() = {
            print arr;
        }
        """
        self.assertError(code, SemanticError.PRINT_ARRAY_NOT_ALLOWED)

    def test_print_array_literal_direct(self):
        code = """
        main: function void() = {
            print {1, 2, 3};
        }
        """
        # syntax error no lo permite la gramática
        # self.assertError(code, SemanticError.PRINT_ARRAY_NOT_ALLOWED)
        self.assertError(code, ParserError.INVALID_STATEMENT)
