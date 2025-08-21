import unittest
import sys
import os
from io import StringIO
import logging


from scanner import Lexer, LexerError, lexer_logger, TokenType


class TestBadNumbers(unittest.TestCase):
    def setUp(self):
        self.lexer = Lexer()

    def capture_lexer_log(self, input_text):
        """Capture the lexer's log output and return it along with the tokens.

        The logger is reset after capturing the output.

        Args:
            input_text: The text to tokenize.

        Returns:
            A tuple of (log_output, tokens), where log_output is the string
            output of the logger during tokenization, and tokens is the list
            of tokens produced by the lexer.
        """
        stream = StringIO()
        handler = logging.StreamHandler(stream)
        logger = logging.getLogger('lexer')
        logger.addHandler(handler)
        logger.setLevel(logging.ERROR)

        tokens = list(self.lexer.tokenize(input_text))

        handler.flush()
        logger.removeHandler(handler)
        return stream.getvalue(), tokens

    def test_malformed_float(self):
        # error illegal because . no match float literal
        log, tokens = self.capture_lexer_log("3.14.")
        self.assertEqual(len(tokens), 1)
        self.assertIn(LexerError.ILLEGAL_CHARACTER.value, log)

    def test_malformed_float_with_leading_zeros(self):
        # error illegal because . no match float literal
        log, tokens = self.capture_lexer_log("0003.14.")
        self.assertEqual(len(tokens), 1)
        self.assertIn(LexerError.ILLEGAL_CHARACTER.value, log)

    def test_bad_notation(self):
        # match float and ID
        log, tokens = self.capture_lexer_log("3.14e")
        self.assertEqual(len(tokens), 2)

        expected = [
            (TokenType.FLOAT.value, 3.14),
            (TokenType.ID.value, 'e')
        ]

        for i in range(len(tokens)):
            self.assertEqual(tokens[i].value, expected[i][1])
            self.assertEqual(tokens[i].type, expected[i][0])

    def test_bad_notation_minus(self):
        # no get a float because no math regex
        # so lexer only get valid tokens for this case float, ID, minus
        log, tokens = self.capture_lexer_log("3.14e-")
        self.assertEqual(len(tokens), 3)

        expected = [
            (TokenType.FLOAT.value, 3.14),
            (TokenType.ID.value, 'e'),
            ('-', '-')
        ]

        for i in range(len(tokens)):
            self.assertEqual(tokens[i].value, expected[i][1])
            self.assertEqual(tokens[i].type, expected[i][0])

    def test_bad_notations_plus(self):
        # no get a float because no math regex
        # so lexer only get valid tokens for this case float, ID, plus
        log, tokens = self.capture_lexer_log("3.14e+")
        self.assertEqual(len(tokens), 3)

        expected = [
            (TokenType.FLOAT.value, 3.14),
            (TokenType.ID.value, 'e'),
            ('+', '+')
        ]

        for i in range(len(tokens)):
            self.assertEqual(tokens[i].value, expected[i][1])
            self.assertEqual(tokens[i].type, expected[i][0])

    def test_bad_notation_with_leading_zeros(self):
        # match float and ID
        log, tokens = self.capture_lexer_log("0003.14e")
        self.assertEqual(len(tokens), 2)

        expected = [
            (TokenType.FLOAT.value, 3.14),
            (TokenType.ID.value, 'e')
        ]

        for i in range(len(tokens)):
            self.assertEqual(tokens[i].value, expected[i][1])
            self.assertEqual(tokens[i].type, expected[i][0])

    def test_bad_float_trailing_literals(self):
        log, tokens = self.capture_lexer_log("3.14e+-2")

        self.assertEqual(len(tokens), 5)

        expected = [
            (TokenType.FLOAT.value, 3.14),
            (TokenType.ID.value, 'e'),
            ('+', '+'),
            ('-', '-'),
            (TokenType.INTEGER.value, 2)
        ]

        for i in range(len(tokens)):
            self.assertEqual(tokens[i].value, expected[i][1])
            self.assertEqual(tokens[i].type, expected[i][0])

    def test_bad_integer_trailing_literals(self):
        log, tokens = self.capture_lexer_log("42++-2")

        self.assertEqual(len(tokens), 4)

        expected = [
            (TokenType.INTEGER.value, 42),
            (TokenType.INCREMENT.value, '++'),
            ('-', '-'),
            (TokenType.INTEGER.value, 2)
        ]

        for i in range(len(tokens)):
            self.assertEqual(tokens[i].value, expected[i][1])
            self.assertEqual(tokens[i].type, expected[i][0])

    def test_bad_integer_trailing_literals_no_space(self):
        log, tokens = self.capture_lexer_log("42-- -2")

        self.assertEqual(len(tokens), 4)

        expected = [
            (TokenType.INTEGER.value, 42),
            (TokenType.DECREMENT.value, '--'),
            ('-', '-'),
            (TokenType.INTEGER.value, 2)
        ]

        for i in range(len(tokens)):
            self.assertEqual(tokens[i].value, expected[i][1])
            self.assertEqual(tokens[i].type, expected[i][0])
