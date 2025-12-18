import unittest
from parser import Parser
from parser.model import *

from scanner import Lexer
from semantic.checker import Check, SemanticError
from utils import clear_errors, errors_detected, has_error


class TestRecursiveArrayIndexEvaluation(unittest.TestCase):
    def setUp(self):
        self.lexer = Lexer()
        self.parser = Parser()
        clear_errors()

    def semantic(self, code):
        tokens = self.lexer.tokenize(code)
        ast = self.parser.parse(tokens)
        return Check.checker(ast)

    def assertNoError(self, code):
        env = self.semantic(code)
        self.assertFalse(errors_detected())

    def assertError(self, code, expected_error):
        self.semantic(code)
        self.assertTrue(errors_detected())
        self.assertTrue(has_error(expected_error))

    # ✅ Casos exitosos

    def test_index_with_variable_equal_to_size(self):
        code = """
        N: integer = 100;
        A: integer = N;
        isprime: array [A] boolean;

        main: function void(a: array[] integer) = {
            i: integer = 99;
            isprime[i] = false;
        }
        """
        self.assertNoError(code)

    def test_index_with_unary_expression(self):
        code = """
        N: integer = 100;
        isprime: array [N] boolean;

        main: function void(a: array[] integer) = {
            i: integer = +50;
            isprime[i] = false;
        }
        """
        self.assertNoError(code)

    def test_index_with_nested_variable(self):
        code = """
        N: integer = 100;
        A: integer = N;
        isprime: array [A] boolean;

        main: function void(a: array[] integer) = {
            i: integer = 10;
            j: integer = i;
            isprime[j] = false;
        }
        """
        self.assertNoError(code)

    # ❌ Casos con error

    def test_index_out_of_bounds_literal(self):
        # No sabemos el valor de N en otros casos puede cambiar antes de ejecutar array[N]
        code = """
        N: integer = 100;
        isprime: array [N] boolean;

        main: function void(a: array[] integer) = {
            isprime[120] = false;
        }
        """
        # self.assertError(code, SemanticError.INDEX_OUT_OF_BOUNDS)
        self.assertNoError(code)

    def test_index_out_of_bounds_variable(self):
        # A puede cambiar antes de ejecutar array[A]
        code = """
        N: integer = 100;
        A: integer = N;
        isprime: array [A] boolean;

        main: function void(a: array[] integer) = {
            i: integer = 120;
            j: integer = i;
            isprime[j] = false;
        }
        """
        # self.assertError(code, SemanticError.INDEX_OUT_OF_BOUNDS)
        self.assertNoError(code)

    def test_index_negative_literal(self):
        code = """
        N: integer = 100;
        isprime: array [N] boolean;

        main: function void(a: array[] integer) = {
            isprime[-1] = false;
        }
        """
        self.assertError(code, SemanticError.INDEX_MUST_BE_POSITIVE)

    def test_index_negative_variable(self):
        # No podemos saber el valor ya que puede cambiar en tiempo de ejecución
        code = """
        N: integer = 100;
        isprime: array [N] boolean;

        main: function void(a: array[] integer) = {
            i: integer = -90;
            isprime[i] = false;
        }
        """
        # self.assertError(code, SemanticError.INDEX_MUST_BE_POSITIVE)
        self.assertNoError(code)

    def test_index_negative_nested(self):
        # No sabemos el valor de arra[size] A y N pueden cambiar antes de ejecutar array[A]
        code = """
        N: integer = 100;
        A: integer = N;
        isprime: array [A] boolean;

        main: function void(a: array[] integer) = {
            i: integer = -120;
            j: integer = i;
            isprime[j] = false;
        }
        """
        # self.assertError(code, SemanticError.INDEX_MUST_BE_POSITIVE)
        self.assertNoError(code)
