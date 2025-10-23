import unittest
from parser import Parser
from parser.model import *

from scanner import Lexer
from semantic import Check, SemanticError
from utils import clear_errors, errors_detected, has_error


class TestFuncCallError(unittest.TestCase):
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

    def test_function_used_as_value_in_assignment(self):
        code = """
        main: function integer () = {
            i: integer;
            i = main;
        }
        """
        self.assertError(code, SemanticError.FUNCTION_USED_AS_VALUE)

    def test_function_used_as_value_in_unary_minus(self):
        code = """
        main: function integer () = {
            i: integer;
            i = -main;
        }
        """
        self.assertError(code, SemanticError.FUNCTION_USED_AS_VALUE)

    def test_function_used_as_value_in_decrement(self):
        code = """
        main: function integer () = {
            i: integer;
            --main;
        }
        """
        self.assertError(code, SemanticError.FUNCTION_USED_AS_VALUE)

    def test_function_used_as_value_in_increment(self):
        code = """
        main: function integer () = {
            i: integer;
            ++main;
        }
        """
        self.assertError(code, SemanticError.FUNCTION_USED_AS_VALUE)

    def test_function_used_as_value_in_binary_expression(self):
        code = """
        main: function integer () = {
            i: integer;
            j: integer = main + 1;
        }
        """
        self.assertError(code, SemanticError.FUNCTION_USED_AS_VALUE)

    def test_function_used_as_value_in_array_index(self):
        code = """
        main: function integer () = {
            a: array [5] integer;
            i: integer = a[main];
        }
        """
        self.assertError(code, SemanticError.FUNCTION_USED_AS_VALUE)
