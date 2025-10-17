import unittest
from parser import Parser, ParserError
from parser.model import *

from scanner import Lexer
from utils.errors import clear_errors, errors_detected, has_error


class TestArrayAssignmentError(unittest.TestCase):
    def setUp(self):
        self.lexer = Lexer()
        self.parser = Parser()
        clear_errors()

    def parse(self, code):
        tokens = self.lexer.tokenize(code)
        return self.parser.parse(tokens)

    def test_assign_missing_bracket(self):
        code = "x[2 = 2;"
        self.parse(code)
        self.assertEqual(errors_detected(), 1)
        self.assertTrue(has_error(ParserError.INVALID_ARRAY_SYNTAX))

    def test_assign_empty_index(self):
        code = "x[] = 5;"
        self.parse(code)
        self.assertEqual(errors_detected(), 1)
        self.assertTrue(has_error(ParserError.INVALID_ARRAY_SYNTAX))

    def test_assign_missing_operator(self):
        code = "x[0] 5;"
        self.parse(code)
        self.assertEqual(errors_detected(), 1)
        self.assertTrue(has_error(ParserError.INVALID_ARRAY_SYNTAX))

    def test_assign_missing_value(self):
        code = "x[0] = ;"
        self.parse(code)
        self.assertEqual(errors_detected(), 1)
        self.assertTrue(has_error(ParserError.INVALID_ARRAY_SYNTAX))

    def test_assign_incomplete_index_expr(self):
        code = "x[1 + ] = 3;"
        self.parse(code)
        self.assertEqual(errors_detected(), 1)
        self.assertTrue(has_error(ParserError.INVALID_ARRAY_SYNTAX))

    def test_assign_incomplete_value_expr(self):
        code = "x[0] = a * ;"
        self.parse(code)
        self.assertEqual(errors_detected(), 1)
        self.assertTrue(has_error(ParserError.INVALID_ARRAY_SYNTAX))

    def test_assign_index_no_closing_bracket(self):
        code = "x[1 = 2;"
        self.parse(code)
        self.assertEqual(errors_detected(), 1)
        self.assertTrue(has_error(ParserError.INVALID_ARRAY_SYNTAX))

    def test_assign_double_equal(self):
        code = "x[0] == 5;"
        self.parse(code)
        self.assertEqual(errors_detected(), 1)
        self.assertTrue(has_error(ParserError.INVALID_ARRAY_SYNTAX))

    def test_assign_curly_brackets(self):
        code = "x{0} = 2;"
        self.parse(code)
        self.assertEqual(errors_detected(), 1)
        self.assertTrue(has_error(ParserError.INVALID_STATEMENT))

    def test_assign_double_brackets(self):
        code = "x[[0]] = 2;"
        self.parse(code)
        self.assertEqual(errors_detected(), 1)
        self.assertTrue(has_error(ParserError.INVALID_ARRAY_SYNTAX))

    def test_assign_parentheses_index(self):
        code = "x(0) = 2;"
        self.parse(code)
        self.assertEqual(errors_detected(), 1)
        self.assertTrue(has_error(ParserError.INCOMPLETE_FUNCTION_DECLARATION))

    # def test_assign_boolean_index(self):
    #     code = "x[true] = 2;"
    #     self.parse(code)
    #     # parser lo acepta, semántico lo rechaza
    #     self.assertEqual(errors_detected(), 1)

    # def test_assign_invalid_value_expr(self):
    #     code = "x[0] = false + 1;"
    #     self.parse(code)
    #     # parser lo acepta, semántico lo rechaza
    #     self.assertEqual(errors_detected(), 0)

    # def test_assign_string_index(self):
    #     code = "x[\"index\"] = 2;"
    #     self.parse(code)
    #     # parser lo acepta, semántico lo rechaza
    #     self.assertEqual(errors_detected(), 1)

    def test_assign_incomplete_index_expr(self):
        code = "x[1 + ] = 2;"
        self.parse(code)
        self.assertEqual(errors_detected(), 1)
        self.assertTrue(has_error(ParserError.INVALID_ARRAY_SYNTAX))

    def test_assign_invalid_operator(self):
        code = "x[0] := 2;"
        self.parse(code)
        self.assertEqual(errors_detected(), 1)
        self.assertTrue(has_error(ParserError.INVALID_ARRAY_SYNTAX))
