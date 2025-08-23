import unittest
from scanner import Lexer, LexerError, TokenType, OperatorType
import logging
from io import StringIO


class TestInvalidInputs(unittest.TestCase):
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

    def test_illegal_character(self):
        log, tokens = self.capture_lexer_log("@")
        self.assertIn(LexerError.ILLEGAL_CHARACTER.value, log)
        self.assertEqual(len(tokens), 1)

    def test_illegal_utf8_character(self):
        log, tokens = self.capture_lexer_log("π")
        self.assertIn(LexerError.ILLEGAL_CHARACTER.value, log)
        self.assertEqual(len(tokens), 1)

    def test_unexpected_symbol(self):
        log, tokens = self.capture_lexer_log("$")
        self.assertIn(LexerError.ILLEGAL_CHARACTER.value, log)
        self.assertEqual(len(tokens), 1)

    def test_malformed_id(self):
        log, tokens = self.capture_lexer_log("9abc")
        # Should tokenize 9 as integer, abc as ID
        self.assertEqual(len(tokens), 2)
        self.assertEqual(tokens[0].type, TokenType.INTEGER_LITERAL.value)
        self.assertEqual(tokens[1].type, TokenType.ID.value)

    def test_malformed_operator(self):
        log, tokens = self.capture_lexer_log("===")
        # Should tokenize == as EQ, = as literal
        self.assertEqual(len(tokens), 2)
        self.assertEqual(tokens[0].type, OperatorType.EQ.value)
        self.assertEqual(tokens[1].type, '=')

    def test_utf8_similar_operators(self):
        # Use Cyrillic '≤' (U+2264) and '≥' (U+2265), which should NOT match
        test_input = "≤ ≥"
        log, tokens = self.capture_lexer_log(test_input)
        # Should tokenize as two separate tokens as bad input
        self.assertEqual(len(tokens), 2)
        self.assertIn(LexerError.ILLEGAL_CHARACTER.value, log)

    def test_utf8_incorrect_operator(self):
        # Use Cyrillic '≠' (U+2260) which should NOT match '!='
        test_input = "≠"
        log, tokens = self.capture_lexer_log(test_input)
        self.assertEqual(len(tokens), 1)
        self.assertIn(LexerError.ILLEGAL_CHARACTER.value, log)
