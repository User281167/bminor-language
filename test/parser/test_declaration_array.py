import unittest
from parser import Parser
from parser.model import *

from scanner import Lexer
from utils.errors import clear_errors


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
        self.assertIsInstance(decl.type.size, Integer)
        self.assertEqual(decl.type.size.value, 3)
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
        self.assertEqual(decl.type.size.value, 2)
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
        self.assertEqual(decl.type.size.value, 4)
        self.assertEqual(len(decl.value), 4)
        expected_chars = ["a", "b", "c", "d"]
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
        self.assertEqual(decl.type.size.value, 2)
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
        self.assertEqual(decl.type.size.value, 3)
        self.assertEqual(decl.type.size.value, decl.type.size.value)
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
        self.assertEqual(decl.type.size.value, 5)
        self.assertEqual(decl.type.size.value, decl.type.size.value)
        self.assertEqual(len(decl.value), 0)  # Empty array

    def test_empty_float_array(self):
        code = "f: array [3] float = {};"
        ast = self.parse(code)
        decl = ast.body[0]
        self.assertIsInstance(decl, ArrayDecl)
        self.assertEqual(decl.name, "f")
        self.assertEqual(decl.type.base.name, "float")
        self.assertEqual(decl.type.size.value, 3)
        self.assertEqual(decl.type.size.value, decl.type.size.value)
        self.assertEqual(len(decl.value), 0)

    def test_empty_char_array(self):
        code = "c: array [10] char = {};"
        ast = self.parse(code)
        decl = ast.body[0]
        self.assertIsInstance(decl, ArrayDecl)
        self.assertEqual(decl.name, "c")
        self.assertEqual(decl.type.base.name, "char")
        self.assertEqual(decl.type.size.value, 10)
        self.assertEqual(decl.type.size.value, decl.type.size.value)
        self.assertEqual(len(decl.value), 0)

    def test_empty_string_array(self):
        code = "s: array [2] string = {};"
        ast = self.parse(code)
        decl = ast.body[0]
        self.assertIsInstance(decl, ArrayDecl)
        self.assertEqual(decl.name, "s")
        self.assertEqual(decl.type.base.name, "string")
        self.assertEqual(decl.type.size.value, 2)
        self.assertEqual(decl.type.size.value, decl.type.size.value)
        self.assertEqual(len(decl.value), 0)

    def test_empty_boolean_array(self):
        code = "b: array [1] boolean = {};"
        ast = self.parse(code)
        decl = ast.body[0]
        self.assertIsInstance(decl, ArrayDecl)
        self.assertEqual(decl.name, "b")
        self.assertEqual(decl.type.base.name, "boolean")
        self.assertEqual(decl.type.size.value, 1)
        self.assertEqual(decl.type.size.value, decl.type.size.value)
        self.assertEqual(len(decl.value), 0)

    def test_none_array(self):
        code = "b: array [1] boolean;"
        ast = self.parse(code)
        decl = ast.body[0]
        self.assertIsInstance(decl, ArrayDecl)
        self.assertEqual(decl.name, "b")
        self.assertEqual(decl.type.base.name, "boolean")
        self.assertEqual(decl.type.size.value, 1)
        self.assertEqual(decl.type.size.value, decl.type.size.value)
        self.assertEqual(len(decl.value), 0)

    def test_negative_size_array(self):
        code = "b: array [-1] boolean = {};"
        ast = self.parse(code)
        decl = ast.body[0]
        self.assertIsInstance(decl, ArrayDecl)
        self.assertEqual(decl.name, "b")
        self.assertEqual(decl.type.base.name, "boolean")
        self.assertIsInstance(decl.type.size, UnaryOper)
        self.assertEqual(decl.type.size.expr.value, 1)
        self.assertEqual(decl.type.size.oper, "-")
        self.assertEqual(len(decl.value), 0)

    # ========== FILLED ARRAY ASSIGNMENTS WITH VARIOUS SIZES ==========

    def test_single_element_array(self):
        code = "a: array [1] integer = {42};"
        ast = self.parse(code)
        decl = ast.body[0]
        self.assertIsInstance(decl, ArrayDecl)
        self.assertEqual(decl.type.size.value, 1)
        self.assertEqual(len(decl.value), 1)
        self.assertEqual(decl.value[0].value, 42)

    def test_large_array_assignment(self):
        code = "a: array [0] integer = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10};"
        ast = self.parse(code)
        decl = ast.body[0]
        self.assertIsInstance(decl, ArrayDecl)
        self.assertEqual(decl.type.size.value, 0)
        # se define como 0 pero se le asigna 10 elementos
        self.assertEqual(len(decl.value), 10)
        for i, val in enumerate(decl.value):
            self.assertEqual(val.value, i + 1)

    def test_mixed_float_array(self):
        code = "f: array [4] float = {1.0, 2.5, 3.14e2, 0.0e2, .5};"
        ast = self.parse(code)
        decl = ast.body[0]
        self.assertIsInstance(decl, ArrayDecl)
        self.assertEqual(decl.type.size.value, 4)
        self.assertEqual(len(decl.value), 5)
        expected_values = [1.0, 2.5, 3.14e2, 0.0e2, 0.5]
        for i, val in enumerate(decl.value):
            self.assertAlmostEqual(val.value, expected_values[i], places=7)

    def test_string_array_with_escapes(self):
        code = 's: array [3] string = {"hello\\n", "world\\t", "test\\\\"};'
        ast = self.parse(code)
        decl = ast.body[0]
        self.assertIsInstance(decl, ArrayDecl)
        self.assertEqual(decl.type.size.value, 3)
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
        self.assertEqual(decl.type.size.value, 5)
        self.assertEqual(len(decl.value), 0)  # No initialization
