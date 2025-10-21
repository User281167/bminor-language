import unittest
from parser import Parser
from parser.model import *

from scanner import Lexer
from semantic import Check, SemanticError
from utils import clear_errors, errors_detected, has_error


class TestScopeError(unittest.TestCase):
    def setUp(self):
        self.lexer = Lexer()
        self.parser = Parser()
        clear_errors()

    def semantic(self, code):
        tokens = self.lexer.tokenize(code)
        ast = self.parser.parse(tokens)
        return Check.checker(ast)

    def assertError(self, code, expected_error):
        self.semantic(code)
        self.assertTrue(errors_detected())
        self.assertTrue(has_error(expected_error))

    def test_scope_undeclared(self):
        code = """
        main: function void() = {
            {
                x: integer = 5;
                print;
            }

            print x;
        }
        """
        self.assertError(code, SemanticError.UNDECLARED_VARIABLE)

    def test_scope_undeclared_in_if(self):
        code = """
        main: function void() = {
            if (true) {
                x: integer = 5;
                print;
            }

            print x;
        }
        """
        self.assertError(code, SemanticError.UNDECLARED_VARIABLE)

    def test_scope_undeclared_in_while(self):
        code = """
        main: function void() = {
            while (true) {
                x: integer = 5;
                print;
            }

            print x;
        }
        """
        self.assertError(code, SemanticError.UNDECLARED_VARIABLE)

    def test_scope_undeclared_in_for(self):
        code = """
        main: function void() = {
            for (; true; ) {
                x: integer = 5;
                print;
            }

            print x;
        }
        """
        self.assertError(code, SemanticError.UNDECLARED_VARIABLE)

    def test_scope_undeclared_in_do_while(self):
        code = """
        main: function void() = {
            do {
                x: integer = 5;
                print;
            } while (true);

            print x;
        }
        """
        self.assertError(code, SemanticError.UNDECLARED_VARIABLE)

    def test_scope_func_inside_scope(self):
        code = """
        main: function void() = {
            {
                my_func: function void() = {
                    x: integer = 5;
                    print;
                }

                my_func();
            }

            my_func();
        }
        """
        self.assertError(code, SemanticError.UNDEFINED_FUNCTION)
