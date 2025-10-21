import unittest
from parser import Parser
from parser.model import *

from scanner import Lexer
from semantic.checker import Check
from utils import errors_detected
from utils.errors import clear_errors


class TestWhile(unittest.TestCase):
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

    def test_while(self):
        code = """
        main: function void () = {
            while (true) print;
        }
        """
        self.assertValid(code)

    def test_while_with_boolean_variable(self):
        code = """
        main: function void () = {
            cond: boolean = true;
            while (cond) print;
        }
        """
        self.assertValid(code)

    def test_while_with_boolean_expression(self):
        code = """
        main: function void () = {
            i: integer = 0;
            while (i < 5) {
                print;
                i = i + 1;
            }
        }
        """
        self.assertValid(code)

    def test_while_with_empty_body(self):
        code = """
        main: function void () = {
            while (true) {a: integer = 0;}
        }
        """
        self.assertValid(code)

    def test_while_with_nested_while(self):
        code = """
        main: function void () = {
            i: integer = 0;
            j: integer = 0;
            while (i < 2) {
                while (j < 2) {
                    print;
                    j = j + 1;
                }
                i = i + 1;
                j = 0;
            }
        }
        """
        self.assertValid(code)

    def test_while_with_complex_condition(self):
        code = """
        main: function void () = {
            a: integer = 0;
            b: integer = 10;
            while ((a < b) && (b > 0)) {
                print;
                a = a + 1;
                b = b - 1;
            }
        }
        """
        self.assertValid(code)

    def test_while_cond_array_index(self):
        code = """
        main: function void () = {
            a: array [2] boolean = {false, false};
            i: integer = 0;

            while (a[i]) {
                a[i] = true;
                i = i + 1;
            }
        }
        """
        self.assertValid(code)
