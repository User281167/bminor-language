import unittest
from parser import Parser
from scanner import Lexer
from model import *


class TestForLoop(unittest.TestCase):
    def setUp(self):
        self.lexer = Lexer()
        self.parser = Parser()

    def parse(self, code):
        tokens = self.lexer.tokenize(code)
        return self.parser.parse(tokens)

    def test_for_basic(self):
        code = """
        main: function void () = {
            for (i = 0; i < 10; i = i + 1) {
                print i;
            }
        }
        """
        ast = self.parse(code)
        stmt = ast.body[0].body[0]
        self.assertIsInstance(stmt, ForStmt)
        self.assertIsInstance(stmt.init, Assignment)
        self.assertIsInstance(stmt.condition, BinOper)
        self.assertEqual(stmt.condition.oper, "<")
        self.assertIsInstance(stmt.update, Assignment)

    def test_for_full_declaration(self):
        code = """
        main: function void () = {
            for (i = 0; i < 10; i = i + 1) { print i; }
        }
        """
        ast = self.parse(code)
        stmt = ast.body[0].body[0]
        self.assertIsInstance(stmt, ForStmt)
        self.assertIsInstance(stmt.init, Assignment)
        self.assertIsInstance(stmt.condition, BinOper)
        self.assertIsInstance(stmt.update, Assignment)
        self.assertEqual(stmt.condition.oper, "<")
        self.assertEqual(len(stmt.body), 1)
        self.assertIsInstance(stmt.body[0], PrintStmt)

    def test_for_only_condition(self):
        code = """
        main: function void () = {
            for (; x < 5; ) { print x; }
        }
        """
        ast = self.parse(code)
        stmt = ast.body[0].body[0]
        self.assertIsNone(stmt.init)
        self.assertIsInstance(stmt.condition, BinOper)
        self.assertIsNone(stmt.update)

    def test_for_only_update(self):
        code = """
        main: function void () = {
            for (; ; x = x + 1) { x;}
        }
        """
        ast = self.parse(code)
        stmt = ast.body[0].body[0]
        self.assertIsNone(stmt.init)
        self.assertIsNone(stmt.condition)
        self.assertIsInstance(stmt.update, Assignment)

    def test_for_only_init(self):
        code = """
        main: function void () = {
            for (i = 0; ; ) { x;}
        }
        """
        ast = self.parse(code)
        stmt = ast.body[0].body[0]
        self.assertIsInstance(stmt.init, Assignment)
        self.assertIsNone(stmt.condition)
        self.assertIsNone(stmt.update)

    def test_for_with_func_call_condition(self):
        code = """
        main: function void () = {
            for (; check(); ) {
                print "looping";
            }
        }
        """
        ast = self.parse(code)
        stmt = ast.body[0].body[0]
        self.assertIsInstance(stmt.condition, FuncCall)
        self.assertEqual(stmt.condition.name, "check")

    def test_for_with_logical_condition(self):
        code = """
        main: function void () = {
            for (; x < 10 && y > 0; ) {
                print x;
            }
        }
        """
        ast = self.parse(code)
        stmt = ast.body[0].body[0]
        self.assertIsInstance(stmt.condition, BinOper)
        self.assertEqual(stmt.condition.oper, "LAND")

    def test_for_only_condition(self):
        code = """
        main: function void () = {
            for (; x < 5; ) {
                print x;
            }
        }
        """
        ast = self.parse(code)
        stmt = ast.body[0].body[0]
        self.assertIsInstance(stmt.condition, BinOper)

    def test_for_empty_declaration(self):
        code = """
        main: function void () = {
            for (; ; ) { x; }
        }
        """
        ast = self.parse(code)
        stmt = ast.body[0].body[0]
        self.assertIsNone(stmt.init)
        self.assertIsNone(stmt.condition)
        self.assertIsNone(stmt.update)

    def test_for_fun_call(self):
        code = """
        main: function void () = {
            for (; check(); ) {
                print "looping";
            }
        }
        """
        ast = self.parse(code)
        stmt = ast.body[0].body[0]
        self.assertIsInstance(stmt.condition, FuncCall)
        self.assertEqual(stmt.condition.name, "check")

    def test_for_body_without_brace(self):
        code = """
        main: function void () = {
            for (i = 0; i < 10; i = i + 1) print i;
        }
        """
        self.parse(code)
        ast = self.parse(code)
        stmt = ast.body[0].body[0]
        self.assertIsInstance(stmt, ForStmt)
        self.assertEqual(len(stmt.body), 1)
        self.assertIsInstance(stmt.body[0], PrintStmt)

    def test_for_body_without_inc(self):
        code = """
        main: function void () = {
            for (i = 0; i < 10; i = i++) print i;
        }
        """
        self.parse(code)
        ast = self.parse(code)
        stmt = ast.body[0].body[0]
        self.assertIsInstance(stmt, ForStmt)
        self.assertIsInstance(stmt.update, Assignment)
        self.assertIsInstance(stmt.update.value, Increment)
        self.assertEqual(len(stmt.body), 1)
        self.assertIsInstance(stmt.body[0], PrintStmt)
