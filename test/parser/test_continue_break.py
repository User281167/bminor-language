import unittest
from parser import Parser
from parser.model import *

from scanner import Lexer


class TestContinueBreak(unittest.TestCase):
    def setUp(self):
        self.lexer = Lexer()
        self.parser = Parser()

    def parse(self, code):
        tokens = self.lexer.tokenize(code)
        return self.parser.parse(tokens)

    def test_continue(self):
        code = """
        main: function void () = {
            continue;
        }
        """
        ast = self.parse(code)
        stmt = ast.body[0].body[0]
        self.assertIsInstance(stmt, ContinueStmt)

    def test_break(self):
        code = """
        main: function void () = {
            break;
        }
        """
        ast = self.parse(code)
        stmt = ast.body[0].body[0]
        self.assertIsInstance(stmt, BreakStmt)

    def test_continue_break_inside_for(self):
        code = """
        main: function void () = {
            for (i = 0; i < 10; i = i + 1) {
                continue;
                break;
            }
        }
        """
        ast = self.parse(code)
        stmt = ast.body[0].body[0]
        self.assertIsInstance(stmt, ForStmt)
        self.assertEqual(len(stmt.body), 2)
        self.assertIsInstance(stmt.body[0], ContinueStmt)
        self.assertIsInstance(stmt.body[1], BreakStmt)

    def test_continue_break_inside_while(self):
        code = """
        main: function void () = {
            while (x < 5) {
                continue;
                break;
            }
        }
        """
        ast = self.parse(code)
        stmt = ast.body[0].body[0]
        self.assertIsInstance(stmt, WhileStmt)
        self.assertEqual(len(stmt.body), 2)
        self.assertIsInstance(stmt.body[0], ContinueStmt)
        self.assertIsInstance(stmt.body[1], BreakStmt)

    def test_continue_break_inside_do_while(self):
        code = """
        main: function void () = {
            do {
                continue;
                break;
            } while (x < 5);
        }
        """
        ast = self.parse(code)
        stmt = ast.body[0].body[0]
        self.assertIsInstance(stmt, DoWhileStmt)
        self.assertEqual(len(stmt.body), 2)
        self.assertIsInstance(stmt.body[0], ContinueStmt)
        self.assertIsInstance(stmt.body[1], BreakStmt)
