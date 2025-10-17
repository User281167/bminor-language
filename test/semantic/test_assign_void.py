import unittest
from parser import Parser
from scanner import Lexer
from parser.model import *
from semantic.checker import Check, SemanticError
from utils import error, errors_detected, clear_errors, has_error


class TestAssignmentVoid(unittest.TestCase):
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
        self.assertTrue(has_error(SemanticError.VOID_VARIABLE))

    def test_assign_void(self):
        self.assertMismatch("x: void;")

    def test_assign_integer_to_void(self):
        self.assertMismatch("x: void = 42;")

    def test_assign_string_to_void(self):
        self.assertMismatch('x: void = "hello";')

    def test_assign_void_array(self):
        code = "x: array [1] void;"
        self.semantic(code)
        self.assertTrue(errors_detected())
        self.assertTrue(has_error(SemanticError.VOID_ARRAY))

    def test_assign_void_array_values(self):
        code = "x: array [1] void = {43};"
        self.semantic(code)
        self.assertTrue(errors_detected())
        self.assertTrue(has_error(SemanticError.VOID_ARRAY))
