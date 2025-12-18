import unittest
from parser import Parser
from parser.model import *

from scanner import Lexer
from semantic.checker import Check, SemanticError
from utils import clear_errors, errors_detected, has_error


class TestArrayLocErrors(unittest.TestCase):
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

    def assertSuccess(self, code):
        env = self.semantic(code)
        self.assertFalse(errors_detected())

    def test_index_out_of_bounds(self):
        code = """
        my_arr: array [10] boolean;
        a: boolean = my_arr[100];
        """
        self.assertError(code, SemanticError.INDEX_OUT_OF_BOUNDS)

    def test_index_negative_literal(self):
        code = """
        my_arr: array [10] boolean;
        a: boolean = my_arr[-1];
        """
        self.assertError(code, SemanticError.INDEX_MUST_BE_POSITIVE)

    def test_array_not_declared(self):
        code = """
        a: boolean = my_arr[0];
        """
        self.assertError(code, SemanticError.UNDECLARED_ARRAY)

    def test_index_negative_from_variable(self):
        # No podemos saber el valor de x que puede cambiar en tiempo de ejecución antes de llegar a array[x]
        code = """
        N: integer = 10;
        my_arr: array [N] boolean;
        x: integer = -1;
        a: boolean = my_arr[x];
        """
        # self.assertError(code, SemanticError.INDEX_MUST_BE_POSITIVE)
        self.assertSuccess(code)

    def test_index_float(self):
        code = """
        my_arr: array [10] boolean;
        a: boolean = my_arr[10.3];
        """
        self.assertError(code, SemanticError.ARRAY_INDEX_MUST_BE_INTEGER)

    def test_index_is_array(self):
        code = """
        x: array [2] integer;
        my_arr: array [10] boolean;
        a: boolean = my_arr[x];
        """
        self.assertError(code, SemanticError.ARRAY_INDEX_MUST_BE_INTEGER)

    def test_index_is_char(self):
        code = """
        my_arr: array [5] boolean;
        a: boolean = my_arr['c'];
        """
        self.assertError(code, SemanticError.ARRAY_INDEX_MUST_BE_INTEGER)

    def test_index_is_string(self):
        code = """
        my_arr: array [5] boolean;
        a: boolean = my_arr["hello"];
        """
        self.assertError(code, SemanticError.ARRAY_INDEX_MUST_BE_INTEGER)

    def test_index_is_boolean(self):
        code = """
        my_arr: array [5] boolean;
        a: boolean = my_arr[true];
        """
        self.assertError(code, SemanticError.ARRAY_INDEX_MUST_BE_INTEGER)

    def test_index_negative_unary_expression(self):
        code = """
        my_arr: array [10] boolean;
        a: boolean = my_arr[-3];
        """
        self.assertError(code, SemanticError.INDEX_MUST_BE_POSITIVE)

    def test_index_out_of_bounds_exact(self):
        code = """
        my_arr: array [3] boolean;
        a: boolean = my_arr[3];
        """
        self.assertError(code, SemanticError.INDEX_OUT_OF_BOUNDS)
