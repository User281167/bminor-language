import unittest
from parser import Parser
from parser.model import *

from scanner import Lexer
from semantic.checker import Check, SemanticError
from utils import clear_errors, errors_detected, has_error


class TestIncDecError(unittest.TestCase):
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

    def test_increment_float(self):
        code = """
        main: function void () = {
            f: float = 3.14;
            f++;
        }
        """
        self.assertError(code, SemanticError.INVALID_INCREMENT)

    def test_increment_string(self):
        code = """
        main: function void () = {
            s: string = "hello";
            s++;
        }
        """
        self.assertError(code, SemanticError.INVALID_INCREMENT)

    def test_increment_char(self):
        code = """
        main: function void () = {
            c: char = 'a';
            c++;
        }
        """
        self.assertError(code, SemanticError.INVALID_INCREMENT)

    def test_increment_boolean(self):
        code = """
        main: function void () = {
            b: boolean = true;
            b++;
        }
        """
        self.assertError(code, SemanticError.INVALID_INCREMENT)

    def test_increment_array(self):
        code = """
        main: function void () = {
            a: array [3] integer = {1, 2, 3};
            a++;
        }
        """
        self.assertError(code, SemanticError.INVALID_INCREMENT)

    def test_decrement_float(self):
        code = """
        main: function void () = {
            f: float = 3.14;
            f--;
        }
        """
        self.assertError(code, SemanticError.INVALID_DECREMENT)

    def test_decrement_string(self):
        code = """
        main: function void () = {
            s: string = "hello";
            s--;
        }
        """
        self.assertError(code, SemanticError.INVALID_DECREMENT)

    def test_decrement_char(self):
        code = """
        main: function void () = {
            c: char = 'a';
            c--;
        }
        """
        self.assertError(code, SemanticError.INVALID_DECREMENT)

    def test_decrement_boolean(self):
        code = """
        main: function void () = {
            b: boolean = false;
            b--;
        }
        """
        self.assertError(code, SemanticError.INVALID_DECREMENT)

    def test_decrement_array(self):
        code = """
        main: function void () = {
            a: array [3] integer = {1, 2, 3};
            a--;
        }
        """
        self.assertError(code, SemanticError.INVALID_DECREMENT)
