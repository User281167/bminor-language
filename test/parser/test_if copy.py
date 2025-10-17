import unittest
from parser import Parser
from parser.model import *

from scanner import Lexer


class TestIfElseStmt(unittest.TestCase):
    def setUp(self):
        self.lexer = Lexer()
        self.parser = Parser()

    def parse(self, code):
        tokens = self.lexer.tokenize(code)
        return self.parser.parse(tokens)

    def test_if_without_else(self):
        code = """
        main: function void () = {
            if (true) {
                print 1;
            }
        }
        """
        ast = self.parse(code)
        func = ast.body[0]
        stmt = func.body[0]
        self.assertIsInstance(stmt, IfStmt)
        self.assertIsInstance(stmt.condition, Boolean)
        self.assertEqual(stmt.condition.value, True)
        self.assertEqual(len(stmt.then_branch), 1)
        self.assertIsInstance(stmt.then_branch[0], PrintStmt)

    def test_if_with_else(self):
        code = """
        main: function void () = {
            if (false) {
                print 0;
            } else {
                print 1;
            }
        }
        """
        ast = self.parse(code)
        func = ast.body[0]
        stmt = func.body[0]
        self.assertIsInstance(stmt, IfStmt)
        self.assertIsInstance(stmt.condition, Boolean)
        self.assertEqual(stmt.condition.value, False)
        self.assertEqual(len(stmt.then_branch), 1)
        self.assertEqual(len(stmt.else_branch), 1)
        self.assertIsInstance(stmt.else_branch[0], PrintStmt)

    def test_nested_if_else(self):
        code = """
        main: function void () = {
            if (true) {
                if (false) {
                    print 0;
                } else {
                    print 1;
                }
            }
        }
        """
        ast = self.parse(code)
        func = ast.body[0]
        outer_if = func.body[0]
        self.assertIsInstance(outer_if, IfStmt)
        inner_if = outer_if.then_branch[0]
        self.assertIsInstance(inner_if, IfStmt)
        self.assertEqual(inner_if.condition.value, False)
        self.assertEqual(len(inner_if.else_branch), 1)
        self.assertIsInstance(inner_if.else_branch[0], PrintStmt)

    def test_if_with_expression_condition(self):
        code = """
        main: function void () = {
            if (1 + 2 == 3) {
                print "ok";
            }
        }
        """
        ast = self.parse(code)
        func = ast.body[0]
        stmt = func.body[0]
        self.assertIsInstance(stmt, IfStmt)
        self.assertIsInstance(stmt.condition, BinOper)
        self.assertEqual(stmt.condition.oper, "==")
        self.assertIsInstance(stmt.then_branch[0], PrintStmt)

    def test_if_with_array_access_condition(self):
        code = """
        main: function void () = {
            arr: array [3] integer = {1, 2, 3};
            if (arr[0] == 1) {
                print "match";
            }
        }
        """
        ast = self.parse(code)
        func = ast.body[0]
        stmt = func.body[1]
        self.assertIsInstance(stmt, IfStmt)
        self.assertIsInstance(stmt.condition, BinOper)
        self.assertEqual(stmt.condition.oper, "==")
        self.assertIsInstance(stmt.then_branch[0], PrintStmt)

    def test_if_with_logical_and(self):
        code = """
        main: function void () = {
            if (true && false) {
                print "never";
            }
        }
        """
        ast = self.parse(code)
        stmt = ast.body[0].body[0]
        self.assertIsInstance(stmt.condition, BinOper)
        self.assertEqual(stmt.condition.oper, "LAND")

    def test_if_with_logical_or(self):
        code = """
        main: function void () = {
            if (false ` true) {
                print "always";
            }
        }
        """
        ast = self.parse(code)
        stmt = ast.body[0].body[0]
        self.assertIsInstance(stmt.condition, BinOper)
        self.assertEqual(stmt.condition.oper, "LOR")

    def test_if_with_return_in_then(self):
        code = """
        main: function integer () = {
            if (true) {
                return 42;
            }
            return 0;
        }
        """
        ast = self.parse(code)
        stmt = ast.body[0].body[0]
        self.assertIsInstance(stmt, IfStmt)
        self.assertIsInstance(stmt.then_branch[0], ReturnStmt)
        self.assertIsInstance(stmt.then_branch[0].expr, Integer)

    def test_if_with_return_in_else(self):
        code = """
        main: function integer () = {
            if (false) {
                print "no";
            } else {
                return 99;
            }
        }
        """
        ast = self.parse(code)
        stmt = ast.body[0].body[0]
        self.assertIsInstance(stmt, IfStmt)
        self.assertIsInstance(stmt.else_branch[0], ReturnStmt)
        self.assertIsInstance(stmt.else_branch[0].expr, Integer)

    def test_if_with_complex_expression(self):
        code = """
        main: function void () = {
            if ((1 + 2) * 3 > 5) {
                print "yes";
            }
        }
        """
        ast = self.parse(code)
        stmt = ast.body[0].body[0]
        self.assertIsInstance(stmt.condition, BinOper)
        self.assertEqual(stmt.condition.oper, ">")
        self.assertIsInstance(stmt.then_branch[0], PrintStmt)

    def test_if_without_braces(self):
        code = """
        main: function void () = {
            if (1 > 0)
                print "ok";
        }
        """
        ast = self.parse(code)
        func = ast.body[0]
        stmt = func.body[0]
        self.assertIsInstance(stmt, IfStmt)
        self.assertIsInstance(stmt.condition, BinOper)
        self.assertEqual(stmt.condition.oper, ">")
        self.assertIsInstance(stmt.then_branch, PrintStmt)
