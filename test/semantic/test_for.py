import unittest
from parser import Parser
from parser.model import *

from scanner import Lexer
from semantic.checker import Check
from utils import errors_detected
from utils.errors import clear_errors


class TestFor(unittest.TestCase):
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

    def test_for(self):
        code = """
        main: function void () = {
            i: integer;
            for (i = 0; i < 10; i = i + 1) print;
        }
        """
        self.assertValid(code)

    def test_for2(self):
        code = """
        main: function void () = {
            i: array [2] integer;
            for (;;) print;
        }
        """
        self.assertValid(code)

    def test_for_with_empty_condition(self):
        code = """
        main: function void () = {
            i: integer;
            for (i = 0;; i = i + 1) print;
        }
        """
        self.assertValid(code)

    def test_for_with_empty_update(self):
        code = """
        main: function void () = {
            i: integer;
            for (i = 0; i < 10;) print;
        }
        """
        self.assertValid(code)

    def test_for_with_empty_init(self):
        code = """
        main: function void () = {
            i: integer = 0;
            for (; i < 10; i = i + 1) print;
        }
        """
        self.assertValid(code)

    def test_for_with_block_body(self):
        code = """
        main: function void () = {
            i: integer;
            for (i = 0; i < 3; i = i + 1) {
                print;
                print;
            }
        }
        """
        self.assertValid(code)

    def test_for_with_nested_for(self):
        code = """
        main: function void () = {
            i: integer;
            j: integer;
            for (i = 0; i < 2; i = i + 1)
                for (j = 0; j < 2; j = j + 1)
                    print;
        }
        """
        self.assertValid(code)

    def test_for_with_boolean_condition(self):
        code = """
        main: function void () = {
            i: integer = 0;
            cond: boolean = true;
            for (; cond; i = i + 1) print;
        }
        """
        self.assertValid(code)
