import unittest
from parser import Parser
from parser.model import *

from scanner import Lexer
from semantic import Check, SemanticError
from utils import clear_errors, errors_detected, has_error


class TestScopeContinueBreal(unittest.TestCase):
    def setUp(self):
        self.lexer = Lexer()
        self.parser = Parser()
        clear_errors()

    def semantic(self, code):
        tokens = self.lexer.tokenize(code)
        ast = self.parser.parse(tokens)
        return Check.checker(ast)

    def assertValid(self, code):
        env = self.semantic(code)
        self.assertFalse(errors_detected())

    def assertError(self, code, expected_error):
        env = self.semantic(code)
        self.assertTrue(errors_detected())
        self.assertTrue(has_error(expected_error))

    def test_array_length_with_integer_literal(self):
        self.assertError(
            """
            fn: function void() = {
                x: integer;
                x = array_length(5);
            }
        """,
            SemanticError.MISMATCH_ARGUMENT_TYPE,
        )

    def test_array_length_with_variable_not_array(self):
        self.assertError(
            """
            fn: function void() = {
                x: integer;
                y: integer;
                x = array_length(y);
            }
        """,
            SemanticError.MISMATCH_ARGUMENT_TYPE,
        )

    def test_array_length_with_string_literal(self):
        self.assertError(
            """
            fn: function void() = {
                x: integer;
                x = array_length("hello");
            }
        """,
            SemanticError.MISMATCH_ARGUMENT_TYPE,
        )

    def test_array_length_with_no_arguments(self):
        self.assertError(
            """
            fn: function void() = {
                x: integer;
                x = array_length();
            }
        """,
            SemanticError.WRONG_NUMBER_OF_ARGUMENTS,
        )

    def test_array_length_with_two_arguments(self):
        self.assertError(
            """
            fn: function void() = {
                x: integer;
                a: array [3] integer;
                b: array [2] integer;
                x = array_length(a, b);
            }
        """,
            SemanticError.WRONG_NUMBER_OF_ARGUMENTS,
        )

    def test_array_length_with_array_variable(self):
        self.assertValid(
            """
            fn: function void() = {
                a: array [5] integer;
                x: integer;
                x = array_length(a);
            }
        """
        )

    def test_array_length_with_function_returning_array(self):
        self.assertValid(
            """
            get_data: function array [5] integer();

            main: function void() = {
                x: integer;
                x = array_length(get_data());
            }
        """
        )

    def test_array_length_with_var_array(self):
        self.assertValid(
            """
            arr: array [5] integer;

            main: function void() = {
                x: integer = array_length(arr);
            }
        """
        )
