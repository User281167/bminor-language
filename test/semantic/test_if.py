import unittest
from parser import Parser
from parser.model import *

from scanner import Lexer
from semantic.checker import Check
from utils import errors_detected
from utils.errors import clear_errors


class TestIf(unittest.TestCase):
    def setUp(self):
        self.lexer = Lexer()
        self.parser = Parser()
        clear_errors()

    def semantic(self, code):
        tokens = self.lexer.tokenize(code)
        ast = self.parser.parse(tokens)
        return Check.checker(ast)

    def assertPrintValid(self, code):
        env = self.semantic(code)
        self.assertFalse(errors_detected())

    def test_if_with_boolean_literal(self):
        code = """
        main: function void () = {
            if (true) print;
        }
        """
        self.assertPrintValid(code)

    def test_if_with_boolean_variable(self):
        code = """
        main: function void () = {
            flag: boolean = true;
            if (flag) print;
        }
        """
        self.assertPrintValid(code)

    def test_if_with_binary_boolean_expr(self):
        code = """
        main: function void () = {
            a: boolean = true;
            b: boolean = false;
            if (a && b) print;
        }
        """
        self.assertPrintValid(code)

    def test_if_with_unary_boolean_expr(self):
        code = """
        main: function void () = {
            a: boolean = false;
            if (!a) print;
        }
        """
        self.assertPrintValid(code)

    def test_if_with_comparison_expr(self):
        code = """
        main: function void () = {
            x: integer = 5;
            if (x < 10) print;
        }
        """
        self.assertPrintValid(code)

    def test_if_with_array_index_comparison(self):
        code = """
        main: function void () = {
            nums: array[5] integer = {1, 2, 3, 4, 5};
            if (nums[2] == 3) print;
        }
        """
        env = self.semantic(code)
        self.assertFalse(errors_detected())

    def test_if_with_function_call(self):
        code = """
        is_ready: function boolean () = {
            return true;
        }

        main: function void () = {
            if (is_ready()) print;
        }
        """
        env = self.semantic(code)
        self.assertFalse(errors_detected())

    def test_new_in_if_else(self):
        code = """
        main: function void() = {
            x: integer = 0;

            if (true) {
                x: integer = 10;
                print x;
            } else {
                x: integer = 20;
                print x;
            }

            print x;
        }
        """
        env = self.semantic(code)
        self.assertFalse(errors_detected())
