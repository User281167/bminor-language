import unittest
from parser import Parser
from parser.model import *

from scanner import Lexer
from semantic.checker import Check
from utils import errors_detected
from utils.errors import clear_errors


class TestPrintMultipleValid(unittest.TestCase):
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

    def test_print_multiple_literals(self):
        code = """
        main: function void() = {
            print 12, 'A';
        }
        """
        self.assertPrintValid(code)

    def test_print_variable_and_literal(self):
        code = """
        main: function void() = {
            x: integer = 12;
            print x, 'A';
        }
        """
        self.assertPrintValid(code)

    def test_print_function_call(self):
        code = """
        my_func: function integer() = {
            return 42;
        }

        main: function void() = {
            print my_func();
        }
        """
        self.assertPrintValid(code)

    def test_print_param(self):
        code = """
        main: function void(c: char) = {
            print c;
        }
        """
        self.assertPrintValid(code)

    def test_print_variable_multiple_and_literal_funcall(self):
        code = """
        my_func: function integer() = {
            return 42;
        }

        x: integer = 12;

        main: function void(c: char) = {
            y: integer = 12;
            print x, 12, 'A', c, my_func();
        }
        """
        self.assertPrintValid(code)
