import unittest
from parser import Parser
from parser.model import *

from scanner import Lexer
from semantic.checker import Check
from utils import clear_errors, errors_detected


class TestFuncCall(unittest.TestCase):
    def setUp(self):
        self.lexer = Lexer()
        self.parser = Parser()
        clear_errors()

    def semantic(self, code):
        tokens = self.lexer.tokenize(code)
        ast = self.parser.parse(tokens)
        return Check.checker(ast)

    def test_func_call_no_args(self):
        code = """
        main: function integer ();
        result: integer = main();
        """
        env = self.semantic(code)
        decl = env.get("result")
        self.assertEqual(decl.type.name, "integer")

    def test_func_call_one_int_arg(self):
        code = """
        add_one: function integer (x: integer);
        a: integer = add_one(5);
        """
        env = self.semantic(code)
        decl = env.get("a")
        self.assertEqual(decl.type.name, "integer")

    def test_func_call_multiple_args(self):
        code = """
        sum: function integer (x: integer, y: integer);
        total: integer = sum(3, 4);
        """
        env = self.semantic(code)
        decl = env.get("total")
        self.assertEqual(decl.type.name, "integer")

    def test_func_call_mixed_types(self):
        code = """
        format: function string (n: integer, flag: boolean);
        msg: string = format(10, true);
        """
        env = self.semantic(code)
        decl = env.get("msg")
        self.assertEqual(decl.type.name, "string")

    def test_func_call_array_return(self):
        code = """
        get_data: function array[] integer ();
        data: array[5] integer;

        main: function void() = {
            data = get_data();
        }
        """
        env = self.semantic(code)
        decl = env.get("data")

        self.assertEqual(decl.type.base.name, "integer")
        self.assertIsInstance(decl.type, ArrayType)
        self.assertEqual(decl.type.size.value, 5)

    def test_func_call_nested(self):
        code = """
        double: function integer (x: integer);
        a: integer = double(3) + 1;
        """
        env = self.semantic(code)
        decl = env.get("a")
        self.assertEqual(decl.type.name, "integer")

    def test_func_call_array_size(self):
        code = """
        SIZE: integer = 1;
        numbers: array [SIZE] integer = {0};

        find_max: function integer (arr: array [] integer, size: integer);

        main: function integer () = {
            max: integer = find_max(numbers, SIZE);
        }
        """
        self.semantic(code)
        self.assertFalse(errors_detected())
