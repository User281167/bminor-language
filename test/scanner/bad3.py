import unittest
from scanner import Lexer, LexerError, TokenType
import logging
from io import StringIO


class TestInvalidInputs(unittest.TestCase):
    def setUp(self):
        self.lexer = Lexer()

    def capture_lexer_log(self, input_text):
        stream = StringIO()
        handler = logging.StreamHandler(stream)
        logger = logging.getLogger('lexer')
        logger.addHandler(handler)
        logger.setLevel(logging.ERROR)
        tokens = list(self.lexer.tokenize(input_text))
        handler.flush()
        logger.removeHandler(handler)
        return stream.getvalue(), tokens

    def test_illegal_character(self):
        log, tokens = self.capture_lexer_log("@")
        self.assertIn(LexerError.ILLEGAL_CHARACTER.value, log)
        self.assertEqual(len(tokens), 0)

    def test_illegal_utf8_character(self):
        log, tokens = self.capture_lexer_log("π")
        self.assertIn(LexerError.ILLEGAL_CHARACTER.value, log)
        self.assertEqual(len(tokens), 0)

    def test_unexpected_symbol(self):
        log, tokens = self.capture_lexer_log("$")
        self.assertIn(LexerError.ILLEGAL_CHARACTER.value, log)
        self.assertEqual(len(tokens), 0)

    def test_malformed_id(self):
        log, tokens = self.capture_lexer_log("9abc")
        # Should tokenize 9 as integer, abc as ID
        self.assertEqual(len(tokens), 2)
        self.assertEqual(tokens[0].type, TokenType.INTEGER.value)
        self.assertEqual(tokens[1].type, TokenType.ID.value)

    def test_malformed_operator(self):
        log, tokens = self.capture_lexer_log("===")
        # Should tokenize == as EQ, = as literal
        self.assertEqual(len(tokens), 2)
        self.assertEqual(tokens[0].type, TokenType.EQ.value)
        self.assertEqual(tokens[1].type, '=')

    def test_utf8_similar_operators(self):
        # Use Cyrillic '≤' (U+2264) and '≥' (U+2265), which should NOT match
        test_input = "≤ ≥"
        log, tokens = self.capture_lexer_log(test_input)
        self.assertEqual(len(tokens), 0)

        # Illegal character in logs 4 error messages
        self.assertIn(LexerError.ILLEGAL_CHARACTER.value, log)
