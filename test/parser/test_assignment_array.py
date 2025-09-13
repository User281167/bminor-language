from errors import errors_detected, clear_errors
import unittest
from parser import Parser
from scanner import Lexer
from model import *
from errors import errors_detected


class TestAssignmentArray(unittest.TestCase):
    def setUp(self):
        self.lexer = Lexer()
        self.parser = Parser()
        clear_errors()

    def parse(self, code):
        tokens = self.lexer.tokenize(code)
        return self.parser.parse(tokens)

    # ========== BASIC DATA TYPES ARRAY ASSIGNMENTS ==========

    def test_integer_array_assignment(self):
        code = "a: array [3] integer = {1, 2, 3};"
        ast = self.parse(code)
        decl = ast.body[0]
        self.assertIsInstance(decl, ArrayDecl)
        self.assertEqual(decl.name, "a")
        self.assertIsInstance(decl.type, ArrayType)
        self.assertEqual(decl.type.base.name, "integer")
        self.assertIsInstance(decl.size, Integer)
        self.assertEqual(decl.size.value, 3)
        self.assertEqual(len(decl.value), 3)
        for i, val in enumerate(decl.value):
            self.assertIsInstance(val, Integer)
            self.assertEqual(val.value, i + 1)

    def test_float_array_assignment(self):
        code = "f: array [2] float = {3.14, 2.71};"
        ast = self.parse(code)
        decl = ast.body[0]
        self.assertIsInstance(decl, ArrayDecl)
        self.assertEqual(decl.name, "f")
        self.assertEqual(decl.type.base.name, "float")
        self.assertEqual(decl.size.value, 2)
        self.assertEqual(len(decl.value), 2)
        self.assertIsInstance(decl.value[0], Float)
        self.assertAlmostEqual(decl.value[0].value, 3.14, places=7)
        self.assertAlmostEqual(decl.value[1].value, 2.71, places=7)

    def test_char_array_assignment(self):
        code = "c: array [4] char = {'a', 'b', 'c', 'd'};"
        ast = self.parse(code)
        decl = ast.body[0]
        self.assertIsInstance(decl, ArrayDecl)
        self.assertEqual(decl.name, "c")
        self.assertEqual(decl.type.base.name, "char")
        self.assertEqual(decl.size.value, 4)
        self.assertEqual(len(decl.value), 4)
        expected_chars = ['a', 'b', 'c', 'd']
        for i, val in enumerate(decl.value):
            self.assertIsInstance(val, Char)
            self.assertEqual(val.value, expected_chars[i])

    def test_string_array_assignment(self):
        code = 's: array [2] string = {"hello", "world"};'
        ast = self.parse(code)
        decl = ast.body[0]
        self.assertIsInstance(decl, ArrayDecl)
        self.assertEqual(decl.name, "s")
        self.assertEqual(decl.type.base.name, "string")
        self.assertEqual(decl.size.value, 2)
        self.assertEqual(len(decl.value), 2)
        expected_strings = ["hello", "world"]
        for i, val in enumerate(decl.value):
            self.assertIsInstance(val, String)
            self.assertEqual(val.value, expected_strings[i])

    def test_boolean_array_assignment(self):
        code = "b: array [3] boolean = {true, false, true};"
        ast = self.parse(code)
        decl = ast.body[0]
        self.assertIsInstance(decl, ArrayDecl)
        self.assertEqual(decl.name, "b")
        self.assertEqual(decl.type.base.name, "boolean")
        self.assertEqual(decl.size.value, 3)
        self.assertEqual(decl.size.value, decl.type.size.value)
        self.assertEqual(len(decl.value), 3)
        expected_bools = [True, False, True]
        for i, val in enumerate(decl.value):
            self.assertIsInstance(val, Boolean)
            self.assertEqual(val.value, expected_bools[i])

    # ========== EMPTY ARRAY ASSIGNMENTS ==========

    def test_empty_integer_array(self):
        code = "a: array [5] integer = {};"
        ast = self.parse(code)
        decl = ast.body[0]
        self.assertIsInstance(decl, ArrayDecl)
        self.assertEqual(decl.name, "a")
        self.assertEqual(decl.type.base.name, "integer")
        self.assertEqual(decl.size.value, 5)
        self.assertEqual(decl.size.value, decl.type.size.value)
        self.assertEqual(len(decl.value), 0)  # Empty array

    def test_empty_float_array(self):
        code = "f: array [3] float = {};"
        ast = self.parse(code)
        decl = ast.body[0]
        self.assertIsInstance(decl, ArrayDecl)
        self.assertEqual(decl.name, "f")
        self.assertEqual(decl.type.base.name, "float")
        self.assertEqual(decl.size.value, 3)
        self.assertEqual(decl.size.value, decl.type.size.value)
        self.assertEqual(len(decl.value), 0)

    def test_empty_char_array(self):
        code = "c: array [10] char = {};"
        ast = self.parse(code)
        decl = ast.body[0]
        self.assertIsInstance(decl, ArrayDecl)
        self.assertEqual(decl.name, "c")
        self.assertEqual(decl.type.base.name, "char")
        self.assertEqual(decl.size.value, 10)
        self.assertEqual(decl.size.value, decl.type.size.value)
        self.assertEqual(len(decl.value), 0)

    def test_empty_string_array(self):
        code = 's: array [2] string = {};'
        ast = self.parse(code)
        decl = ast.body[0]
        self.assertIsInstance(decl, ArrayDecl)
        self.assertEqual(decl.name, "s")
        self.assertEqual(decl.type.base.name, "string")
        self.assertEqual(decl.size.value, 2)
        self.assertEqual(decl.size.value, decl.type.size.value)
        self.assertEqual(len(decl.value), 0)

    def test_empty_boolean_array(self):
        code = "b: array [1] boolean = {};"
        ast = self.parse(code)
        decl = ast.body[0]
        self.assertIsInstance(decl, ArrayDecl)
        self.assertEqual(decl.name, "b")
        self.assertEqual(decl.type.base.name, "boolean")
        self.assertEqual(decl.size.value, 1)
        self.assertEqual(decl.size.value, decl.type.size.value)
        self.assertEqual(len(decl.value), 0)

    def test_none_array(self):
        code = "b: array [1] boolean;"
        ast = self.parse(code)
        decl = ast.body[0]
        self.assertIsInstance(decl, ArrayDecl)
        self.assertEqual(decl.name, "b")
        self.assertEqual(decl.type.base.name, "boolean")
        self.assertEqual(decl.size.value, 1)
        self.assertEqual(decl.size.value, decl.type.size.value)
        self.assertEqual(decl.type.size, decl.size)
        self.assertEqual(len(decl.value), 0)

    def test_negative_size_array(self):
        code = "b: array [-1] boolean = {};"
        ast = self.parse(code)
        decl = ast.body[0]
        self.assertIsInstance(decl, ArrayDecl)
        self.assertEqual(decl.name, "b")
        self.assertEqual(decl.type.base.name, "boolean")
        self.assertIsInstance(decl.size, UnaryOper)
        self.assertEqual(decl.size.expr.value, 1)
        self.assertEqual(decl.size.oper, '-')
        self.assertEqual(decl.type.size, decl.size)

    # ========== FILLED ARRAY ASSIGNMENTS WITH VARIOUS SIZES ==========

    def test_single_element_array(self):
        code = "a: array [1] integer = {42};"
        ast = self.parse(code)
        decl = ast.body[0]
        self.assertIsInstance(decl, ArrayDecl)
        self.assertEqual(decl.size.value, 1)
        self.assertEqual(len(decl.value), 1)
        self.assertEqual(decl.value[0].value, 42)

    def test_large_array_assignment(self):
        code = "a: array [0] integer = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10};"
        ast = self.parse(code)
        decl = ast.body[0]
        self.assertIsInstance(decl, ArrayDecl)
        self.assertEqual(decl.size.value, 0)
        # se define como 0 pero se le asigna 10 elementos
        self.assertEqual(len(decl.value), 10)
        for i, val in enumerate(decl.value):
            self.assertEqual(val.value, i + 1)

    def test_mixed_float_array(self):
        code = "f: array [4] float = {1.0, 2.5, 3.14e2, 0.0e2, .5};"
        ast = self.parse(code)
        decl = ast.body[0]
        self.assertIsInstance(decl, ArrayDecl)
        self.assertEqual(decl.size.value, 4)
        self.assertEqual(len(decl.value), 5)
        expected_values = [1.0, 2.5, 3.14e2, 0.0e2, 0.5]
        for i, val in enumerate(decl.value):
            self.assertAlmostEqual(val.value, expected_values[i], places=7)

    def test_string_array_with_escapes(self):
        code = 's: array [3] string = {"hello\\n", "world\\t", "test\\\\"};'
        ast = self.parse(code)
        decl = ast.body[0]
        self.assertIsInstance(decl, ArrayDecl)
        self.assertEqual(decl.size.value, 3)
        self.assertEqual(len(decl.value), 3)
        expected_strings = ["hello\\n", "world\\t", "test\\\\"]
        for i, val in enumerate(decl.value):
            self.assertEqual(val.value, expected_strings[i])

    # ========== ARRAY DECLARATIONS WITHOUT INITIALIZATION ==========

    def test_integer_array_declaration_only(self):
        code = "a: array [5] integer;"
        ast = self.parse(code)
        decl = ast.body[0]
        self.assertIsInstance(decl, ArrayDecl)
        self.assertEqual(decl.name, "a")
        self.assertEqual(decl.type.base.name, "integer")
        self.assertEqual(decl.size.value, 5)
        self.assertEqual(len(decl.value), 0)  # No initialization


