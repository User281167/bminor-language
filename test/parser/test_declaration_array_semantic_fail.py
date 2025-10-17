import unittest
from parser import Parser
from parser.model import *

from scanner import Lexer
from utils.errors import clear_errors, errors_detected


class TestArrayPassingSemanticErrors(unittest.TestCase):
    # ========== VALID PARSER CASES (SEMANTIC ERRORS SHOULD BE ACCEPTED BY PARSER) ==========
    def setUp(self):
        self.lexer = Lexer()
        self.parser = Parser()
        clear_errors

    def parse(self, code):
        tokens = self.lexer.tokenize(code)
        return self.parser.parse(tokens)

    def test_integer_array_with_float_values_parser_accepts(self):
        # Parser should accept this - semantic analysis comes later
        code = "a: array [3] integer = {1, 2.5, 3};"
        ast = self.parse(code)
        self.assertIsInstance(ast.body[0], ArrayDecl)
        self.assertEqual(ast.body[0].name, "a")

    def test_float_array_with_string_values_parser_accepts(self):
        # Parser should accept this - semantic analysis comes later
        code = 'f: array [2] float = {1.0, "hello"};'
        ast = self.parse(code)
        self.assertIsInstance(ast.body[0], ArrayDecl)
        self.assertEqual(ast.body[0].name, "f")

    def test_char_array_with_string_values_parser_accepts(self):
        # Parser should accept this - semantic analysis comes later
        code = 'c: array [2] char = {"a", "b"};'
        ast = self.parse(code)
        self.assertIsInstance(ast.body[0], ArrayDecl)
        self.assertEqual(ast.body[0].name, "c")

    def test_boolean_array_with_integer_values_parser_accepts(self):
        # Parser should accept this - semantic analysis comes later
        code = "b: array [2] boolean = {true, 1};"
        ast = self.parse(code)
        self.assertIsInstance(ast.body[0], ArrayDecl)
        self.assertEqual(ast.body[0].name, "b")

    def test_string_array_with_char_values_parser_accepts(self):
        # Parser should accept this - semantic analysis comes later
        code = "s: array [2] string = {'a', 'b'};"
        ast = self.parse(code)
        self.assertIsInstance(ast.body[0], ArrayDecl)
        self.assertEqual(ast.body[0].name, "s")

    def test_array_size_mismatch_parser_accepts(self):
        # Parser should accept this - semantic analysis comes later
        code = "a: array [2] integer = {1, 2, 3};"
        ast = self.parse(code)
        self.assertIsInstance(ast.body[0], ArrayDecl)
        self.assertEqual(ast.body[0].name, "a")

    def test_array_with_few_elements_parser_accepts(self):
        # Parser should accept this - semantic analysis comes later
        code = "a: array [5] integer = {1, 2};"
        ast = self.parse(code)
        self.assertIsInstance(ast.body[0], ArrayDecl)
        self.assertEqual(ast.body[0].name, "a")

    # ========== INVALID ARRAY VALUES ==========

    def test_array_with_invalid_char_literal(self):
        code = "c: array [2] char = {'ab', 'c'};"
        self.parse(code)
        self.assertNotEqual(
            errors_detected(), 0, "Se esperaba error por literal char inválido"
        )

    def test_array_with_unterminated_string(self):
        code = 's: array [2] string = {"hello", "world;'
        self.parse(code)
        self.assertNotEqual(
            errors_detected(), 0, "Se esperaba error por string sin terminar"
        )

    def test_array_with_invalid_float_literal(self):
        code = "f: array [2] float = {1.2.3, 4.5};"
        self.parse(code)
        self.assertNotEqual(
            errors_detected(), 0, "Se esperaba error por literal float inválido"
        )

    # ========== ADDITIONAL PARSER SYNTAX ERRORS ==========

    def test_missing_array_type(self):
        code = "a: array [5] = {1, 2, 3};"
        self.parse(code)
        self.assertNotEqual(
            errors_detected(), 0, "Se esperaba error por falta de tipo de array"
        )

    def test_invalid_array_syntax_missing_brackets_around_size(self):
        code = "a: array 5 integer = {1, 2, 3};"
        self.parse(code)
        self.assertNotEqual(
            errors_detected(), 0, "Se esperaba error por sintaxis de array inválida"
        )

    def test_malformed_array_initialization_missing_opening_brace(self):
        code = "a: array [5] integer = 1, 2, 3};"
        self.parse(code)
        self.assertNotEqual(
            errors_detected(), 0, "Se esperaba error por llave de apertura faltante"
        )

    def test_malformed_array_initialization_missing_closing_brace(self):
        code = "a: array [5] integer = {1, 2, 3;"
        self.parse(code)
        self.assertNotEqual(
            errors_detected(), 0, "Se esperaba error por llave de cierre faltante"
        )

    def test_array_with_invalid_nested_structure(self):
        code = "a: array [2] integer = {1, {2, 3}};"
        self.parse(code)
        self.assertNotEqual(
            errors_detected(), 0, "Se esperaba error por estructura anidada inválida"
        )
