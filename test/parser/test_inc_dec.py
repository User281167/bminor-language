import unittest
from parser import Parser
from scanner import Lexer
from model import *


class TestIncDec(unittest.TestCase):
    def setUp(self):
        self.lexer = Lexer()
        self.parser = Parser()

    def parse(self, code):
        tokens = self.lexer.tokenize(code)
        return self.parser.parse(tokens)

    def test_var_increment(self):
        code = "main: function integer () = {x++;}"
        ast = self.parse(code)
        stmt = ast.body[0].body[0]
        self.assertEqual(stmt, Increment(VarLoc("x"), True))

    def test_var_decrement(self):
        code = "main: function integer () = {x--;}"
        ast = self.parse(code)
        stmt = ast.body[0].body[0]
        self.assertEqual(stmt, Decrement(VarLoc("x"), True))

    def test_array_index_increment(self):
        code = "main: function integer () = {arr[0]++;}"
        ast = self.parse(code)
        stmt = ast.body[0].body[0]
        self.assertEqual(
            stmt,
            Increment(ArrayLoc(VarLoc("arr"), Integer(0)), True)
        )

    def test_array_index_decrement(self):
        code = "main: function integer () = {arr[0]--;}"
        ast = self.parse(code)
        stmt = ast.body[0].body[0]
        self.assertEqual(
            stmt,
            Decrement(ArrayLoc(VarLoc("arr"), Integer(0)), True)
        )

    def test_pre_increment(self):
        code = "main: function integer () = {++x;}"
        ast = self.parse(code)
        stmt = ast.body[0].body[0]
        self.assertEqual(stmt, Increment(VarLoc("x"), False))

    def test_pre_decrement(self):
        code = "main: function integer () = {--x;}"
        ast = self.parse(code)
        stmt = ast.body[0].body[0]
        self.assertEqual(stmt, Decrement(VarLoc("x"), False))

    def test_increment_in_expression(self):
        code = "main: function integer () = {y = x++;}"
        ast = self.parse(code)
        stmt = ast.body[0].body[0]
        self.assertEqual(
            stmt,
            Assignment(
                VarLoc("y"),
                Increment(VarLoc("x"), True)
            )
        )

    def test_decrement_in_expression(self):
        code = "main: function integer () = {y = --x;}"
        ast = self.parse(code)
        stmt = ast.body[0].body[0]
        self.assertEqual(
            stmt,
            Assignment(
                VarLoc("y"),
                Decrement(VarLoc("x"), False)
            )
        )

    def test_char_increment(self):
        code = "main: function char () = {c: char = 'a'; c++;}"
        ast = self.parse(code)
        decl = ast.body[0].body[0]
        inc = ast.body[0].body[1]
        self.assertEqual(decl.name, "c")
        self.assertEqual(inc, Increment(VarLoc("c"), True))

    def test_string_decrement(self):
        # Correcto para el parser mal para el semántico
        code = "main: function string () = {s: string = \"hello\"; s--;}"
        ast = self.parse(code)
        decl = ast.body[0].body[0]
        dec = ast.body[0].body[1]
        self.assertEqual(decl.name, "s")
        self.assertEqual(dec, Decrement(VarLoc("s"), True))

    def test_increment_integer_literal(self):
        code = "main: function integer () = {123++;}"
        ast = self.parse(code)
        decl = ast.body[0].body[0]
        self.assertEqual(decl, Increment(Integer(123), True))

    def test_decrement_float_literal(self):
        code = "main: function float () = {3.14--;}"
        ast = self.parse(code)
        decl = ast.body[0].body[0]
        self.assertEqual(decl, Decrement(Float(3.14), True))

    def test_increment_char_literal(self):
        code = "main: function char () = {'a'++;}"
        ast = self.parse(code)
        decl = ast.body[0].body[0]
        self.assertEqual(decl, Increment(Char("'a'"), True))

    def test_decrement_string_literal(self):
        # valido pero no semántico
        code = "main: function string () = {\"hello\"--;}"
        ast = self.parse(code)
        decl = ast.body[0].body[0]
        self.assertEqual(decl, Decrement(String("\"hello\""), True))

    def test_increment_boolean_literal(self):
        # valido pero no semántico
        code = "main: function boolean () = {true++;}"
        ast = self.parse(code)
        decl = ast.body[0].body[0]
        self.assertEqual(decl, Increment(Boolean(True), True))

    def test_decrement_boolean_literal(self):
        code = "main: function boolean () = {false--;}"
        ast = self.parse(code)
        decl = ast.body[0].body[0]
        self.assertEqual(decl, Decrement(Boolean(False), True))

    def test_increment_function_call(self):
        code = "main: function integer () = {sum()++;}"
        ast = self.parse(code)
        decl = ast.body[0].body[0]
        self.assertEqual(decl, Increment(FuncCall("sum", []), True))

    def test_decrement_function_call(self):
        code = "main: function integer () = {--sum();}"
        ast = self.parse(code)
        decl = ast.body[0].body[0]
        self.assertEqual(decl, Decrement(FuncCall("sum", []), False))

    def test_increment_grouped_expression(self):
        code = "main: function integer () = {(x + 1)++;}"
        ast = self.parse(code)
        decl = ast.body[0].body[0]
        self.assertEqual(decl, Increment(
            BinOper("+", VarLoc("x"), Integer(1)), True))

    def test_decrement_grouped_expression(self):
        code = "main: function integer () = {--(x + 1);}"
        ast = self.parse(code)
        decl = ast.body[0].body[0]
        self.assertEqual(decl, Decrement(
            BinOper("+", VarLoc("x"), Integer(1)), False))
