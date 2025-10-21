import unittest
from parser import Parser
from parser.model import *

from scanner import Lexer
from semantic import Check, SemanticError
from utils import clear_errors, errors_detected, has_error


class TestWhileError(unittest.TestCase):
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

    def test_while_with_integer_condition(self):
        code = """
        main: function void () = {
            i: integer = 1;
            while (i) print;
        }
        """
        self.assertError(code, SemanticError.LOOP_CONDITION_MUST_BE_BOOLEAN)

    def test_while_with_float_condition(self):
        code = """
        main: function void () = {
            f: float = 3.14;
            while (f) print;
        }
        """
        self.assertError(code, SemanticError.LOOP_CONDITION_MUST_BE_BOOLEAN)

    def test_while_with_string_condition(self):
        code = """
        main: function void () = {
            s: string = "loop";
            while (s) print;
        }
        """
        self.assertError(code, SemanticError.LOOP_CONDITION_MUST_BE_BOOLEAN)

    def test_while_with_char_condition(self):
        code = """
        main: function void () = {
            c: char = 'a';
            while (c) print;
        }
        """
        self.assertError(code, SemanticError.LOOP_CONDITION_MUST_BE_BOOLEAN)

    def test_while_with_array_condition(self):
        code = """
        main: function void () = {
            a: array [3] integer;
            while (a) print;
        }
        """
        self.assertError(code, SemanticError.LOOP_CONDITION_MUST_BE_BOOLEAN)
