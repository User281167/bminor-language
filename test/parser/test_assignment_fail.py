from errors import clear_errors, errors_detected
import unittest
from parser import Parser
from scanner import Lexer
from model import *


class TestAssignmentError(unittest.TestCase):
    def setUp(self):
        self.lexer = Lexer()
        self.parser = Parser()
        clear_errors()

    def parse(self, code):
        tokens = self.lexer.tokenize(code)
        return self.parser.parse(tokens)

    def test_assign_no_value(self):
        code = "x: integer = ;"
        self.parse(code)
        self.assertEqual(errors_detected(), 1)

    def test_assign_no_type(self):
        code = "x: = 42;"
        self.parse(code)
        self.assertEqual(errors_detected(), 1)

    def test_assign_no_name(self):
        code = ": integer = 42;"
        self.parse(code)
        self.assertEqual(errors_detected(), 1)

    def test_assign_float_no_value(self):
        code = "f: float = ;"
        self.parse(code)
        self.assertEqual(errors_detected(), 1)

    def test_assign_string_no_value(self):
        code = 's: string = ;'
        self.parse(code)
        self.assertEqual(errors_detected(), 1)

    def test_assign_boolean_no_value(self):
        code = "b: boolean = ;"
        self.parse(code)
        self.assertEqual(errors_detected(), 1)

    def test_assign_char_no_value(self):
        code = "c: char = ;"
        self.parse(code)
        self.assertEqual(errors_detected(), 1)

    def test_assign_inc_no_value(self):
        code = "x: integer = ++;"
        self.parse(code)
        self.assertEqual(errors_detected(), 1)

    def test_assign_dec_no_value(self):
        code = "x: integer = --;"
        self.parse(code)
        self.assertEqual(errors_detected(), 1)

    def test_assign_inc_no_location(self):
        code = "++;"
        self.parse(code)
        self.assertEqual(errors_detected(), 1)

    def test_assign_dec_no_location(self):
        code = "--;"
        self.parse(code)
        self.assertEqual(errors_detected(), 1)

    def test_assign_inc_no_postfix(self):
        code = "x: integer = ++;"
        self.parse(code)
        self.assertEqual(errors_detected(), 1)

    def test_assign_dec_no_postfix(self):
        code = "x: integer = --;"
        self.parse(code)
        self.assertEqual(errors_detected(), 1)

    def test_assign_no_expr(self):
        code = "x: integer = ;"
        self.parse(code)
        self.assertEqual(errors_detected(), 1)

    # def test_assign_empty_
