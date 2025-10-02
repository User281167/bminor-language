import unittest
from parser import Parser
from scanner import Lexer
from model import *


class TestArrayAssignment(unittest.TestCase):
    def setUp(self):
        self.lexer = Lexer()
        self.parser = Parser()

    def parse(self, code):
        tokens = self.lexer.tokenize(code)
        return self.parser.parse(tokens)

    def test_array_assignment_expr(self):
        code = "main: function integer() = {x[0] = 0;}"
        ast = self.parse(code)
        main_dcl = ast.body[0]
        decl = main_dcl.body[0]
        self.assertIsInstance(decl, Assignment)
        self.assertEqual(decl.value.type, "integer")
        self.assertEqual(decl.location.array.name, "x")
        self.assertEqual(decl.location.index.type, "integer")
        self.assertEqual(decl.location.index.value, 0)

    def test_array_assignment_boolean(self):
        code = "main: function boolean() = {flags[1] = true;}"
        ast = self.parse(code)
        main_dcl = ast.body[0]
        decl = main_dcl.body[0]
        self.assertIsInstance(decl, Assignment)
        self.assertEqual(decl.value.type, "boolean")
        self.assertEqual(decl.value.value, True)
        self.assertEqual(decl.location.array.name, "flags")
        self.assertEqual(decl.location.index.type, "integer")
        self.assertEqual(decl.location.index.value, 1)

    def test_array_assignment_index_expr(self):
        code = "main: function integer() = {x[i + 1] = 42;}"
        ast = self.parse(code)
        main_dcl = ast.body[0]
        decl = main_dcl.body[0]
        self.assertIsInstance(decl.location.index, BinOper)
        self.assertEqual(decl.location.index.oper, '+')
        self.assertEqual(decl.location.index.left.name, "i")
        self.assertEqual(decl.location.index.right.value, 1)
        self.assertEqual(decl.value.value, 42)

    def test_array_assignment_value_expr(self):
        code = "main: function integer() = {x[0] = a * 2;}"
        ast = self.parse(code)
        main_dcl = ast.body[0]
        decl = main_dcl.body[0]
        self.assertIsInstance(decl.value, BinOper)
        self.assertEqual(decl.value.oper, '*')
        self.assertEqual(decl.value.left.name, "a")
        self.assertEqual(decl.value.right.value, 2)

    def test_array_assignment_negative_index(self):
        code = "main: function integer() = {x[-1] = 99;}"
        ast = self.parse(code)
        main_dcl = ast.body[0]
        decl = main_dcl.body[0]
        self.assertIsInstance(decl.location.index, UnaryOper)
        self.assertEqual(decl.location.index.oper, '-')
        self.assertEqual(decl.location.index.expr.value, 1)
        self.assertEqual(decl.value.value, 99)

    def test_array_assignment_negated_boolean(self):
        code = "main: function boolean() = {flags[0] = !ready;}"
        ast = self.parse(code)
        main_dcl = ast.body[0]
        decl = main_dcl.body[0]
        self.assertIsInstance(decl.value, UnaryOper)
        self.assertEqual(decl.value.oper, '!')
        self.assertEqual(decl.value.expr.name, "ready")

    def test_array_assignment_float(self):
        code = "main: function float() = {temps[2] = 36.5;}"
        ast = self.parse(code)
        decl = ast.body[0].body[0]
        self.assertIsInstance(decl, Assignment)
        self.assertEqual(decl.value.type, "float")
        self.assertEqual(decl.value.value, 36.5)
        self.assertEqual(decl.location.array.name, "temps")
        self.assertEqual(decl.location.index.value, 2)

    def test_array_assignment_index_variable(self):
        code = "main: function integer() = {x[i] = 10;}"
        ast = self.parse(code)
        decl = ast.body[0].body[0]
        self.assertIsInstance(decl.location.index, VarLoc)
        self.assertEqual(decl.location.index.name, "i")
        self.assertEqual(decl.value.value, 10)

    def test_array_assignment_function_call(self):
        code = "main: function integer() = {results[0] = compute();}"
        ast = self.parse(code)
        decl = ast.body[0].body[0]
        self.assertIsInstance(decl.value, FuncCall)
        self.assertEqual(decl.value.name, "compute")
        self.assertEqual(decl.location.array.name, "results")

    def test_array_assignment_complex_index(self):
        code = "main: function integer() = {x[(a + b) * 2] = 5;}"
        ast = self.parse(code)
        decl = ast.body[0].body[0]
        self.assertIsInstance(decl.location.index, BinOper)
        self.assertEqual(decl.location.index.oper, '*')
        self.assertIsInstance(decl.location.index.left, BinOper)
        self.assertEqual(decl.location.index.left.oper, '+')

    def test_array_assignment_logical_expr(self):
        code = "main: function boolean() = {flags[0] = a && b;}"
        ast = self.parse(code)
        decl = ast.body[0].body[0]
        self.assertIsInstance(decl.value, BinOper)
        self.assertEqual(decl.value.oper, 'LAND')
        self.assertEqual(decl.value.left.name, "a")
        self.assertEqual(decl.value.right.name, "b")

    def test_array_assignment_index_string(self):
        code = 'main: function integer() = {x["key"] = 1;}'
        ast = self.parse(code)
        decl = ast.body[0].body[0]
        self.assertIsInstance(decl.location.index, Literal)
        self.assertEqual(decl.location.index.type, "string")
        self.assertEqual(decl.location.index.value, "key")
        self.assertEqual(decl.value.value, 1)

    def test_array_assignment_index_char(self):
        code = "main: function integer() = {x['a'] = 2;}"
        ast = self.parse(code)
        decl = ast.body[0].body[0]
        self.assertIsInstance(decl.location.index, Literal)
        self.assertEqual(decl.location.index.type, "char")
        self.assertEqual(decl.location.index.value, 'a')
        self.assertEqual(decl.value.value, 2)

    def test_array_assignment_value_string(self):
        code = 'main: function string() = {names[0] = "Alice";}'
        ast = self.parse(code)
        decl = ast.body[0].body[0]
        self.assertEqual(decl.location.array.name, "names")
        self.assertEqual(decl.location.index.value, 0)
        self.assertEqual(decl.value.type, "string")
        self.assertEqual(decl.value.value, "Alice")

    def test_array_assignment_value_char(self):
        code = "main: function char() = {letters[1] = 'z';}"
        ast = self.parse(code)
        decl = ast.body[0].body[0]
        self.assertEqual(decl.location.array.name, "letters")
        self.assertEqual(decl.location.index.value, 1)
        self.assertEqual(decl.value.type, "char")
        self.assertEqual(decl.value.value, 'z')

    def test_array_assignment_index_boolean(self):
        code = "main: function integer() = {x[true] = 5;}"
        ast = self.parse(code)
        decl = ast.body[0].body[0]
        self.assertEqual(decl.location.index.type, "boolean")
        self.assertEqual(decl.location.index.value, True)
        self.assertEqual(decl.value.value, 5)

    def test_array_assignment_value_boolean_expr(self):
        code = "main: function boolean() = {flags[0] = a ` b;}"
        ast = self.parse(code)
        decl = ast.body[0].body[0]
        self.assertIsInstance(decl.value, BinOper)
        self.assertEqual(decl.value.oper, 'LOR')
        self.assertEqual(decl.value.left.name, "a")
        self.assertEqual(decl.value.right.name, "b")
