import unittest
from parser import Parser
from parser.model import *

from scanner import Lexer
from semantic.checker import Check
from utils import errors_detected
from utils.errors import clear_errors


class TestArrayElementAssignment(unittest.TestCase):
    def setUp(self):
        self.lexer = Lexer()
        self.parser = Parser()
        clear_errors()

    def semantic(self, code):
        tokens = self.lexer.tokenize(code)
        ast = self.parser.parse(tokens)
        return Check.checker(ast)

    def assertArrayAssignment(self, code):
        env = self.semantic(code)
        self.assertFalse(errors_detected())

    def test_assign_integer_direct(self):
        code = """
        a: array [3] integer;

        main: function void() = {
            a[0] = 12;
        }
        """
        self.assertArrayAssignment(code)

    def test_assign_integer_unary_index(self):
        code = """
        a: array [3] integer;

        main: function void() = {
            a[+1] = 42;
        }
        """
        self.assertArrayAssignment(code)

    def test_assign_integer_var_index(self):
        code = """
        i: integer = 2;
        a: array [3] integer;

        main: function void() = {
            a[i] = 99;
        }
        """
        self.assertArrayAssignment(code)

    def test_assign_integer_binary_index(self):
        code = """
        a: array [3] integer;

        main: function void() = {
            a[1 + 1] = 77;
        }
        """
        self.assertArrayAssignment(code)

    def test_assign_float_array(self):
        code = """
        f: array [2] float;

        main: function void() = {
            f[1] = 3.14;
        }
        """
        self.assertArrayAssignment(code)

    def test_assign_char_array(self):
        code = """
        c: array [2] char;

        main: function void() = {
            c[0] = 'z';
        }
        """
        self.assertArrayAssignment(code)

    def test_assign_boolean_array(self):
        code = """
        b: array [2] boolean;

        main: function void() = {
            b[1] = false;
        }
        """
        self.assertArrayAssignment(code)

    def test_assign_string_array(self):
        code = """
        s: array [2] string;

        main: function void() = {
            s[0] = "ok";
        }
        """
        self.assertArrayAssignment(code)

    def test_assign_integer_nested_expr(self):
        code = """
        a: array [3] integer;

        main: function void() = {
            a[(1 + 1) - 1] = 60;
        }
        """
        self.assertArrayAssignment(code)
