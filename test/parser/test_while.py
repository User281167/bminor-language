import unittest
from parser import Parser
from parser.model import *

from scanner import Lexer


class TestWhileLoop(unittest.TestCase):
    def setUp(self):
        self.lexer = Lexer()
        self.parser = Parser()

    def parse(self, code):
        tokens = self.lexer.tokenize(code)
        return self.parser.parse(tokens)

    def test_while_true_literal(self):
        code = """
        main: function void () = {
            while (true) {
                print "looping";
            }
        }
        """
        ast = self.parse(code)
        stmt = ast.body[0].body[0]
        self.assertIsInstance(stmt, WhileStmt)
        self.assertIsInstance(stmt.condition, Boolean)
        self.assertTrue(stmt.condition.value)
        self.assertIsInstance(stmt.body[0], PrintStmt)

    def test_while_with_binop_condition(self):
        code = """
        main: function void () = {
            while (x < 10) {
                print x;
            }
        }
        """
        ast = self.parse(code)
        stmt = ast.body[0].body[0]
        self.assertIsInstance(stmt.condition, BinOper)
        self.assertEqual(stmt.condition.oper, "<")

    def test_while_with_func_call_condition(self):
        code = """
        main: function void () = {
            while (check()) {
                print "ok";
            }
        }
        """
        ast = self.parse(code)
        stmt = ast.body[0].body[0]
        self.assertIsInstance(stmt.condition, FuncCall)
        self.assertEqual(stmt.condition.name, "check")

    def test_while_without_braces(self):
        code = """
        main: function void () = {
            while (x < 5)
                print x;
        }
        """
        ast = self.parse(code)
        stmt = ast.body[0].body[0]
        self.assertIsInstance(stmt, WhileStmt)
        self.assertEqual(len(stmt.body), 1)
        self.assertIsInstance(stmt.body[0], PrintStmt)

    def test_while_empty_body(self):
        code = """
        main: function void () = {
            while (true) { x = 2;}
        }
        """
        ast = self.parse(code)
        stmt = ast.body[0].body[0]
        self.assertEqual(len(stmt.body), 1)

    def test_while_with_func_call_condition_2(self):
        code = """
        main: function void () = {
            while (isReady()) {
                print "ready";
            }
        }
        """
        ast = self.parse(code)
        stmt = ast.body[0].body[0]
        self.assertIsInstance(stmt.condition, FuncCall)
        self.assertEqual(stmt.condition.name, "isReady")
        self.assertIsInstance(stmt.body[0], PrintStmt)

    def test_while_with_return_in_body(self):
        code = """
        main: function integer () = {
            while (x < 5) {
                return x;
            }
        }
        """
        ast = self.parse(code)
        stmt = ast.body[0].body[0]
        self.assertIsInstance(stmt.body[0], ReturnStmt)
        self.assertIsInstance(stmt.body[0].expr, VarLoc)

    def test_while_with_multiple_statements(self):
        code = """
        main: function integer () = {
            while (x < 5) {
                print x;
                return x;
            }
        }
        """
        ast = self.parse(code)
        stmt = ast.body[0].body[0]
        self.assertEqual(len(stmt.body), 2)
        self.assertIsInstance(stmt.body[0], PrintStmt)
        self.assertIsInstance(stmt.body[1], ReturnStmt)

    def test_while_with_logical_expression(self):
        code = """
        main: function void () = {
            while (x < 10 && y > 0) {
                print x;
            }
        }
        """
        ast = self.parse(code)
        stmt = ast.body[0].body[0]
        self.assertIsInstance(stmt.condition, BinOper)
        self.assertEqual(stmt.condition.oper, "LAND")

    def test_while_missing_condition(self):
        code = """
        main: function void () = {
            while () {
                print x;
            }
        }
        """
        self.parse(code)
        ast = self.parse(code)
        stmt = ast.body[0].body[0]
        self.assertIsNone(stmt.condition)
