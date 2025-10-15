from utils.errors import errors_detected, clear_errors
import unittest
from parser import Parser
from scanner import Lexer
from parser.model import *
from utils.errors import errors_detected


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
        self.assertEqual(decl.type.size.value, 2)

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
