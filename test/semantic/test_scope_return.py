import unittest
from parser import Parser
from parser.model import *

from scanner import Lexer
from semantic.checker import Check
from utils import errors_detected
from utils.errors import clear_errors


class TestScopeReturn(unittest.TestCase):
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

    def test_return_inside_fun_if(self):
        code = """
        get_value: function integer() = {
            if (true) {
                return 42;
            }
        }
        """
        env = self.semantic(code)
        func = env.get("get_value")
        self.assertFalse(errors_detected())

    def test_return_inside_fun_while(self):
        code = """
        get_value: function integer() = {
            while (true) {
                return 42;
            }
        }
        """
        env = self.semantic(code)
        func = env.get("get_value")
        self.assertFalse(errors_detected())

    def test_return_inside_fun_for(self):
        code = """
        get_value: function integer() = {
            i: integer;

            for (i = 0; i < 10; i = i + 1) {
                return 42;
            }
        }
        """
        env = self.semantic(code)
        func = env.get("get_value")
        self.assertFalse(errors_detected())

    def test_return_inside_fun_block(self):
        code = """
        get_value: function integer() = {
            {
                return 42;
            }
        }
        """
        env = self.semantic(code)
        func = env.get("get_value")
        self.assertFalse(errors_detected())

    def test_return_inside_fun_block_nested(self):
        code = """
        get_value: function integer() = {
            {
                {
                    return 42;
                }
            }
        }
        """
        env = self.semantic(code)
        func = env.get("get_value")
        self.assertFalse(errors_detected())
