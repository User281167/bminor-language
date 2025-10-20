import unittest
from parser import Parser
from parser.model import *

from scanner import Lexer
from semantic.checker import Check
from utils import errors_detected
from utils.errors import clear_errors


class TestScope(unittest.TestCase):
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

    def test_scope_inside_main(self):
        code = """
        main: function void() = {
            {
                x: integer = 5;
                print;
            }
        }
        """
        self.assertValid(code)

    def test_scope_inside_if(self):
        code = """
        main: function void() = {
            flag: boolean = true;
            if (flag) {
                {
                    x: integer = 10;
                    print;
                }
            }
        }
        """
        self.assertValid(code)

    def test_scope_variable_shadowing(self):
        code = """
        main: function void() = {
            x: integer = 1;
            {
                x: integer = 2;
                print;
            }
            print;
        }
        """
        self.assertValid(code)

    def test_nested_scopes(self):
        code = """
        main: function void() = {
            {
                x: integer = 5;
                {
                    y: integer = x + 1;
                    print;
                }
            }
        }
        """
        self.assertValid(code)

    def test_scope_access_parent_variable(self):
        code = """
        main: function void() = {
            x: integer = 3;
            {
                y: integer = x + 2;
                print;
            }
        }
        """
        self.assertValid(code)

    def test_scope_multiple_declarations(self):
        code = """
        main: function void() = {
            {
                a: integer = 1;
                b: boolean = true;
                c: float = 3.14;
                print;
            }
        }
        """
        self.assertValid(code)
