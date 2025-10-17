import unittest
from parser import Parser
from parser.model import *

from scanner import Lexer
from semantic.checker import Check, SemanticError
from utils import clear_errors, errors_detected, has_error


class TestComplexBinaryErrors(unittest.TestCase):
    def setUp(self):
        self.lexer = Lexer()
        self.parser = Parser()
        clear_errors()

    def semantic(self, code):
        tokens = self.lexer.tokenize(code)
        ast = self.parser.parse(tokens)
        return Check.checker(ast)

    def assertComplexError(self, code):
        self.semantic(code)
        self.assertTrue(errors_detected())
        self.assertTrue(has_error(SemanticError.INVALID_BINARY_OP))

    def test_mixed_logic_and_integer(self):
        code = "x: boolean = (true || false) && 1;"
        self.assertComplexError(code)

    def test_comparison_and_string(self):
        code = 'x: boolean = (3 < 5) && "yes";'
        self.assertComplexError(code)

    def test_nested_invalid_logic(self):
        code = "x: boolean = (true && 2.0) || (false && 1);"
        self.assertComplexError(code)

    def test_invalid_comparison_chain(self):
        code = "x: boolean = (3.5 == 3.5) && (true < false);"
        self.assertComplexError(code)

    def test_invalid_logic_with_char(self):
        code = "x: boolean = (true || 'a') && false;"
        self.assertComplexError(code)

    def test_invalid_logic_with_float(self):
        code = "x: boolean = (1.0 == 1.0) && 0.0;"
        self.assertComplexError(code)

    def test_invalid_logic_with_mixed_types(self):
        code = "x: boolean = (3 == 3) && (false || 1);"
        self.assertComplexError(code)

    def test_invalid_logic_with_string_comparison(self):
        code = 'x: boolean = (true && false) && ("hi" == true);'
        self.assertComplexError(code)

    def test_invalid_logic_with_modulo(self):
        code = "x: boolean = (10 % 3) && true;"
        self.assertComplexError(code)

    def test_invalid_logic_with_nested_comparison(self):
        code = "x: boolean = ((1 + 2) < true) && (false || true);"
        self.assertComplexError(code)
