import unittest
from parser import Parser, ParserError
from parser.model import *

from scanner import Lexer
from semantic.checker import Check, SemanticError
from utils import clear_errors, errors_detected, has_error


class TestIfErrors(unittest.TestCase):
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

    def test_if_with_integer_literal_condition(self):
        code = """
        main: function void() = {
            if (1) print;
        }
        """
        self.assertError(code, SemanticError.IF_CONDITION_MUST_BE_BOOLEAN)

    def test_if_with_void_function_call(self):
        code = """
        do_nothing: function void () = {
            return;
        }

        main: function void() = {
            if (do_nothing()) print;
        }
        """
        self.assertError(code, SemanticError.IF_CONDITION_MUST_BE_BOOLEAN)

    def test_if_with_integer_variable_condition(self):
        code = """
        main: function void() = {
            x: integer = 5;
            if (x) print;
        }
        """
        self.assertError(code, SemanticError.IF_CONDITION_MUST_BE_BOOLEAN)

    def test_if_with_array_as_condition(self):
        code = """
        main: function void() = {
            a: array[3] integer = {1, 2, 3};
            if (a) print;
        }
        """
        self.assertError(code, SemanticError.IF_CONDITION_MUST_BE_BOOLEAN)

    def test_if_with_array_index_non_boolean(self):
        code = """
        main: function void() = {
            a: array[3] integer = {1, 2, 3};
            if (a[0]) print;
        }
        """
        self.assertError(code, SemanticError.IF_CONDITION_MUST_BE_BOOLEAN)

    def test_if_with_arithmetic_expression(self):
        code = """
        main: function void() = {
            x: integer = 1;
            y: integer = 2;
            if (x + y) print;
        }
        """
        self.assertError(code, SemanticError.IF_CONDITION_MUST_BE_BOOLEAN)

    def test_if_with_invalid_comparison(self):
        code = """
        main: function void() = {
            x: integer = 1;
            y: boolean = true;
            if (x < y) print;
        }
        """
        self.assertError(code, SemanticError.IF_CONDITION_MUST_BE_BOOLEAN)
