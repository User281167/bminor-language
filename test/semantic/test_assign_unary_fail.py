import unittest
from parser import Parser
from parser.model import *

from scanner import Lexer
from semantic.checker import Check, SemanticError
from utils import clear_errors, error, errors_detected, has_error


class TestAssignmentUnaryError(unittest.TestCase):
    def setUp(self):
        self.lexer = Lexer()
        self.parser = Parser()
        clear_errors()

    def semantic(self, code):
        tokens = self.lexer.tokenize(code)
        ast = self.parser.parse(tokens)
        return Check.checker(ast)

    def assertUnaryError(self, code):
        self.semantic(code)
        self.assertTrue(errors_detected())
        self.assertTrue(has_error(SemanticError.INVALID_UNARY_OP))

    def test_plus_boolean(self):
        self.assertUnaryError("x: boolean = +false;")

    def test_minus_boolean(self):
        self.assertUnaryError("x: boolean = -true;")

    def test_not_integer(self):
        self.assertUnaryError("x: integer = !42;")

    def test_not_float(self):
        self.assertUnaryError("x: float = !3.14;")

    def test_plus_char(self):
        self.assertUnaryError("x: char = +'a';")

    def test_minus_char(self):
        self.assertUnaryError("x: char = -'z';")

    def test_not_char(self):
        self.assertUnaryError("x: char = !'x';")

    def test_plus_string(self):
        self.assertUnaryError('x: string = +"hello";')

    def test_minus_string(self):
        self.assertUnaryError('x: string = -"world";')

    def test_not_string(self):
        self.assertUnaryError('x: string = !"nope";')
