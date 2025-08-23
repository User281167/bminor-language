import unittest
from scanner import Lexer, LexerError, TokenType


class TestInvalidInputs(unittest.TestCase):
    def setUp(self):
        self.lexer = Lexer()

    def test_utf8_illegal_characters(self):
        # Greek pi, Cyrillic a, emoji, etc.
        for ch in ["π", "λ", "ж", "😀", "©"]:
            tokens = list(self.lexer.tokenize(ch))
            self.assertEqual(len(tokens), 1)
            self.assertEqual(
                tokens[0].type, LexerError.ILLEGAL_CHARACTER.value)

    def test_keywords_with_utf8(self):
        # Replace 'i' with Cyrillic 'і' in 'if', etc.
        tokens = list(self.lexer.tokenize("іf whіle truе fаlse"))
        self.assertTrue(all(t.type == LexerError.ILLEGAL_CHARACTER.value or t.type ==
                        TokenType.ID.value for t in tokens))

        # Invalid: starts with number, should split into INTEGER_LITERAL and ID
        tokens = list(self.lexer.tokenize("9abc"))
        self.assertEqual(len(tokens), 2)
        self.assertEqual(tokens[0].type, TokenType.INTEGER_LITERAL.value)
        self.assertEqual(tokens[1].type, TokenType.ID.value)

    def test_malformed_float(self):
        tokens = list(self.lexer.tokenize("3.14."))
        self.assertTrue(
            any(t.type == LexerError.UNEXPECTED_TOKEN.value for t in tokens))

    def test_malformed_id(self):
        tokens = list(self.lexer.tokenize("9abc"))
        self.assertEqual(tokens[0].type, TokenType.INTEGER_LITERAL.value)
        self.assertEqual(tokens[1].type, TokenType.ID.value)

    def test_unexpected_symbols(self):
        for ch in ["@", "$", "#", "~"]:
            tokens = list(self.lexer.tokenize(ch))
            self.assertEqual(len(tokens), 1)
            self.assertEqual(
                tokens[0].type, LexerError.ILLEGAL_CHARACTER.value)

    def test_invalid_operator_utf8(self):
        # ≤, ≥, ≠ are not valid operators
        for ch in ["≤", "≥", "≠"]:
            tokens = list(self.lexer.tokenize(ch))
            self.assertEqual(len(tokens), 1)
            self.assertEqual(
                tokens[0].type, LexerError.ILLEGAL_CHARACTER.value)
