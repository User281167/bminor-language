import unittest
from scanner import Lexer, LexerError, TokenType


class TestInvalidArrayAndLoopTokens(unittest.TestCase):
    def setUp(self):
        self.lexer = Lexer()

    def test_invalid_bracket_in_array_declaration(self):
        # Use a non-ASCII bracket (e.g., full-width bracket)
        tokens = list(self.lexer.tokenize('a: array ［5］ integer;'))
        # Should produce ILLEGAL_CHARACTER for both brackets
        self.assertTrue(
            any(t.type == LexerError.ILLEGAL_CHARACTER.value for t in tokens)
        )

    def test_array_size_with_unexpected_chars(self):
        tokens = list(self.lexer.tokenize('x: array [@5#] integer;'))
        # Should detect @ and # as illegal characters
        self.assertTrue(
            any(t.type == LexerError.ILLEGAL_CHARACTER.value for t in tokens)
        )

    def test_array_index_with_invalid_chars(self):
        tokens = list(self.lexer.tokenize('arr[¢123]'))
        # Should detect ¢ as an illegal character
        self.assertTrue(
            any(t.type == LexerError.ILLEGAL_CHARACTER.value for t in tokens)
        )

    def test_malformed_for_loop_tokens(self):
        tokens = list(self.lexer.tokenize('for(i=0 $$ i<10 i++)'))
        # Should detect $ as illegal characters
        self.assertTrue(
            any(t.type == LexerError.ILLEGAL_CHARACTER.value for t in tokens)
        )

    def test_invalid_increment_operator(self):
        tokens = list(self.lexer.tokenize('for(i=0; i<10; i+±)'))
        # Should detect ± as illegal character
        self.assertTrue(
            any(t.type == LexerError.ILLEGAL_CHARACTER.value for t in tokens)
        )

    def test_array_declaration_unexpected_tokens(self):
        tokens = list(self.lexer.tokenize('x: array [5] integer¥;'))
        # Should detect ¥ as illegal character
        self.assertTrue(
            any(t.type == LexerError.ILLEGAL_CHARACTER.value for t in tokens)
        )

    def test_for_loop_invalid_separator(self):
        tokens = list(self.lexer.tokenize('for(i=0¦i<10¦i++)'))
        # Should detect ¦ as illegal character
        self.assertTrue(
            any(t.type == LexerError.ILLEGAL_CHARACTER.value for t in tokens)
        )

    def test_array_with_emoji_index(self):
        tokens = list(self.lexer.tokenize('arr[👍]'))
        # Should detect emoji as illegal character
        self.assertTrue(
            any(t.type == LexerError.ILLEGAL_CHARACTER.value for t in tokens)
        )

    def test_array_size_with_unexpected_chars(self):
        tokens = list(self.lexer.tokenize('x: array [@5#] integer;'))
        # Should detect @ and # as illegal characters
        self.assertTrue(
            any(t.type == LexerError.ILLEGAL_CHARACTER.value for t in tokens)
        )

    def test_array_index_with_invalid_chars(self):
        tokens = list(self.lexer.tokenize('arr[¢123]'))
        # Should detect ¢ as an illegal character
        self.assertTrue(
            any(t.type == LexerError.ILLEGAL_CHARACTER.value for t in tokens)
        )

    def test_malformed_for_loop_tokens(self):
        tokens = list(self.lexer.tokenize('for(i=0 $$ i<10 i++)'))
        # Should detect $ as illegal characters
        self.assertTrue(
            any(t.type == LexerError.ILLEGAL_CHARACTER.value for t in tokens)
        )

    def test_invalid_increment_operator(self):
        tokens = list(self.lexer.tokenize('for(i=0; i<10; i+±)'))
        # Should detect ± as illegal character
        self.assertTrue(
            any(t.type == LexerError.ILLEGAL_CHARACTER.value for t in tokens)
        )

    def test_array_declaration_unexpected_tokens(self):
        tokens = list(self.lexer.tokenize('x: array [5] integer¥;'))
        # Should detect ¥ as illegal character
        self.assertTrue(
            any(t.type == LexerError.ILLEGAL_CHARACTER.value for t in tokens)
        )

    def test_for_loop_with_invalid_identifier_utf8(self):
        tokens = list(self.lexer.tokenize('for(и=0; и<10; и++) { print и; }'))
        # Cyrillic 'и' should produce ILLEGAL_CHARACTER tokens
        self.assertTrue(
            any(t.type == LexerError.ILLEGAL_CHARACTER.value for t in tokens))

    def test_for_loop_with_float(self):
        tokens = list(self.lexer.tokenize('for(123.) { print 1; }'))
        # Should tokenize FOR, (, FLOAT_LITERAL, ), {, PRINT, INTEGER_LITERAL, ;, }
        expected_types = [
            TokenType.FOR.value, '(', TokenType.FLOAT_LITERAL.value, ')', '{', TokenType.PRINT.value, TokenType.INTEGER_LITERAL.value, ';', '}'
        ]
        self.assertEqual([t.type for t in tokens], expected_types)

    def test_non_keyword_while(self):
        tokens = list(self.lexer.tokenize('Whiile(x) { print x; }'))
        # 'Whiile' is not a keyword, should be ID
        expected_types = [
            TokenType.ID.value, '(', TokenType.ID.value, ')', '{', TokenType.PRINT.value, TokenType.ID.value, ';', '}'
        ]
        self.assertEqual([t.type for t in tokens], expected_types)

    def test_non_keyword_do(self):
        tokens = list(self.lexer.tokenize('doo { print x; } while(x);'))
        # 'doo' is not a keyword, should be ID
        expected_types = [
            TokenType.ID.value, '{', TokenType.PRINT.value, TokenType.ID.value, ';', '}', TokenType.WHILE.value, '(', TokenType.ID.value, ')', ';'
        ]
        self.assertEqual([t.type for t in tokens], expected_types)
