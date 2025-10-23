import unittest
from parser import Parser
from parser.model import *

from scanner import Lexer
from semantic.checker import Check
from utils import errors_detected
from utils.errors import clear_errors


class TestIncDec(unittest.TestCase):
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

    def test_increment_integer_variable(self):
        code = """
        main: function void () = {
            x: integer = 0;
            x++;
        }
        """
        self.assertValid(code)

    def test_decrement_integer_variable(self):
        code = """
        main: function void () = {
            x: integer = ++10--;
            x--;
        }
        """
        self.assertValid(code)

    def test_increment_array_element(self):
        code = """
        main: function void () = {
            a: array [3] integer = {1, 2, 3};
            i: integer = 0;
            a[i]++;
        }
        """
        self.assertValid(code)

    def test_decrement_array_element(self):
        code = """
        main: function void () = {
            a: array [3] integer = {1, 2, 3};
            i: integer = 2;
            a[i]--;
        }
        """
        self.assertValid(code)

    def test_increment_result_of_function_call(self):
        code = """
        get_index: function integer () = {
            return 1;
        }

        main: function void () = {
            a: array [3] integer = {1, 2, 3};
            a[get_index()]++;
        }
        """
        self.assertValid(code)

    def test_decrement_result_of_function_call(self):
        code = """
        get_index: function integer () = {
            return 2;
        }

        main: function void () = {
            a: array [3] integer = {1, --2, ++3};
            a[get_index()]--;
        }
        """
        self.assertValid(code)
