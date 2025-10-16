import unittest
from parser import Parser
from scanner import Lexer
from parser.model import *
from semantic.checker import Check, SemanticError
from utils import error, errors_detected, clear_errors, has_error


class TestAssignmentBinaryError(unittest.TestCase):
    def setUp(self):
        self.lexer = Lexer()
        self.parser = Parser()
        clear_errors()

    def semantic(self, code):
        tokens = self.lexer.tokenize(code)
        ast = self.parser.parse(tokens)
        return Check.checker(ast)

    def assertBinaryError(self, code):
        self.semantic(code)
        self.assertTrue(errors_detected())
        self.assertTrue(has_error(SemanticError.INVALID_BINARY_OP))

    def test_integer_plus_boolean(self):
        self.assertBinaryError("x: integer = 12 + false;")

    def test_float_minus_boolean(self):
        self.assertBinaryError("x: float = 3.5 - true;")

    def test_boolean_and_integer(self):
        self.assertBinaryError("x: boolean = true && 1;")

    def test_char_multiply_string(self):
        self.assertBinaryError("x: char = 'a' * \"hello\";")

    def test_string_plus_integer(self):
        self.assertBinaryError("x: string = \"hi\" + 5;")

    def test_integer_less_string(self):
        self.assertBinaryError("x: boolean = 10 < \"ten\";")

    def test_float_modulo_boolean(self):
        self.assertBinaryError("x: float = 5.5 % true;")

    def test_boolean_equal_char(self):
        self.assertBinaryError("x: boolean = false == 'f';")

    def test_char_less_float(self):
        self.assertBinaryError("x: boolean = 'x' < 3.14;")

    def test_string_equal_boolean(self):
        self.assertBinaryError("x: boolean = \"yes\" == true;")
