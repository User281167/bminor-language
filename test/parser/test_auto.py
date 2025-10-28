import unittest
from parser import Parser, ParserError
from parser.model import *

from scanner import Lexer
from utils import clear_errors, has_error


class TestAuto(unittest.TestCase):
    def setUp(self):
        self.lexer = Lexer()
        self.parser = Parser()
        clear_errors()

    def parse(self, code):
        tokens = self.lexer.tokenize(code)
        return self.parser.parse(tokens)

    def test_auto_integer(self):
        code = """
            x: auto = 12;
        """
        ast = self.parse(code)
        stmt = ast.body[0]
        self.assertIsInstance(stmt, AutoDecl)
        self.assertIsInstance(stmt.value, Integer)
        self.assertEqual(stmt.value.value, 12)

    def test_auto_string(self):
        code = """
            x: auto = "hello";
        """
        ast = self.parse(code)
        stmt = ast.body[0]
        self.assertIsInstance(stmt, AutoDecl)
        self.assertIsInstance(stmt.value, String)
        self.assertEqual(stmt.value.value, "hello")

    def test_auto_boolean(self):
        code = """
            x: auto = true;
        """
        ast = self.parse(code)
        stmt = ast.body[0]
        self.assertIsInstance(stmt, AutoDecl)
        self.assertIsInstance(stmt.value, Boolean)
        self.assertEqual(stmt.value.value, True)

    def test_auto_null(self):
        code = """
            x: auto = null;
        """
        ast = self.parse(code)
        stmt = ast.body[0]
        self.assertIsInstance(stmt, AutoDecl)
        self.assertIsInstance(stmt.value, VarLoc)

    def test_auto_void(self):
        code = """
            x: auto = void;
        """
        ast = self.parse(code)
        stmt = ast.body[0]
        self.assertIsInstance(stmt, AutoDecl)
        self.assertIsInstance(stmt.value, SimpleType)
        self.assertEqual(stmt.value.name, "undefined")

    # Errors

    def test_auto_no_value(self):
        code = """
            x: auto;
        """
        self.parse(code)
        self.assertTrue(has_error(ParserError.UNEXPECTED_TOKEN))
