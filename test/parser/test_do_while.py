import unittest
from parser import Parser
from parser.model import *

from scanner import Lexer


class TestDoWhileLoop(unittest.TestCase):
    def setUp(self):
        self.lexer = Lexer()
        self.parser = Parser()

    def parse(self, code):
        tokens = self.lexer.tokenize(code)
        return self.parser.parse(tokens)

    def test_do_while_true_literal(self):
        code = """
        main: function void () = {
            do {
                print "looping";
            } while (true);
        }
        """
        ast = self.parse(code)
        stmt = ast.body[0].body[0]
        self.assertIsInstance(stmt, DoWhileStmt)
        self.assertIsInstance(stmt.condition, Boolean)
        self.assertTrue(stmt.condition.value)
        self.assertEqual(len(stmt.body), 1)
        self.assertIsInstance(stmt.body[0], PrintStmt)

    def test_do_while_with_binop_condition(self):
        code = """
        main: function void () = {
            do {
                print x;
            } while (x < 10);
        }
        """
        ast = self.parse(code)
        stmt = ast.body[0].body[0]
        self.assertIsInstance(stmt.condition, BinOper)
        self.assertEqual(stmt.condition.oper, "<")

    def test_do_while_with_func_call_condition(self):
        code = """
        main: function void () = {
            do {
                print "checking";
            } while (shouldContinue());
        }
        """
        ast = self.parse(code)
        stmt = ast.body[0].body[0]
        self.assertIsInstance(stmt.condition, FuncCall)
        self.assertEqual(stmt.condition.name, "shouldContinue")

    def test_do_while_with_multiple_statements(self):
        code = """
        main: function void () = {
            do {
                print x;
                x = x + 1;
            } while (x < 5);
        }
        """
        ast = self.parse(code)
        stmt = ast.body[0].body[0]
        self.assertEqual(len(stmt.body), 2)
        self.assertIsInstance(stmt.body[0], PrintStmt)
        self.assertIsInstance(stmt.body[1], Assignment)

    def test_do_while_with_return(self):
        code = """
        main: function integer () = {
            do {
                return 42;
            } while (false);
        }
        """
        ast = self.parse(code)
        stmt = ast.body[0].body[0]
        self.assertIsInstance(stmt.body[0], ReturnStmt)
        self.assertIsInstance(stmt.condition, Boolean)
        self.assertFalse(stmt.condition.value)

    def test_do_while_with_expr(self):
        code = """
        main: function integer () = {
            do {
                return 42;
            } while (x + y);
        }
        """
        ast = self.parse(code)
        stmt = ast.body[0].body[0]
        self.assertIsInstance(stmt.body[0], ReturnStmt)
        self.assertIsInstance(stmt.condition, BinOper)