class TestAssignmentMultiDimensionalArray(unittest.TestCase):
    # ========== MULTIDIMENSIONAL ARRAYS ==========
    def setUp(self):
        self.lexer = Lexer()
        self.parser = Parser()
        clear_errors()

    def parse(self, code):
        tokens = self.lexer.tokenize(code)
        return self.parser.parse(tokens)

    def test_2d_integer_array_empty(self):
        code = "a: array [2] array [3] integer = {};"
        ast = self.parse(code)
        decl = ast.body[0]
        self.assertIsInstance(decl, ArrayDecl)
        self.assertEqual(decl.name, "a")
        self.assertIsInstance(decl.type, ArrayType)
        self.assertIsInstance(decl.type.base, ArrayType)
        self.assertEqual(decl.type.base.base.name, "integer")
        self.assertEqual(decl.size.value, 2)

    def test_2d_integer_array(self):
        code = "a: array [2] array [3] integer = {{1, 2, 3}, {4, 5, 6}};"
        ast = self.parse(code)

        # body []
        # no hay gramática que permite = {{}} o {{1, 2, 3}, {4, 5, 6}}
        self.assertEqual(len(ast.body), 0)
        self.assertNotEqual(errors_detected(), 0)

    def test_3d_float_array(self):
        code = "f: array [2] array [2] array [2] float = {};"
        ast = self.parse(code)
        decl = ast.body[0]
        self.assertIsInstance(decl, ArrayDecl)
        self.assertEqual(decl.name, "f")
        self.assertIsInstance(decl.type, ArrayType)
        self.assertIsInstance(decl.type.base, ArrayType)
        self.assertIsInstance(decl.type.base.base, ArrayType)
        self.assertEqual(decl.type.base.base.base.name, "float")

    # ========== MULTIDIMENSIONAL ARRAY PARSER ACCEPTS ==========

    def test_multidimensional_array_size_mismatch_parser_accepts(self):
        code = "a: array [2] array [3] integer = {{1, 2}, {3, 4, 5}};"
        ast = self.parse(code)
        # self.assertIsInstance(ast.body[0], ArrayDecl)
        # self.assertEqual(ast.body[0].name, "a")
        # no hay gramática que permita esto
        self.assertNotEqual(errors_detected(), 0)
        self.assertEqual(len(ast.body), 0)

    def test_multidimensional_array_type_mismatch_parser_accepts(self):
        code = "a: array [2] array [2] integer = {{1, 2}, {3.0, 4.0}};"
        ast = self.parse(code)
        # self.assertIsInstance(ast.body[0], ArrayDecl)
        # self.assertEqual(ast.body[0].name, "a")
        # no hay gramática que permita esto
        self.assertNotEqual(errors_detected(), 0)
        self.assertEqual(len(ast.body), 0)


