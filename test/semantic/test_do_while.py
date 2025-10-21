import unittest
from parser import Parser
from parser.model import *

from scanner import Lexer
from semantic.checker import Check
from utils import errors_detected
from utils.errors import clear_errors


class TestDoWhile(unittest.TestCase):
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

    def test_do_while(self):
        code = """
        main: function void () = {
            i: integer = 0;

            do {
                print;
                i = i + 1;
            } while (i < 5);
        }
        """
        self.assertValid(code)

    def test_do_while_with_boolean_variable(self):
        code = """
        main: function void () = {
            cond: boolean = true;
            do {
                print;
            } while (cond);
        }
        """
        self.assertValid(code)

    def test_do_while_with_boolean_literal(self):
        code = """
        main: function void () = {
            do {
                print;
            } while (true);
        }
        """
        self.assertValid(code)

    def test_do_while_with_relational_condition(self):
        code = """
        main: function void () = {
            i: integer = 0;
            do {
                print;
                i = i + 1;
            } while (i < 3);
        }
        """
        self.assertValid(code)

    def test_do_while_with_logical_expression(self):
        code = """
        main: function void () = {
            a: integer = 0;
            b: integer = 5;
            do {
                print;
                a = a + 1;
                b = b - 1;
            } while ((a < b) && (b > 0));
        }
        """
        self.assertValid(code)

    def test_do_while_with_nested_do_while(self):
        code = """
        main: function void () = {
            i: integer = 0;
            j: integer = 0;
            do {
                do {
                    print;
                    j = j + 1;
                } while (j < 2);
                i = i + 1;
                j = 0;
            } while (i < 2);
        }
        """
        self.assertValid(code)

    def test_do_while_cond_array_index(self):
        code = """
        main: function void () = {
            a: array [2] boolean = {false, false};
            i: integer = 0;

            do {
                a[i] = true;
                i = i + 1;
            } while (a[i]);
        }
        """
        self.assertValid(code)
