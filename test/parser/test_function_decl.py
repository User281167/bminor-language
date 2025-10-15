import unittest
from parser import Parser
from scanner import Lexer
from parser.model import *


class TestFunctionDecl(unittest.TestCase):
    def setUp(self):
        self.lexer = Lexer()
        self.parser = Parser()

    def parse(self, code):
        tokens = self.lexer.tokenize(code)
        return self.parser.parse(tokens)

    def test_fun_void(self):
        code = "main: function void () = { }"
        ast = self.parse(code)
        decl = ast.body[0]
        self.assertIsInstance(decl, FuncDecl)
        self.assertEqual(decl.name, "main")
        self.assertEqual(decl.return_type.name, "void")
        self.assertEqual(len(decl.params), 0)

    def test_fun_name(self):
        code = "myFunc: function integer () = { }"
        ast = self.parse(code)
        decl = ast.body[0]
        self.assertIsInstance(decl, FuncDecl)
        self.assertEqual(decl.name, "myFunc")

    def test_fun_name_(self):
        code = "_123_: function integer () = { }"
        ast = self.parse(code)
        decl = ast.body[0]
        self.assertIsInstance(decl, FuncDecl)
        self.assertEqual(decl.name, "_123_")

    def test_fun_return_integer(self):
        code = "main: function integer () = { }"
        ast = self.parse(code)
        decl = ast.body[0]
        self.assertIsInstance(decl, FuncDecl)
        self.assertEqual(decl.return_type.name, "integer")

    def test_fun_return_char(self):
        code = "main: function char () = { }"
        ast = self.parse(code)
        decl = ast.body[0]
        self.assertIsInstance(decl, FuncDecl)
        self.assertEqual(decl.return_type.name, "char")

    def test_fun_return_string(self):
        code = "main: function string () = { }"
        ast = self.parse(code)
        decl = ast.body[0]
        self.assertIsInstance(decl, FuncDecl)
        self.assertEqual(decl.return_type.name, "string")

    def test_fun_return_float(self):
        code = "main: function float () = { }"
        ast = self.parse(code)
        decl = ast.body[0]
        self.assertIsInstance(decl, FuncDecl)
        self.assertEqual(decl.return_type.name, "float")

    def test_fun_return_boolean(self):
        code = "main: function boolean () = { }"
        ast = self.parse(code)
        decl = ast.body[0]
        self.assertIsInstance(decl, FuncDecl)
        self.assertEqual(decl.return_type.name, "boolean")

    ############################################################
    # la gramática permite funciones con arreglos con tamaños
    ############################################################

    def test_fun_return_array_int_size(self):
        code = "main: function array [0] integer () = { }"
        ast = self.parse(code)
        decl = ast.body[0]
        self.assertIsInstance(decl, FuncDecl)
        self.assertIsInstance(decl.return_type, ArrayType)
        self.assertEqual(decl.return_type.base.name, "integer")
        self.assertEqual(decl.return_type.size.value, 0)

    def test_fun_return_array_float_size(self):
        code = "main: function array [10] float () = { }"
        ast = self.parse(code)
        decl = ast.body[0]
        self.assertIsInstance(decl, FuncDecl)
        self.assertIsInstance(decl.return_type, ArrayType)
        self.assertEqual(decl.return_type.base.name, "float")
        self.assertEqual(decl.return_type.size.value, 10)

    def test_fun_return_array_char_size(self):
        code = "main: function array [3] char () = { }"
        ast = self.parse(code)
        decl = ast.body[0]
        self.assertIsInstance(decl, FuncDecl)
        self.assertIsInstance(decl.return_type, ArrayType)
        self.assertEqual(decl.return_type.base.name, "char")
        self.assertEqual(decl.return_type.size.value, 3)

    def test_fun_return_array_boolean_size(self):
        code = "main: function array [1] boolean () = { }"
        ast = self.parse(code)
        decl = ast.body[0]
        self.assertIsInstance(decl, FuncDecl)
        self.assertIsInstance(decl.return_type, ArrayType)
        self.assertEqual(decl.return_type.base.name, "boolean")
        self.assertEqual(decl.return_type.size.value, 1)

    def test_fun_return_array_string(self):
        code = "main: function array [] string () = { }"
        ast = self.parse(code)
        decl = ast.body[0]
        self.assertIsInstance(decl, FuncDecl)
        self.assertIsInstance(decl.return_type, ArrayType)
        self.assertEqual(decl.return_type.base.name, "string")
        self.assertEqual(decl.return_type.size, None)

    def test_fun_return_array_empty(self):
        code = "main: function array [] string () = { }"
        ast = self.parse(code)
        decl = ast.body[0]
        self.assertIsInstance(decl, FuncDecl)
        self.assertIsInstance(decl.return_type, ArrayType)
        self.assertEqual(decl.return_type.base.name, "string")
        self.assertEqual(decl.return_type.size, None)

    def test_fun_return_array_multidimensional(self):
        code = "main: function array [2] array [4] integer () = { }"
        ast = self.parse(code)
        decl = ast.body[0]
        self.assertIsInstance(decl, FuncDecl)
        self.assertIsInstance(decl.return_type, ArrayType)
        self.assertIsInstance(decl.return_type.base, ArrayType)
        self.assertEqual(decl.return_type.size.value, 2)
        self.assertEqual(decl.return_type.base.size.value, 4)
        self.assertEqual(decl.return_type.base.base.name, "integer")

    ############################################################
    # la gramática permite incluso funciones con arreglos con tamaños como expresiones
    ############################################################

    def test_fun_return_array_expr(self):
        code = "main: function array [2 + 3] integer () = { }"
        ast = self.parse(code)
        decl = ast.body[0]
        self.assertIsInstance(decl, FuncDecl)
        self.assertIsInstance(decl.return_type, ArrayType)
        self.assertIsInstance(decl.return_type.size, BinOper)
        self.assertEqual(decl.return_type.size.oper, "+")
        self.assertEqual(decl.return_type.size.left.value, 2)
        self.assertEqual(decl.return_type.size.right.value, 3)
        self.assertEqual(decl.return_type.base.name, "integer")

    def test_fun_return_array_var(self):
        code = "main: function array [a] integer () = { }"
        ast = self.parse(code)
        decl = ast.body[0]
        self.assertIsInstance(decl, FuncDecl)
        self.assertIsInstance(decl.return_type, ArrayType)
        self.assertIsInstance(decl.return_type.size, VarLoc)

    def test_fun_return_array_expr_var(self):
        code = "main: function array [2 + a] integer () = { }"
        ast = self.parse(code)
        decl = ast.body[0]
        self.assertIsInstance(decl, FuncDecl)
        self.assertIsInstance(decl.return_type, ArrayType)
        self.assertIsInstance(decl.return_type.size, BinOper)
        self.assertIsInstance(decl.return_type.size.right, VarLoc)
