import unittest
from parser import Parser
from parser.model import *

from scanner import Lexer
from semantic import Check, SemanticError
from utils import clear_errors, errors_detected, has_error


class TestScopeContinueBreakError(unittest.TestCase):
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

    def test_continue_outside_loop(self):
        code = """
        main: function void() = {
            continue;
        }
        """
        self.assertError(code, SemanticError.CONTINUE_OUT_OF_LOOP)

    def test_continue_inside_scope_only(self):
        code = """
        main: function void() = {
            {
                break;
            }
        }
        """
        self.assertError(code, SemanticError.BREAK_OUT_OF_LOOP)

    def test_continue_inside_if(self):
        code = """
        main: function void() = {
            if (true) {
                continue;
            }
        }
        """
        self.assertError(code, SemanticError.CONTINUE_OUT_OF_LOOP)

    def test_continue_inside_function_scope(self):
        code = """
        main: function void() = {
            {
                continue;
            }
        }
        """
        self.assertError(code, SemanticError.CONTINUE_OUT_OF_LOOP)
