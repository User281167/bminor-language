import unittest
from parser import Parser
from parser.model import *

from scanner import Lexer
from semantic import Check
from utils import clear_errors, errors_detected


class TestContinueBreak(unittest.TestCase):
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

    def test_for_continue_break(self):
        code = """
        main: function void() = {
            i: integer;

            for (i = 0; i < 10; i = i + 1) {
                if (i == 5) {
                    break;
                }

                if (i == 7) {
                    continue;
                }

                print;
            }
        }
        """
        self.assertPrintValid(code)

    def test_while_continue_break(self):
        code = """
        main: function void() = {
            i: integer = 0;

            while (i < 10) {
                if (i == 5) {
                    break;
                }

                if (i == 7) {
                    continue;
                }

                print;
                i = i + 1;
            }
        }
        """
        self.assertPrintValid(code)

    def test_do_while_continue_break(self):
        code = """
        main: function void() = {
            i: integer = 0;

            do {
                if (i == 5) {
                    break;
                }

                if (i == 7) {
                    continue;
                }

                print;
                i = i + 1;
            } while (i < 10);
        }
        """
        self.assertPrintValid(code)