class TestFailingCases(unittest.TestCase):
    def setUp(self):
        self.lexer = Lexer()
        self.parser = Parser()
        clear_errors

    def parse(self, code):
        clear_errors()
        tokens = self.lexer.tokenize(code)
        return self.parser.parse(tokens)

#     # ========== SYNTAX ERRORS ==========

    def test_missing_array_keyword(self):
        code = "a: [5] integer = {1, 2, 3};"
        self.parse(code)
        self.assertNotEqual(
            errors_detected(), 0, "Se esperaba error por falta de palabra clave 'array'")

    def test_missing_square_brackets(self):
        code = "a: array 5 integer = {1, 2, 3};"
        self.parse(code)
        self.assertNotEqual(errors_detected(), 0,
                            "Se esperaba error por falta de corchetes")

    def test_missing_size_in_brackets(self):
        code = "a: array [] integer = {1, 2, 3};"
        self.parse(code)
        self.assertNotEqual(
            errors_detected(), 0, "Se esperaba error por falta de tamaño en corchetes")

    def test_missing_equals_sign(self):
        code = "a: array [5] integer {1, 2, 3};"
        self.parse(code)
        self.assertNotEqual(errors_detected(), 0,
                            "Se esperaba error por falta de signo '='")

    def test_missing_curly_braces(self):
        code = "a: array [5] integer = 1, 2, 3;"
        self.parse(code)
        self.assertNotEqual(errors_detected(), 0,
                            "Se esperaba error por falta de llaves")

    def test_missing_semicolon(self):
        code = "a: array [5] integer = {1, 2, 3}"
        self.parse(code)
        self.assertNotEqual(errors_detected(), 0,
                            "Se esperaba error por falta de punto y coma")

    def test_array_with_missing_comma_separator(self):
        code = "a: array [3] integer = {1 2, 3};"
        self.parse(code)
        self.assertNotEqual(errors_detected(), 0,
                            "Se esperaba error por separador de coma faltante")

    def test_array_with_trailing_comma(self):
        code = "a: array [2] integer = {1, 2,};"
        self.parse(code)
        self.assertNotEqual(errors_detected(), 0,
                            "Se esperaba error por coma final")

    def test_array_with_extra_comma(self):
        code = "a: array [2] integer = {1, , 2};"
        self.parse(code)
        self.assertNotEqual(errors_detected(), 0,
                            "Se esperaba error por coma extra")


