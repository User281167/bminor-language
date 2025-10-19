import unittest
from parser import Parser
from parser.model import *

from scanner import Lexer
from semantic.checker import Check
from utils import errors_detected
from utils.errors import clear_errors


class TestReturn(unittest.TestCase):
    def setUp(self):
        self.lexer = Lexer()
        self.parser = Parser()
        clear_errors()

    def semantic(self, code):
        tokens = self.lexer.tokenize(code)
        ast = self.parser.parse(tokens)
        return Check.checker(ast)

    def test_return_integer_literal(self):
        code = """
        sum: function integer() = {
            return 42;
        }
        """
        env = self.semantic(code)
        func = env.get("sum")
        self.assertEqual(func.return_type.name, "integer")

    def test_return_float_literal(self):
        code = """
        pi: function float() = {
            return 3.14;
        }
        """
        env = self.semantic(code)
        func = env.get("pi")
        self.assertEqual(func.return_type.name, "float")

    def test_return_boolean_literal(self):
        code = """
        is_ready: function boolean() = {
            return true;
        }
        """
        env = self.semantic(code)
        func = env.get("is_ready")
        self.assertEqual(func.return_type.name, "boolean")

    def test_return_char_literal(self):
        code = """
        get_letter: function char() = {
            return 'A';
        }
        """
        env = self.semantic(code)
        func = env.get("get_letter")
        self.assertEqual(func.return_type.name, "char")

    def test_return_string_literal(self):
        code = """
        greet: function string() = {
            return "hello";
        }
        """
        env = self.semantic(code)
        func = env.get("greet")
        self.assertEqual(func.return_type.name, "string")

    def test_return_expression(self):
        code = """
        double: function integer() = {
            return 21 + 21;
        }
        """
        env = self.semantic(code)
        func = env.get("double")
        self.assertEqual(func.return_type.name, "integer")

    def test_return_unary_expression(self):
        code = """
        negate: function integer() = {
            return -42;
        }
        """
        env = self.semantic(code)
        func = env.get("negate")
        self.assertEqual(func.return_type.name, "integer")

    def test_return_variable(self):
        code = """
        get_value: function float() = {
            x: float = 2.5;
            return x;
        }
        """
        env = self.semantic(code)
        func = env.get("get_value")
        self.assertEqual(func.return_type.name, "float")

    def test_return_var_out_scope(self):
        code = """
        x: float = 2.5;

        get_value: function float() = {
            return x;
        }
        """
        env = self.semantic(code)
        func = env.get("get_value")
        self.assertEqual(func.return_type.name, "float")

    def test_return_array_index(self):
        code = """
        my_arr: array [3] integer;
        get_value: function integer() = {
            return my_arr[2];
        }
        """

        env = self.semantic(code)
        func = env.get("get_value")
        self.assertEqual(func.return_type.name, "integer")
