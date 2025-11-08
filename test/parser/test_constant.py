import unittest
from parser import Parser, ParserError
from parser.model import *

from scanner import Lexer
from utils import clear_errors, has_error


class TestConstant(unittest.TestCase):
    def setUp(self):
        self.lexer = Lexer()
        self.parser = Parser()
        clear_errors()

    def parse(self, code):
        tokens = self.lexer.tokenize(code)
        return self.parser.parse(tokens)

    def test_constant_integer(self):
        code = """
            x: constant = 12;
        """
        ast = self.parse(code)
        stmt = ast.body[0]
        self.assertIsInstance(stmt, ConstantDecl)
        self.assertIsInstance(stmt.value, Integer)
        self.assertEqual(stmt.value.value, 12)

    def test_constant_string(self):
        code = """
            x: constant = "hello";
        """
        ast = self.parse(code)
        stmt = ast.body[0]
        self.assertIsInstance(stmt, ConstantDecl)
        self.assertIsInstance(stmt.value, String)
        self.assertEqual(stmt.value.value, "hello")

    def test_constant_boolean(self):
        code = """
            x: constant = true;
        """
        ast = self.parse(code)
        stmt = ast.body[0]
        self.assertIsInstance(stmt, ConstantDecl)
        self.assertIsInstance(stmt.value, Boolean)
        self.assertEqual(stmt.value.value, True)

    def test_constant_null(self):
        code = """
            x: constant = null;
        """
        ast = self.parse(code)
        stmt = ast.body[0]
        self.assertIsInstance(stmt, ConstantDecl)
        self.assertIsInstance(stmt.value, VarLoc)

    def test_constant_void(self):
        code = """
            x: constant = void;
        """
        ast = self.parse(code)
        stmt = ast.body[0]
        self.assertIsInstance(stmt, ConstantDecl)
        self.assertIsInstance(stmt.value, SimpleType)
        self.assertEqual(stmt.value.name, "undefined")

    # Errors

    def test_constant_no_value(self):
        code = """
            x: constant;
        """
        self.parse(code)
        self.assertTrue(has_error(ParserError.UNEXPECTED_TOKEN))

    def test_constant_array(self):
        code = """
            x: constant = {1, 2, 3};
        """
        ast = self.parse(code)
        stmt = ast.body[0]
        self.assertIsInstance(stmt, ConstantDecl)
        self.assertIsInstance(stmt.value, list)
