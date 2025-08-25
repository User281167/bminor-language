
import unittest
from scanner import Lexer, TokenType


class TestCharLiterals(unittest.TestCase):
    def setUp(self):
        self.lexer = Lexer()

    def test_print_integer_and_char(self):
        tokens = list(self.lexer.tokenize("print 42 'a';"))
        expected_types = [TokenType.PRINT.value,
                          TokenType.INTEGER_LITERAL.value, TokenType.CHAR_LITERAL.value, ';']
        self.assertEqual([t.type for t in tokens], expected_types)
        self.assertEqual(tokens[1].value, 42)
        self.assertEqual(tokens[2].type, TokenType.CHAR_LITERAL.value)

    def test_ascii_printable_char(self):
        # Test specific printable characters (excluding ' and \ which need escaping)
        test_chars = ['a', 'Z', '0', '9', '!', '~',
                      ' ', '@', '#', '$', '%', '^', '&', '*']
        for c in test_chars:
            with self.subTest(char=c):
                tokens = list(self.lexer.tokenize(f"'{c}'"))
                self.assertEqual(len(tokens), 1)
                self.assertEqual(tokens[0].type, TokenType.CHAR_LITERAL.value)

    def test_escaped_newline(self):
        tokens = list(self.lexer.tokenize("'\\n'"))  # \n
        self.assertEqual(len(tokens), 1)
        self.assertEqual(tokens[0].type, TokenType.CHAR_LITERAL.value)

    def test_escaped_tab(self):
        tokens = list(self.lexer.tokenize("'\\t'"))  # \t
        self.assertEqual(len(tokens), 1)
        self.assertEqual(tokens[0].type, TokenType.CHAR_LITERAL.value)

    def test_escaped_backslash(self):
        # CORRECTED: Need four backslashes to represent \\
        tokens = list(self.lexer.tokenize("'\\\\'"))  # \\
        self.assertEqual(len(tokens), 1)
        self.assertEqual(tokens[0].type, TokenType.CHAR_LITERAL.value)

    def test_escaped_single_quote(self):
        # Using programmatic construction (your method works)
        # test_string = "'" + "\\" + "'" + "'"
        test_string = r"'\''"
        tokens = list(self.lexer.tokenize(test_string))  # \'
        print(f"\n>>>>>>>>>>Testing escaped single quote: {tokens}")
        self.assertEqual(len(tokens), 1)
        self.assertEqual(tokens[0].type, TokenType.CHAR_LITERAL.value)

    def test_escaped_double_quote(self):
        tokens = list(self.lexer.tokenize("'\\\"'"))  # \"
        self.assertEqual(len(tokens), 1)
        self.assertEqual(tokens[0].type, TokenType.CHAR_LITERAL.value)

    def test_escaped_hex(self):
        # Test hex escapes
        tokens = list(self.lexer.tokenize("'\\x41'"))  # \x41 = 'A'
        self.assertEqual(len(tokens), 1)
        self.assertEqual(tokens[0].type, TokenType.CHAR_LITERAL.value)

    def test_all_valid_escapes(self):
        # Test all standard C escape sequences
        escape_tests = [
            ('\\a', "'\\a'"),   # bell
            ('\\b', "'\\b'"),   # backspace
            ('\\e', "'\\e'"),   # escape (if supported)
            ('\\f', "'\\f'"),   # form feed
            ('\\n', "'\\n'"),   # newline
            ('\\r', "'\\r'"),   # carriage return
            ('\\t', "'\\t'"),   # tab
            ('\\v', "'\\v'"),   # vertical tab
            ("\\'", "'" + "\\" + "'" + "'"),  # escaped single quote
            ('\\"', "'\\\"'"),  # escaped double quote
            ('\\\\', "'\\\\'"),  # escaped backslash
        ]

        for desc, test_string in escape_tests:
            with self.subTest(escape=desc):
                tokens = list(self.lexer.tokenize(test_string))
                self.assertEqual(
                    len(tokens), 1, f"Failed for {desc}: {test_string}")
                self.assertEqual(tokens[0].type, TokenType.CHAR_LITERAL.value)

    def test_all_ascii_printable_chars(self):
        # ASCII 32 to 126 inclusive, excluding ' (39) and \ (92) which need escaping
        for code in range(32, 127):
            char = chr(code)
            if char not in ["'", "\\", '"']:  # Skip chars that need escaping
                with self.subTest(ascii_code=code, char=char):
                    tokens = list(self.lexer.tokenize(f"'{char}'"))
                    self.assertEqual(
                        len(tokens), 1, f"Failed for ASCII {code} ('{char}')")
                    self.assertEqual(
                        tokens[0].type, TokenType.CHAR_LITERAL.value)

    def test_hex_escape_samples(self):
        # Test various hex escapes
        hex_tests = [
            ("'\\x20'", 32),   # space
            ("'\\x41'", 65),   # 'A'
            ("'\\x61'", 97),   # 'a'
            ("'\\x30'", 48),   # '0'
            ("'\\x7E'", 126),  # '~'
            ("'\\x21'", 33),   # '!'
        ]

        for test_string, expected_ascii in hex_tests:
            with self.subTest(hex_test=test_string):
                tokens = list(self.lexer.tokenize(test_string))
                self.assertEqual(len(tokens), 1)
                self.assertEqual(tokens[0].type, TokenType.CHAR_LITERAL.value)

    def test_mixed_char_literals_in_expression(self):
        # Test multiple char literals in a single tokenization
        tokens = list(self.lexer.tokenize("'a' + '\\n' + '\\x41'"))
        print(f"\n>>>>>>>>>>Testing mixed char literals: {tokens}")
        char_tokens = [t for t in tokens if t.type ==
                       TokenType.CHAR_LITERAL.value]
        self.assertEqual(len(char_tokens), 3)

    def test_char_literal_boundaries(self):
        # Test edge cases for ASCII printable range
        boundary_tests = [
            ("'\\x20'", "space (ASCII 32)"),      # First printable
            ("'\\x7E'", "tilde (ASCII 126)"),     # Last printable
            ("' '", "literal space"),              # Space as literal char
        ]

        for test_string, desc in boundary_tests:
            with self.subTest(test=desc):
                tokens = list(self.lexer.tokenize(test_string))
                self.assertEqual(len(tokens), 1)
                self.assertEqual(tokens[0].type, TokenType.CHAR_LITERAL.value)

    def test_literal_control_chars(self):
        """Test literal control characters (should use escapes instead)"""
        control_chars = [
            ("'\\n'", "literal newline"),
            ("'\\t'", "literal tab"),
            ("'\\r'", "literal carriage return"),
            ("'\\0'", "literal null"),
        ]

        for char_test, desc in control_chars:
            with self.subTest(test=desc):
                tokens = list(self.lexer.tokenize(char_test))
                self.assertEqual(len(tokens), 1)
                self.assertEqual(tokens[0].type, TokenType.CHAR_LITERAL.value)

    def test_space_in_char_literal(self):
        tokens = list(self.lexer.tokenize("' '"))
        self.assertEqual(len(tokens), 1)
        self.assertEqual(tokens[0].type, TokenType.CHAR_LITERAL.value)

    def test_char_literals_basic(self):
        input_test = "[]{};:,.+-*/%&|^~!=<>?@#"

        for char_test in input_test:
            with self.subTest(char=char_test):
                tokens = list(self.lexer.tokenize(f"'{char_test}'"))
                self.assertEqual(len(tokens), 1)
                self.assertEqual(tokens[0].type, TokenType.CHAR_LITERAL.value)

    def test_char_literal_backslash(self):
        # Casos válidos
        valid = [r"'\\'", r"'\''", r"'\"'"]
        for lit in valid:
            with self.subTest(valid=lit):
                tokens = list(self.lexer.tokenize(lit))
                self.assertEqual(len(tokens), 1)
                self.assertEqual(tokens[0].type, TokenType.CHAR_LITERAL.value)
