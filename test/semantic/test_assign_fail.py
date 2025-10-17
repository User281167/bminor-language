import unittest
from parser import Parser
from parser.model import *

from scanner import Lexer
from semantic.checker import Check, SemanticError
from utils import clear_errors, error, errors_detected, has_error


class TestAssignmentError(unittest.TestCase):
    def setUp(self):
        self.lexer = Lexer()
        self.parser = Parser()
        clear_errors()

    def semantic(self, code):
        tokens = self.lexer.tokenize(code)
        ast = self.parser.parse(tokens)
        return Check.checker(ast)

    def assertMismatch(self, code):
        self.semantic(code)
        self.assertTrue(errors_detected())
        self.assertTrue(has_error(SemanticError.MISMATCH_DECLARATION))

    def test_integer_from_float(self):
        self.assertMismatch("x: integer = 42.2;")

    def test_float_from_integer_string(self):
        self.assertMismatch('pi: float = "3.14";')

    def test_string_from_char(self):
        self.assertMismatch("msg: string = 'a';")

    def test_char_from_string(self):
        self.assertMismatch('letter: char = "a";')

    def test_boolean_from_integer(self):
        self.assertMismatch("flag: boolean = 1;")

    def test_integer_from_boolean(self):
        self.assertMismatch("num: integer = true;")

    def test_float_from_boolean(self):
        self.assertMismatch("f: float = false;")

    def test_char_from_integer(self):
        self.assertMismatch("c: char = 65;")

    def test_string_from_boolean(self):
        self.assertMismatch("s: string = true;")

    def test_boolean_from_string(self):
        self.assertMismatch('ok: boolean = "true";')
