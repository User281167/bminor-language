import unittest
from parser import Parser
from scanner import Lexer
from parser.model import *
from semantic.checker import Check, SemanticError
from utils import error, errors_detected, clear_errors, has_error


class TestArrayDeclarationErrors(unittest.TestCase):
    def setUp(self):
        self.lexer = Lexer()
        self.parser = Parser()
        clear_errors()

    def semantic(self, code):
        tokens = self.lexer.tokenize(code)
        ast = self.parser.parse(tokens)
        return Check.checker(ast)

    def assertArrayError(self, code, expected_error):
        self.semantic(code)
        self.assertTrue(errors_detected())
        self.assertTrue(has_error(expected_error))

    def test_multi_dimensional_array(self):
        code = "x: array [1] array [2] integer;"
        self.assertArrayError(code, SemanticError.MULTI_DIMENSIONAL_ARRAYS)

    def test_array_size_float(self):
        code = "x: array [3.5] integer = {1, 2, 3};"
        self.assertArrayError(code, SemanticError.ARRAY_SIZE_MUST_BE_INTEGER)

    def test_array_size_string(self):
        code = 'x: array ["3"] integer = {1, 2, 3};'
        self.assertArrayError(code, SemanticError.ARRAY_SIZE_MUST_BE_INTEGER)

    def test_array_size_char(self):
        code = "x: array ['3'] integer = {1, 2, 3};"
        self.assertArrayError(code, SemanticError.ARRAY_SIZE_MUST_BE_INTEGER)

    def test_array_size_variable_wrong_type(self):
        code = "a: float = 3.0; x: array [a] integer = {1, 2, 3};"
        self.assertArrayError(code, SemanticError.ARRAY_SIZE_MUST_BE_INTEGER)

    def test_array_size_negative_literal(self):
        code = "x: array [-3] integer = {1, 2, 3};"
        self.assertArrayError(code, SemanticError.ARRAY_SIZE_MUST_BE_POSITIVE)

    def test_array_size_negative_unary(self):
        code = "x: array [-3] integer = {1, 2, 3};"
        self.assertArrayError(code, SemanticError.ARRAY_SIZE_MUST_BE_POSITIVE)

    def test_array_size_negative_variable(self):
        code = "a: integer = -3; x: array [a] integer = {1, 2, 3};"
        self.assertArrayError(code, SemanticError.ARRAY_SIZE_MUST_BE_POSITIVE)

    def test_array_size_mismatch_literal(self):
        code = "x: array [2] integer = {1, 2, 3};"
        self.assertArrayError(code, SemanticError.ARRAY_SIZE_MISMATCH)

    def test_array_size_mismatch_variable(self):
        code = "a: integer = 2; x: array [a] integer = {1, 2, 3};"
        self.assertArrayError(code, SemanticError.ARRAY_SIZE_MISMATCH)

    def test_array_type_mismatch(self):
        code = "x: array [3] integer = {1, true, 3};"
        self.assertArrayError(code, SemanticError.MISMATCH_ARRAY_ASSIGNMENT)

    def test_array_type_mismatch_string(self):
        code = 'x: array [2] string = {"hello", 42};'
        self.assertArrayError(code, SemanticError.MISMATCH_ARRAY_ASSIGNMENT)

    def test_array_type_mismatch_string(self):
        code = 'x: array [false] string = {"hello", 42};'
        self.assertArrayError(code, SemanticError.ARRAY_SIZE_MUST_BE_INTEGER)

    def test_array_type_mismatch_string(self):
        code = 'x: array [true] string = {"hello", 42};'
        self.assertArrayError(code, SemanticError.ARRAY_SIZE_MUST_BE_INTEGER)

    def test_array_size_array(self):
        code = "a: array [3] integer = {1, 2, 3}; x: array [a] integer;"
        self.assertArrayError(code, SemanticError.ARRAY_SIZE_MUST_BE_INTEGER)
