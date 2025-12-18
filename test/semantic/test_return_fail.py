import unittest
from parser import Parser, ParserError
from parser.model import *

from scanner import Lexer
from semantic.checker import Check, SemanticError
from utils import clear_errors, errors_detected, has_error


class TestReturnErrors(unittest.TestCase):
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

    def test_return_outside_function(self):
        code = """
        return 42;
        """

        # la gramática no permite return fuera de declaraciones
        self.assertError(code, SemanticError.RETURN_OUT_OF_FUNCTION)

    def test_return_type_mismatch_integer_vs_float(self):
        code = """
        get_int: function integer() = {
            return 3.14;
        }
        """
        self.assertError(code, SemanticError.RETURN_TYPE_MISMATCH)

    def test_return_type_mismatch_boolean_vs_integer(self):
        code = """
        is_ready: function boolean() = {
            return 1 + 2;
        }
        """
        self.assertError(code, SemanticError.RETURN_TYPE_MISMATCH)

    def test_return_expression_in_void_function(self):
        code = """
        do_nothing: function void() = {
            return 42;
        }
        """
        self.assertError(code, SemanticError.RETURN_IN_VOID_FUNCTION)

    def test_return_variable_not_declared(self):
        code = """
        get_value: function integer() = {
            return x;
        }
        """
        self.assertError(code, SemanticError.UNDECLARED_VARIABLE)

    def test_return_wrong_expression_type(self):
        code = """
        get_char: function char() = {
            return "hello";
        }
        """
        self.assertError(code, SemanticError.RETURN_TYPE_MISMATCH)

    def test_return_array_index(self):
        code = """
        my_arr: array [3] integer;
        get_value: function integer() = {
            return my_arr[3];
        }
        """
        self.assertError(code, SemanticError.INDEX_OUT_OF_BOUNDS)

    def test_return_array_literal(self):
        code = """
        get_array: function array [3] integer() = {
            return {1, 2, 3}
        }
        """
        # self.assertError(code, SemanticError.RETURN_TYPE_NOT_SUPPORTED)

        # Syntax error la gramática no permite retornar un array literal
        self.assertError(code, ParserError.INVALID_STATEMENT)
