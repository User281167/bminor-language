import unittest
from parser import Parser, ParserError
from scanner import Lexer
from parser.model import *
from utils.errors import clear_errors, errors_detected, has_error


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
        self.assertTrue(has_error(ParserError.MISSING_STATEMENT))

    def test_assign_no_type(self):
        code = "x: = 42;"
        self.parse(code)
        self.assertEqual(errors_detected(), 1)
        self.assertTrue(has_error(ParserError.INVALID_ASSIGNMENT))

    def test_assign_no_name(self):
        code = ": integer = 42;"
        self.parse(code)
        self.assertEqual(errors_detected(), 1)
        self.assertTrue(has_error(ParserError.UNEXPECTED_COLON))

    def test_assign_float_no_value(self):
        code = "f: float = ;"
        self.parse(code)
        self.assertEqual(errors_detected(), 1)
        self.assertTrue(has_error(ParserError.MISSING_STATEMENT))

    def test_assign_string_no_value(self):
        code = 's: string = ;'
        self.parse(code)
        self.assertEqual(errors_detected(), 1)
        self.assertTrue(has_error(ParserError.MISSING_STATEMENT))

    def test_assign_boolean_no_value(self):
        code = "b: boolean = ;"
        self.parse(code)
        self.assertEqual(errors_detected(), 1)
        self.assertTrue(has_error(ParserError.MISSING_STATEMENT))

    def test_assign_char_no_value(self):
        code = "c: char = ;"
        self.parse(code)
        self.assertEqual(errors_detected(), 1)
        self.assertTrue(has_error(ParserError.MISSING_STATEMENT))

    def test_assign_inc_no_value(self):
        code = "x: integer = ++;"
        self.parse(code)
        self.assertEqual(errors_detected(), 1)
        self.assertTrue(has_error(ParserError.MISSING_STATEMENT))

    def test_assign_dec_no_value(self):
        code = "x: integer = --;"
        self.parse(code)
        self.assertEqual(errors_detected(), 1)
        self.assertTrue(has_error(ParserError.MISSING_STATEMENT))

    def test_assign_inc_no_location(self):
        code = "++;"
        self.parse(code)
        self.assertEqual(errors_detected(), 1)
        self.assertTrue(has_error(ParserError.INVALID_INC_DEC))

    def test_assign_dec_no_location(self):
        code = "--;"
        self.parse(code)
        self.assertEqual(errors_detected(), 1)
        self.assertTrue(has_error(ParserError.INVALID_INC_DEC))

    def test_assign_inc_no_postfix(self):
        code = "x: integer = ++;"
        self.parse(code)
        self.assertEqual(errors_detected(), 1)
        self.assertTrue(has_error(ParserError.MISSING_STATEMENT))

    def test_assign_dec_no_postfix(self):
        code = "x: integer = --;"
        self.parse(code)
        self.assertTrue(has_error(ParserError.MISSING_STATEMENT))

    def test_assign_no_expr(self):
        code = "x: integer = ;"
        self.parse(code)
        self.assertEqual(errors_detected(), 1)
        self.assertTrue(has_error(ParserError.MISSING_STATEMENT))
