import unittest
from utils import capture_lexer_log
from scanner import Lexer, LexerError, TokenType, OperatorType


class TestInvalidInputs(unittest.TestCase):
    def test_illegal_character(self):
        log, tokens = capture_lexer_log("@")
        self.assertIn(LexerError.ILLEGAL_CHARACTER.value, log)
        self.assertEqual(len(tokens), 1)

    def test_illegal_utf8_character(self):
        log, tokens = capture_lexer_log("π")
        self.assertIn(LexerError.ILLEGAL_CHARACTER.value, log)
        self.assertEqual(len(tokens), 1)

    def test_unexpected_symbol(self):
        log, tokens = capture_lexer_log("$")
        self.assertIn(LexerError.ILLEGAL_CHARACTER.value, log)
        self.assertEqual(len(tokens), 1)

    def test_malformed_id(self):
        log, tokens = capture_lexer_log("9abc")
        # Should tokenize 9 as integer, abc as ID
        self.assertEqual(len(tokens), 2)
        self.assertEqual(tokens[0].type, TokenType.INTEGER_LITERAL.value)
        self.assertEqual(tokens[1].type, TokenType.ID.value)

    def test_malformed_operator(self):
        log, tokens = capture_lexer_log("===")
        # Should tokenize == as EQ, = as literal
        self.assertEqual(len(tokens), 2)
        self.assertEqual(tokens[0].type, OperatorType.EQ.value)
        self.assertEqual(tokens[1].type, '=')

    def test_utf8_similar_operators(self):
        # Use Cyrillic '≤' (U+2264) and '≥' (U+2265), which should NOT match
        test_input = "≤ ≥"
        log, tokens = capture_lexer_log(test_input)
        # Should tokenize as two separate tokens as bad input
        self.assertEqual(len(tokens), 2)
        self.assertIn(LexerError.ILLEGAL_CHARACTER.value, log)
