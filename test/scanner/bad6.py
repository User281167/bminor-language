import logging
import unittest
from io import StringIO

from scanner import Lexer, LexerError, TokenType


class TestBadStringLiterals(unittest.TestCase):
    def setUp(self):
        self.lexer = Lexer()

    def capture_lexer_log(self, input_text):
        """Capture lexer error logs and return them with tokens"""
        stream = StringIO()
        handler = logging.StreamHandler(stream)
        logger = logging.getLogger("lexer")
        logger.addHandler(handler)
        logger.setLevel(logging.ERROR)
        tokens = list(self.lexer.tokenize(input_text))
        handler.flush()
        logger.removeHandler(handler)
        return stream.getvalue(), tokens

    # === UTF-8/UNICODE TESTS ===
    def test_string_with_illegal_utf8_2(self):
        # String with emoji and non-ascii chars
        for s in ['"emoji 🚀"', '"ñandú"', '"你好"', '"αβγ"']:
            tokens = list(self.lexer.tokenize(s))
            self.assertTrue(
                any(t.type == LexerError.ILLEGAL_CHARACTER.value for t in tokens)
            )

    def test_string_with_illegal_utf8_3(self):
        # String with emoji and non-ascii chars
        for s in ['"🚀"', '"ñ"', '"你"', '"α"']:
            tokens = list(self.lexer.tokenize(s))
            self.assertTrue(
                any(t.type == LexerError.ILLEGAL_CHARACTER.value for t in tokens)
            )

    def test_string_with_illegal_utf8(self):
        """Test strings with UTF-8/Unicode characters (should be rejected if ASCII-only)"""
        utf8_strings = [
            '"emoji 🚀"',
            '"café"',
            '"niño"',
            '"Hello 世界"',
            '"Greek: αβγ"',
            '"Symbols: ©®™"',
        ]

        for test_string in utf8_strings:
            with self.subTest(string=test_string):
                log, tokens = self.capture_lexer_log(test_string)
                self.assertTrue(
                    any(t.type == LexerError.ILLEGAL_CHARACTER.value for t in tokens)
                )

    def test_string_with_high_ascii(self):
        """Test strings with extended ASCII characters (128-255)"""
        high_ascii_chars = ["é", "ñ", "ü", "ß", "¡", "¿"]

        for char in high_ascii_chars:
            test_string = f'"Hello {char}"'
            with self.subTest(char=char):
                log, tokens = self.capture_lexer_log(test_string)
                self.assertTrue(
                    any(t.type == LexerError.ILLEGAL_CHARACTER.value for t in tokens)
                )

    # === UNTERMINATED STRING TESTS ===

    def test_unterminated_string(self):
        """Test unterminated string literals"""
        unterminated_cases = [
            '"Hello world',  # Missing closing quote
            r'"Escaped quote \\',  # Missing final quote after escape
            '"Multi line',  # No closing quote
        ]

        for test_case in unterminated_cases:
            with self.subTest(string=test_case):
                log, tokens = self.capture_lexer_log(test_case)
                self.assertTrue(
                    any(t.type == LexerError.MALFORMED_STRING.value for t in tokens)
                )

    def test_unterminated_string(self):
        """Test unterminated string literals"""
        unterminated_cases = [
            '"hola',  # without closing quote
            '"hola \\',  # with backslash at end
            '"hola \\"',  # with escaped quote at end
            '"',  # empty string without closing quote
            '"\\',  # just backslash
            '"hola\n"',  # with new line
        ]

        for test_case in unterminated_cases:
            with self.subTest(string=test_case):
                log, tokens = self.capture_lexer_log(test_case)
                self.assertTrue(
                    any(t.type == LexerError.MALFORMED_STRING.value for t in tokens)
                )

    def test_unterminated_string_variants(self):
        """Test various unterminated string scenarios"""
        unterminated_variants = [
            r'"Unclosed string',
            r'"Bad escape \q"',
            r'"Broken hex \xZZ"',
        ]

        for test_case in unterminated_variants:
            with self.subTest(string=test_case):
                log, tokens = self.capture_lexer_log(test_case)
                self.assertTrue(
                    any(t.type == LexerError.MALFORMED_STRING.value for t in tokens)
                )

    def test_string_with_literal_newline_in_middle(self):
        """Test string with actual newline character"""
        # This creates a string that spans multiple lines
        test_multiline = """print "Line 1
Line 2";"""

        log, tokens = self.capture_lexer_log(test_multiline)
        self.assertTrue(
            any(t.type == LexerError.MALFORMED_STRING.value for t in tokens)
        )

    # === INVALID ESCAPE SEQUENCE TESTS ===

    def test_string_with_invalid_escapes(self):
        """Test strings with invalid escape sequences"""
        invalid_escapes = [
            '"Invalid \\z escape"',  # \z is not a valid escape
            '"Bad \\q sequence"',  # \q is not valid
            # \1 is not valid (unless octal supported)
            '"Wrong \\1 escape"',
            '"Invalid \\w escape"',  # \w is not valid
        ]

        for test_case in invalid_escapes:
            with self.subTest(escape=test_case):
                log, tokens = self.capture_lexer_log(test_case)
                self.assertTrue(
                    any(t.type == LexerError.MALFORMED_STRING.value for t in tokens)
                )

    def test_string_with_incomplete_hex_escape(self):
        """Test strings with incomplete hex escape sequences"""
        incomplete_hex = [
            '"Incomplete \\x"',  # Missing hex digits
            '"Bad \\x4"',  # Only one hex digit
            '"Invalid \\xGG"',  # Invalid hex characters
            '"Wrong \\x4G"',  # One valid, one invalid hex digit
        ]

        for test_case in incomplete_hex:
            with self.subTest(hex=test_case):
                log, tokens = self.capture_lexer_log(test_case)
                self.assertTrue(
                    any(t.type == LexerError.MALFORMED_STRING.value for t in tokens)
                )

    # === EDGE CASE TESTS ===

    def test_string_at_eof(self):
        """Test unterminated string at end of file"""
        log, tokens = self.capture_lexer_log('"unterminated')
        self.assertTrue(
            len(log) > 0
            and any(t.type == LexerError.MALFORMED_STRING.value for t in tokens)
        )

    def test_mixed_quotes(self):
        """Test mixing single and double quotes incorrectly"""
        mixed_cases = [
            "\"mixed quotes'",  # Start with " end with '
            "'mixed quotes\"",  # Start with ' end with "
        ]

        for test_case in mixed_cases:
            with self.subTest(mixed=test_case):
                log, tokens = self.capture_lexer_log(test_case)
                self.assertTrue(
                    any(t.type == LexerError.MALFORMED_STRING.value for t in tokens)
                )

    def test_string_exceeding_max_length(self):
        """Test string literals exceeding maximum length (255 chars)"""
        long_string = '"' + "a" * 300 + '"'
        log, tokens = self.capture_lexer_log(long_string)
        self.assertTrue(any(t.type == LexerError.TOO_LONG_STRING.value for t in tokens))
