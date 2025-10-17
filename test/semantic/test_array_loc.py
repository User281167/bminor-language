import unittest
from parser import Parser
from scanner import Lexer
from parser.model import *
from semantic.checker import Check
from utils import errors_detected
from utils.errors import clear_errors


class TestArrayLocValid(unittest.TestCase):
    def setUp(self):
        self.lexer = Lexer()
        self.parser = Parser()
        clear_errors()

    def semantic(self, code):
        tokens = self.lexer.tokenize(code)
        ast = self.parser.parse(tokens)
        return Check.checker(ast)

    def assertArrayLoc(self, code, array_name, expected_type):
        env = self.semantic(code)
        self.assertFalse(errors_detected())
        decl = env.get("a")
        self.assertIsNotNone(decl)
        self.assertEqual(decl.name, "a")
        self.assertEqual(decl.type.name, expected_type)

    def test_access_index_zero(self):
        code = """
        isprime: array [10] boolean;
        a: boolean = isprime[0];
        """
        self.assertArrayLoc(code, "isprime", "boolean")

    def test_access_index_middle(self):
        code = """
        isprime: array [10] boolean;
        a: boolean = isprime[5];
        """
        self.assertArrayLoc(code, "isprime", "boolean")

    def test_access_index_last(self):
        code = """
        isprime: array [10] boolean;
        a: boolean = isprime[9];
        """
        self.assertArrayLoc(code, "isprime", "boolean")

    def test_access_index_from_variable(self):
        code = """
        isprime: array [10] boolean;
        i: integer = 3;
        a: boolean = isprime[i];
        """
        self.assertArrayLoc(code, "isprime", "boolean")

    def test_access_index_from_unary(self):
        code = """
        isprime: array [10] boolean;
        a: boolean = isprime[+2];
        """
        self.assertArrayLoc(code, "isprime", "boolean")

    def test_access_index_from_negative_variable_but_not_evaluated(self):
        code = """
        isprime: array [10] boolean;
        i: integer = 1;
        a: boolean = isprime[-i];
        """
        # No error because index is not resolved statically
        self.assertArrayLoc(code, "isprime", "boolean")

    def test_access_index_from_variable_with_unknown_size(self):
        code = """
        N: integer;
        isprime: array [N] boolean;
        i: integer = 5;
        a: boolean = isprime[i];
        """
        self.assertArrayLoc(code, "isprime", "boolean")
