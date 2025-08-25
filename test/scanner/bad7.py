import unittest
from scanner import Lexer, LexerError, TokenType, LiteralType
import logging
from io import StringIO


class TestBadVariableDeclarations(unittest.TestCase):
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

    def test_invalid_identifier_length(self):
        """Test identifier exceeding maximum length (255 characters)"""
        long_id = 'x' * 256 + ': integer;'
        log, tokens = self.capture_lexer_log(long_id)
        self.assertTrue(
            any(t.type == LexerError.INVALID_ID.value for t in tokens)
        )

    def test_invalid_identifier_characters(self):
        """Test identifiers with invalid characters"""
        invalid_ids = [
            '123var: integer;',      # Starting with number
            '$var: integer;',        # Invalid special character
            '@test: integer;',       # Invalid special character
            'var#1: integer;',       # Invalid character in middle
            'var-name: integer;',    # Hyphen not allowed
            'var.name: integer;',    # Dot not allowed
        ]

        expected = [
            TokenType.INTEGER_LITERAL.value,        # 123VAR
            LexerError.ILLEGAL_CHARACTER.value,     # $
            LexerError.ILLEGAL_CHARACTER.value,     # @
            LexerError.ILLEGAL_CHARACTER.value,     # #
            LiteralType.MINUS.value,                # -
            LexerError.UNEXPECTED_TOKEN.value,      # .
        ]

        for i in range(len(invalid_ids)):
            test_case = invalid_ids[i]
            expected_type = expected[i]

            with self.subTest(identifier=test_case):
                log, tokens = self.capture_lexer_log(test_case)
                self.assertTrue(
                    any(t.type == expected_type for t in tokens)
                )

    def test_invalid_type_declarations(self):
        """Test invalid type declarations"""
        invalid_types = [
            'x: Int;',              # Wrong case for integer
            'y: STRING;',           # Wrong case for string
            'z: Boolean;',          # Wrong case for boolean
            'w: number;',           # Non-existent type
            'v: str;',              # Invalid type abbreviation
            'u: int;',              # Invalid type abbreviation
        ]

        for test_case in invalid_types:
            with self.subTest(type_decl=test_case):
                log, tokens = self.capture_lexer_log(test_case)

                self.assertTrue(all(t.type != TokenType.INTEGER.value and
                                    t.type != TokenType.STRING.value and
                                    t.type != TokenType.BOOLEAN.value
                                    for t in tokens)
                                )

        def test_invalid_utf8_characters_in_identifier(self):
            """Test variable declarations with UTF-8/emoji/non-ASCII in identifier"""
            invalid_ids = [
                '🚀x: integer;',
                '变量: integer;',
                'αβγ: integer;',
                'ñandú: integer;',
                'x😊: integer;',
            ]
            for test_case in invalid_ids:
                with self.subTest(identifier=test_case):
                    log, tokens = self.capture_lexer_log(test_case)
                    self.assertTrue(
                        any(t.type == LexerError.ILLEGAL_CHARACTER.value for t in tokens)
                    )

        def test_invalid_utf8_characters_in_type(self):
            """Test variable declarations with UTF-8/emoji/non-ASCII in type name"""
            invalid_types = [
                'x: 🚀;',
                'x: 变量;',
                'x: αβγ;',
                'x: ñandú;',
                'x: 😊;',
            ]
            for test_case in invalid_types:
                with self.subTest(type_decl=test_case):
                    log, tokens = self.capture_lexer_log(test_case)
                    self.assertTrue(
                        any(t.type == LexerError.ILLEGAL_CHARACTER.value for t in tokens)
                    )

        def test_invalid_utf8_characters_in_value(self):
            """Test variable initializations with UTF-8/emoji/non-ASCII in value"""
            invalid_values = [
                'x: string = "hello 🚀";',
                'x: string = "你好";',
                'x: string = "αβγ";',
                'x: string = "ñandú";',
                'x: string = "😊";',
            ]
            for test_case in invalid_values:
                with self.subTest(value=test_case):
                    log, tokens = self.capture_lexer_log(test_case)
                    self.assertTrue(
                        any(t.type == LexerError.ILLEGAL_CHARACTER.value for t in tokens)
                    )

    def test_malformed_declarations(self):
        """Test malformed variable declarations"""
        malformed_cases = [
            ': integer x;',         # Colon before identifier
            'integer: x;',          # Type before colon
            'x integer: ;',         # Wrong order
            'x integer;',           # Missing colon
            'x :: integer;',        # Double colon
            'x :integer;',          # Missing space after colon
            'x: integer;;',         # Double semicolon
        ]

        for test_case in malformed_cases:
            with self.subTest(malformed=test_case):
                log, tokens = self.capture_lexer_log(test_case)
                # These should produce tokens but in invalid sequences
                self.assertTrue(len(tokens) > 0)
