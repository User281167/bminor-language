import unittest
from parser import Parser
from parser.model import *

from scanner import Lexer
from semantic.checker import Check
from utils import errors_detected
from utils.errors import clear_errors


class TestArrayParameterAssignment(unittest.TestCase):
    def setUp(self):
        self.lexer = Lexer()
        self.parser = Parser()
        clear_errors()

    def semantic(self, code):
        tokens = self.lexer.tokenize(code)
        ast = self.parser.parse(tokens)
        return Check.checker(ast)

    def assertArrayParamAssignment(self, code):
        env = self.semantic(code)
        self.assertFalse(errors_detected())

    def test_assign_direct_index(self):
        code = """
        main: function void(a: array [] integer) = {
            a[0] = 12;
        }
        """
        self.assertArrayParamAssignment(code)

    def test_assign_unary_index(self):
        code = """
        main: function void(a: array [] integer) = {
            a[+1] = 42;
        }
        """
        self.assertArrayParamAssignment(code)

    def test_assign_var_index(self):
        code = """
        i: integer = 2;

        main: function void(a: array [] integer) = {
            a[i] = 99;
        }
        """
        self.assertArrayParamAssignment(code)

    def test_assign_binary_index(self):
        code = """
        main: function void(a: array [] integer) = {
            a[1 + 1] = 77;
        }
        """
        self.assertArrayParamAssignment(code)

    def test_assign_nested_expr_index(self):
        code = """
        main: function void(a: array [] integer) = {
            a[(1 + 1) - 1] = 60;
        }
        """
        self.assertArrayParamAssignment(code)

    def test_assign_float_array_param(self):
        code = """
        main: function void(f: array [] float) = {
            f[1] = 3.14;
        }
        """
        self.assertArrayParamAssignment(code)

    def test_assign_char_array_param(self):
        code = """
        main: function void(c: array [] char) = {
            c[0] = 'z';
        }
        """
        self.assertArrayParamAssignment(code)

    def test_assign_boolean_array_param(self):
        code = """
        main: function void(b: array [] boolean) = {
            b[1] = false;
        }
        """
        self.assertArrayParamAssignment(code)

    def test_assign_string_array_param(self):
        code = """
        main: function void(s: array [] string) = {
            s[0] = "ok";
        }
        """
        self.assertArrayParamAssignment(code)
