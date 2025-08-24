import unittest
from scanner import Lexer, LexerError, lexer_logger, TokenType, OperatorType
import logging
from io import StringIO


class TestBadCharLiterals(unittest.TestCase):
    def setUp(self):
        self.lexer = Lexer()

    def capture_lexer_log(self, input_text):
        """Capture lexer error logs and return them with tokens"""
        stream = StringIO()
        handler = logging.StreamHandler(stream)
        logger = logging.getLogger('lexer')
        logger.addHandler(handler)
        logger.setLevel(logging.ERROR)
        tokens = list(self.lexer.tokenize(input_text))
        handler.flush()
        logger.removeHandler(handler)
        return stream.getvalue(), tokens

    # === MALFORMED CHAR LITERAL TESTS ===

    def test_empty_char_literal(self):
        """Test empty char literal ''"""
        # Should produce error for unterminated or malformed char
        # Check that we get an error token

        log, tokens = self.capture_lexer_log("''")
        self.assertIn(LexerError.MALFORMED_CHAR.value, log)

        error_tokens = [t for t in tokens if t.type ==
                        LexerError.MALFORMED_CHAR.value]

        self.assertGreater(len(error_tokens), 0)

    def test_multiple_chars_in_literal(self):
        """Test multiple characters in char literal 'ab'"""
        log, tokens = self.capture_lexer_log("'ab'")
        self.assertIn(LexerError.MALFORMED_CHAR.value, log)
        error_tokens = [t for t in tokens if t.type ==
                        LexerError.MALFORMED_CHAR.value]
        self.assertGreater(len(error_tokens), 0)

    def test_unterminated_char_literal(self):
        """Test unterminated char literal 'a"""
        log, tokens = self.capture_lexer_log("'a")
        expected = [
            LexerError.MALFORMED_CHAR.value,
            TokenType.ID.value  # a is treated as ID after error
        ]

        self.assertIn(LexerError.MALFORMED_CHAR.value, log)
        self.assertEqual([t.type for t in tokens], expected)

    def test_unterminated_escaped_char(self):
        # get ' malformed char token
        # get \ as illegal character
        log, tokens = self.capture_lexer_log("'\\")
        self.assertIn(LexerError.MALFORMED_CHAR.value, log)
        expected_types = [LexerError.MALFORMED_CHAR.value,
                          LexerError.ILLEGAL_CHARACTER.value]
        self.assertEqual([t.type for t in tokens], expected_types)

    def test_invalid_escape_sequence(self):
        """Test invalid escape sequences like '\\z'"""
        invalid_escapes = ['\\z', '\\q', '\\w', '\\1', '\\2']
        for escape in invalid_escapes:
            with self.subTest(escape=escape):
                log, tokens = self.capture_lexer_log(f"'{escape}'")
                # Should either be malformed char or unexpected token
                self.assertTrue(
                    LexerError.MALFORMED_CHAR.value in log or
                    LexerError.UNEXPECTED_TOKEN.value in log
                )

    def test_incomplete_hex_escape(self):
        """Test incomplete hex escapes"""
        incomplete_hex = ["'\\x'", "'\\x4'", "'\\xG'", "'\\x4G'"]
        for hex_test in incomplete_hex:
            with self.subTest(hex_escape=hex_test):
                log, tokens = self.capture_lexer_log(hex_test)
                self.assertIn(LexerError.MALFORMED_CHAR.value, log)

    # === ILLEGAL CHARACTER TESTS ===

    def test_utf8_characters(self):
        """Test UTF-8 characters that should be rejected"""
        utf8_chars = [
            'ñ', 'é', 'ü', 'ß',           # Latin characters
            'α', 'β', 'γ',                 # Greek letters
            '中', '文',                     # Chinese characters
            '🚀', '💻', '🔥',              # Emojis
            '©', '®', '™',                 # Symbols
        ]

        for char in utf8_chars:
            with self.subTest(utf8_char=char):
                log, tokens = self.capture_lexer_log(char)
                self.assertIn(LexerError.ILLEGAL_CHARACTER.value, log)
                error_tokens = [t for t in tokens if t.type ==
                                LexerError.ILLEGAL_CHARACTER.value]
                self.assertGreater(len(error_tokens), 0)

    def test_non_printable_ascii(self):
        """Test non-printable ASCII characters"""
        # ASCII 0-31 (except those that might be whitespace)
        for code in range(0, 32):
            # Skip tab, newline, carriage return if they're handled as whitespace
            if code not in [9, 10, 13]:
                char = chr(code)
                with self.subTest(ascii_code=code):
                    log, tokens = self.capture_lexer_log(char)
                    self.assertIn(LexerError.ILLEGAL_CHARACTER.value, log)

        # ASCII 127 (DEL)
        log, tokens = self.capture_lexer_log(chr(127))
        self.assertIn(LexerError.ILLEGAL_CHARACTER.value, log)

    def test_mixed_valid_invalid(self):
        """Test mixing valid tokens with invalid characters"""
        test_cases = [
            ("int x = 42; ñ", "valid code with UTF-8"),
            ("'a' + β", "char literal with Greek letter"),
            ("print 🚀;", "keyword with emoji"),
            ("float π = 3.14;", "valid syntax with pi symbol"),
        ]

        for test_input, desc in test_cases:
            with self.subTest(test=desc):
                log, tokens = self.capture_lexer_log(test_input)
                self.assertIn(LexerError.ILLEGAL_CHARACTER.value, log)
                # Should still tokenize the valid parts
                valid_tokens = [
                    t for t in tokens if not t.type.startswith('error')]
                self.assertGreater(len(valid_tokens), 0)

