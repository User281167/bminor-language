import unittest
from parser import Parser, ParserError
from scanner import Lexer
from parser.model import *
from utils.errors import errors_detected, clear_errors, has_error, get_errors


class TestIncDecErrors(unittest.TestCase):
    def setUp(self):
        clear_errors()
        self.lexer = Lexer()
        self.parser = Parser()

    def parse(self, code):
        tokens = self.lexer.tokenize(code)
        return self.parser.parse(tokens)

    def test_inc_dec_error(self):
        self.parse("++[]")
        self.assertTrue(errors_detected())
        self.assertTrue(has_error(ParserError.INVALID_INC_DEC))

    def test_inc_dec_error2(self):
        self.parse("{}++")
        self.assertTrue(errors_detected())
        self.assertTrue(has_error(ParserError.INVALID_STATEMENT))

    def test_inc_dec_error3(self):
        self.parse("++&&")
        self.assertTrue(errors_detected())
        self.assertTrue(has_error(ParserError.INVALID_INC_DEC))

    def test_dec_on_operator(self):
        self.parse("--`")
        self.assertTrue(errors_detected())
        self.assertTrue(has_error(ParserError.INVALID_INC_DEC))

    def test_inc_on_unfinished_expression(self):
        self.parse("++(")
        self.assertTrue(errors_detected())
        self.assertTrue(has_error(ParserError.INVALID_INC_DEC))

    def test_dec_on_unfinished_expression(self):
        self.parse("--()")
        self.assertTrue(errors_detected())
        self.assertTrue(has_error(ParserError.INVALID_INC_DEC))

    def test_inc_on_missing_expression(self):
        self.parse("++(2+1)")
        self.assertTrue(errors_detected())
        self.assertTrue(has_error(ParserError.INVALID_INC_DEC))

    def test_dec_on_missing_expression(self):
        self.parse("--")
        self.assertTrue(errors_detected())
        self.assertTrue(has_error(ParserError.INVALID_INC_DEC))

    def test_inc_on_comma(self):
        self.parse("++,,")
        self.assertTrue(errors_detected())
        self.assertTrue(has_error(ParserError.INVALID_INC_DEC))

    def test_dec_on_semicolon(self):
        self.parse("--;")
        self.assertTrue(errors_detected())
        self.assertTrue(has_error(ParserError.INVALID_INC_DEC))

    def test_inc_on_array_missing_index(self):
        self.parse("arr[]++;")
        self.assertTrue(errors_detected())
        self.assertTrue(has_error(ParserError.INVALID_ARRAY_SYNTAX))

    def test_dec_on_array_missing_index(self):
        self.parse("--arr[];")
        self.assertTrue(errors_detected())
        self.assertTrue(has_error(ParserError.INVALID_INC_DEC))
