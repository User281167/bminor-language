import unittest
from parser import Parser
from scanner import Lexer
from parser.model import *
from semantic.checker import Check, SemanticError
from utils import errors_detected, clear_errors, has_error


class TestAssignmentComparisonError(unittest.TestCase):
    def setUp(self):
        self.lexer = Lexer()
        self.parser = Parser()
        clear_errors()

    def semantic(self, code):
        tokens = self.lexer.tokenize(code)
        ast = self.parser.parse(tokens)
        return Check.checker(ast)

    def assertComparisonError(self, code):
        self.semantic(code)
        self.assertTrue(errors_detected())
        self.assertTrue(has_error(SemanticError.INVALID_BINARY_OP))

    def test_integer_less_boolean(self):
        self.assertComparisonError("x: boolean = 3 < false;")

    def test_integer_equal_boolean(self):
        self.assertComparisonError("x: boolean = 1 == true;")

    def test_float_greater_boolean(self):
        self.assertComparisonError("x: boolean = 2.5 > false;")

    def test_boolean_less_integer(self):
        self.assertComparisonError("x: boolean = true < 5;")

    def test_boolean_equal_float(self):
        self.assertComparisonError("x: boolean = false == 3.14;")

    def test_boolean_and_integer(self):
        self.assertComparisonError("x: boolean = true && 1;")

    def test_boolean_or_float(self):
        self.assertComparisonError("x: boolean = false || 0.0;")

    def test_boolean_equal_char(self):
        self.assertComparisonError("x: boolean = true == 't';")

    def test_boolean_equal_string(self):
        self.assertComparisonError('x: boolean = false == "false";')

    def test_boolean_and_string(self):
        self.assertComparisonError('x: boolean = true && "yes";')
