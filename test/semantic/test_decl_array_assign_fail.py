import unittest
from parser import Parser
from parser.model import *

from scanner import Lexer
from semantic.checker import Check, SemanticError
from utils import clear_errors, errors_detected, has_error


class TestArrayAssignmentErrors(unittest.TestCase):
    def setUp(self):
        self.lexer = Lexer()
        self.parser = Parser()
        clear_errors()

    def semantic(self, code):
        tokens = self.lexer.tokenize(code)
        ast = self.parser.parse(tokens)
        return Check.checker(ast)

    def assertArrayError(self, code, expected_error):
        self.semantic(code)
        self.assertTrue(errors_detected())
        self.assertTrue(has_error(expected_error))

    def assertSuccess(self, code):
        env = self.semantic(code)
        self.assertFalse(errors_detected())

    def test_index_float(self):
        code = """
        a: array [3] integer;

        main: function void() = {
            a[1.5] = 10;
        }
        """
        self.assertArrayError(code, SemanticError.ARRAY_INDEX_MUST_BE_INTEGER)

    def test_index_boolean(self):
        code = """
        a: array [3] integer;

        main: function void() = {
            a[true] = 10;
        }
        """
        self.assertArrayError(code, SemanticError.ARRAY_INDEX_MUST_BE_INTEGER)

    def test_index_string(self):
        code = """
        a: array [3] integer;

        main: function void() = {
            a["1"] = 10;
        }
        """
        self.assertArrayError(code, SemanticError.ARRAY_INDEX_MUST_BE_INTEGER)

    def test_index_char(self):
        code = """
        a: array [3] integer;

        main: function void() = {
            a['1'] = 10;
        }
        """
        self.assertArrayError(code, SemanticError.ARRAY_INDEX_MUST_BE_INTEGER)

    def test_index_array(self):
        code = """
        i: array [1] integer = {0};
        a: array [3] integer;

        main: function void() = {
            a[i] = 10;
        }
        """
        self.assertArrayError(code, SemanticError.ARRAY_INDEX_MUST_BE_INTEGER)

    def test_index_negative_literal(self):
        code = """
        a: array [3] integer;

        main: function void() = {
            a[-1] = 10;
        }
        """
        self.assertArrayError(code, SemanticError.INDEX_MUST_BE_POSITIVE)

    def test_index_negative_variable(self):
        # no podemos saber el valor ya que puede cambiar en tiempo de ejecución
        code = """
        i: integer = -1;
        a: array [3] integer;

        main: function void() = {
            a[i] = 10;
        }
        """
        # self.assertArrayError(code, SemanticError.INDEX_MUST_BE_POSITIVE)
        self.assertSuccess(code)

    def test_index_out_of_bounds_literal(self):
        code = """
        a: array [3] integer;

        main: function void() = {
            a[3] = 10;
        }
        """
        self.assertArrayError(code, SemanticError.INDEX_OUT_OF_BOUNDS)

    # no podemos saber el valor ya que puede cambiar en tiempo de ejecución
    # i = Otro valor; antes de llamar a[i];
    def test_index_out_of_bounds_variable(self):
        code = """
        i: integer = 5;
        a: array [3] integer;

        main: function void() = {
            a[i] = 10;
        }
        """
        # self.assertArrayError(code, SemanticError.INDEX_OUT_OF_BOUNDS)
        self.assertSuccess(code)

    def test_value_type_mismatch(self):
        code = """
        a: array [3] integer;

        main: function void() = {
            a[0] = false;
        }
        """
        self.assertArrayError(code, SemanticError.MISMATCH_ASSIGNMENT)

    def test_value_type_mismatch_string(self):
        code = """
        s: array [2] string;

        main: function void() = {
            s[1] = 42;
        }
        """
        self.assertArrayError(code, SemanticError.MISMATCH_ASSIGNMENT)