#     # === EDGE CASES ===

    def test_char_literal_at_eof(self):
        """Test unterminated char literal at end of file"""
        log, tokens = self.capture_lexer_log("int x = 'a")
        self.assertIn(LexerError.MALFORMED_CHAR.value, log)

    def test_multiple_errors_in_sequence(self):
        """Test multiple consecutive errors"""
        log, tokens = self.capture_lexer_log("ñβγ")
        # Should generate multiple illegal character errors
        error_count = log.count(LexerError.ILLEGAL_CHARACTER.value)
        self.assertGreaterEqual(error_count, 3)

    def test_char_with_high_ascii(self):
        """Test characters in extended ASCII range (128-255)"""
        high_ascii_chars = [chr(i) for i in range(128, 256)]
        for char in high_ascii_chars[:10]:  # Test first 10 to avoid huge test
            with self.subTest(char_code=ord(char)):
                log, tokens = self.capture_lexer_log(char)
                self.assertIn(LexerError.ILLEGAL_CHARACTER.value, log)

    def test_malformed_char_in_expression(self):
        """Test malformed char literals within valid expressions"""
        test_cases = [
            "int x = 'ab' + 5;",          # Multiple chars in literal
            "if (c == '') return;",       # Empty char literal
            "char c = '\\z';",            # Invalid escape
            "printf('%c', 'hello');",     # Multiple chars
        ]

        for test_case in test_cases:
            with self.subTest(expression=test_case):
                log, tokens = self.capture_lexer_log(test_case)
                self.assertIn(LexerError.MALFORMED_CHAR.value, log)
                # Should still parse other valid tokens
                valid_tokens = [
                    t for t in tokens if not t.type.startswith('error')]
                self.assertGreater(len(valid_tokens), 0)

    def test_error_recovery(self):
        """Test that lexer continues after errors"""
        log, tokens = self.capture_lexer_log("'bad β char' + 'good'")
        # should have malformed and illegal character errors
        self.assertIn(LexerError.MALFORMED_CHAR.value, log)
        self.assertIn(LexerError.ILLEGAL_CHARACTER.value, log)

    def test_illegal_utf8(self):
        # String with emoji and non-ascii chars
        for s in ["'🚀'", "'ñ'", "'é'"]:
            tokens = list(self.lexer.tokenize(s))
            print(f"\n\n---------------------{tokens}---------------------")
            self.assertTrue(
                any(t.type == LexerError.ILLEGAL_CHARACTER.value for t in tokens))
