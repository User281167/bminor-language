import unittest
from parser import Parser
from parser.model import *

from scanner import Lexer
from semantic.checker import Check
from utils import errors_detected
from utils.errors import clear_errors


class TestScopeContinueBreal(unittest.TestCase):
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

    def test_break_inside_while_scope(self):
        code = """
        main: function void () = {
            while (true) {
                {
                    break;
                }
            }
        }
        """
        self.assertValid(code)

    def test_continue_inside_while_scope(self):
        code = """
        main: function void () = {
            while (true) {
                {
                    continue;
                }
            }
        }
        """
        self.assertValid(code)

    def test_break_inside_for_scope(self):
        code = """
        main: function void () = {
            i: integer = 0;
            for (i = 0; i < 10; i = i + 1) {
                {
                    break;
                }
            }
        }
        """
        self.assertValid(code)

    def test_continue_inside_for_scope(self):
        code = """
        main: function void () = {
            i: integer = 0;
            for (i = 0; i < 10; i = i + 1) {
                {
                    continue;
                }
            }
        }
        """
        self.assertValid(code)

    def test_break_inside_do_while_scope(self):
        code = """
        main: function void () = {
            do {
                {
                    if (true) break;
                }
            } while (true);
        }
        """
        self.assertValid(code)

    def test_continue_inside_do_while_scope(self):
        code = """
        main: function void () = {
            do {
                {
                    if (true) continue;
                }
            } while (true);
        }
        """
        self.assertValid(code)
