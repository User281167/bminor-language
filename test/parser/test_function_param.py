import unittest
from parser import Parser
from scanner import Lexer
from model import *


class TestFunctionParams(unittest.TestCase):
    def setUp(self):
        self.lexer = Lexer()
        self.parser = Parser()

    def parse(self, code):
        tokens = self.lexer.tokenize(code)
        return self.parser.parse(tokens)

    def test_fun_with_named_params(self):
        code = "sum: function integer (a: integer, b: integer) = { return a + b; }"
        ast = self.parse(code)
        decl = ast.body[0]
        self.assertEqual(decl.params[0].name, "a")
        self.assertEqual(decl.params[1].name, "b")
        self.assertEqual(decl.params[0].type.name, "integer")

    def test_fun_with_array_param(self):
        code = "process: function void (arr: array [10] float) = { print arr[0]; }"
        ast = self.parse(code)
        decl = ast.body[0]
        self.assertIsInstance(decl.params[0].type, ArrayType)
        self.assertEqual(decl.params[0].type.base.name, "float")
        self.assertEqual(decl.params[0].type.size.value, 10)

    def test_fun_call_no_args(self):
        code = """
        main: function void () = {
            foo();
        }
        """
        ast = self.parse(code)
        call = ast.body[0].body[0]
        self.assertIsInstance(call, FuncCall)
        self.assertEqual(call.name, "foo")
        self.assertEqual(len(call.args), 0)

    def test_fun_call_with_args(self):
        code = """
        main: function void () = {
            foo(1, 2);
        }
        """
        ast = self.parse(code)
        call = ast.body[0].body[0]
        self.assertEqual(len(call.args), 2)
        self.assertIsInstance(call.args[0], Integer)
        self.assertEqual(call.args[0].value, 1)

    def test_fun_call_with_expr_args(self):
        code = """
        main: function void () = {
            foo(1 + 2, a);
        }
        """
        ast = self.parse(code)
        call = ast.body[0].body[0]
        self.assertIsInstance(call.args[0], BinOper)
        self.assertEqual(call.args[0].oper, "+")
        self.assertIsInstance(call.args[1], VarLoc)