class TestPassingSemanticErrors(unittest.TestCase):
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
        self.assertNotEqual(errors_detected(), 0,
                            "Se esperaba error por literal char inválido")

    def test_array_with_unterminated_string(self):
        code = 's: array [2] string = {"hello", "world;'
        self.parse(code)
        self.assertNotEqual(errors_detected(), 0,
                            "Se esperaba error por string sin terminar")

    def test_array_with_invalid_float_literal(self):
        code = "f: array [2] float = {1.2.3, 4.5};"
        self.parse(code)
        self.assertNotEqual(errors_detected(), 0,
                            "Se esperaba error por literal float inválido")

    # ========== ADDITIONAL PARSER SYNTAX ERRORS ==========

    def test_missing_array_type(self):
        code = "a: array [5] = {1, 2, 3};"
        self.parse(code)
        self.assertNotEqual(errors_detected(), 0,
                            "Se esperaba error por falta de tipo de array")

    def test_invalid_array_syntax_missing_brackets_around_size(self):
        code = "a: array 5 integer = {1, 2, 3};"
        self.parse(code)
        self.assertNotEqual(errors_detected(), 0,
                            "Se esperaba error por sintaxis de array inválida")

    def test_malformed_array_initialization_missing_opening_brace(self):
        code = "a: array [5] integer = 1, 2, 3};"
        self.parse(code)
        self.assertNotEqual(errors_detected(), 0,
                            "Se esperaba error por llave de apertura faltante")

    def test_malformed_array_initialization_missing_closing_brace(self):
        code = "a: array [5] integer = {1, 2, 3;"
        self.parse(code)
        self.assertNotEqual(errors_detected(), 0,
                            "Se esperaba error por llave de cierre faltante")

    def test_array_with_invalid_nested_structure(self):
        code = "a: array [2] integer = {1, {2, 3}};"
        self.parse(code)
        self.assertNotEqual(errors_detected(), 0,
                            "Se esperaba error por estructura anidada inválida")
