import unittest
from parser import Parser
from parser.model import *

from scanner import Lexer
from semantic import Check, SemanticError
from utils import clear_errors, errors_detected, has_error


class TestAssignment(unittest.TestCase):
    def setUp(self):
        self.lexer = Lexer()
        self.parser = Parser()
        clear_errors()

    def semantic(self, code):
        tokens = self.lexer.tokenize(code)
        ast = self.parser.parse(tokens)
        return Check.checker(ast)

    def test_assign_integer(self):
        code = "x: auto = 42;"
        env = self.semantic(code)
        decl = env.get("x")
        self.assertFalse(errors_detected())
        self.assertEqual(decl.type.name, "integer")
        self.assertIsInstance(decl.value, Integer)
        self.assertEqual(decl.value.value, 42)

    def test_assign_float(self):
        code = "pi: auto = 3.14;"
        env = self.semantic(code)
        decl = env.get("pi")
        self.assertEqual(decl.type.name, "float")
        self.assertIsInstance(decl.value, Float)
        self.assertAlmostEqual(decl.value.value, 3.14)

    def test_assign_string(self):
        code = 'msg: auto = "hello";'
        env = self.semantic(code)
        decl = env.get("msg")
        self.assertFalse(errors_detected())

    def test_assign_char(self):
        code = "letter: auto = 'a';"
        env = self.semantic(code)
        decl = env.get("letter")
        self.assertFalse(errors_detected())

    def test_assign_boolean_true(self):
        code = "flag: auto = true;"
        env = self.semantic(code)
        decl = env.get("flag")
        self.assertEqual(decl.type.name, "boolean")
        self.assertIsInstance(decl.value, Boolean)
        self.assertTrue(decl.value.value)

    def test_complex(self):
        code = "x: auto = (true || false) && (true || false);"
        env = self.semantic(code)
        decl = env.get("x")
        self.assertIsNotNone(decl)
        self.assertEqual(decl.type.name, "boolean")
        self.assertFalse(errors_detected())

    def test_re_assign(self):
        code = "main: function void () = {x: auto = 42;  x = 1; }"
        env = self.semantic(code)
        decl = env.get("main")
        decl = decl.env.get("x")
        self.assertFalse(errors_detected())
        self.assertIsNotNone(decl)
        self.assertEqual(decl.type.name, "integer")
        self.assertIsInstance(decl.value, Integer)

    def test_array(self):
        code = "x: auto = {1, 2, 3};"
        env = self.semantic(code)
        decl = env.get("x")
        self.assertIsNotNone(decl)
        self.assertIsInstance(decl.type, ArrayType)
        self.assertEqual(decl.type.size, 3)
        self.assertEqual(decl.type.base.name, "integer")
        self.assertFalse(errors_detected())

    def assertError(self, code, expected_error):
        self.semantic(code)
        self.assertTrue(errors_detected())
        self.assertTrue(has_error(expected_error))

    def test_bad_re_type(self):
        code = "x: auto = 42; main: function void () = {x = false;}"
        self.assertError(code, SemanticError.MISMATCH_ASSIGNMENT)

    def test_bad_re_type_array(self):
        code = """
                x: auto = {1, 2, 3};

                fn: function array[] float();

                main: function void () = {
                    x = fn();
                }
            """
        self.assertError(code, SemanticError.MISMATCH_ASSIGNMENT)

    def test_bad_item_array(self):
        code = """
                x: auto = {1, 2, 3.3};
            """
        self.assertError(code, SemanticError.MISMATCH_ARRAY_ASSIGNMENT)
