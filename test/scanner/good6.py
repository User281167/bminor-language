import unittest

from scanner import Lexer, TokenType


class TestStringLiterals(unittest.TestCase):
    def setUp(self):
        self.lexer = Lexer()

    def test_empty_string(self):
        """Test empty string literal"""
        tokens = list(self.lexer.tokenize('""'))
        self.assertEqual(len(tokens), 1)
        self.assertEqual(tokens[0].type, TokenType.STRING_LITERAL.value)
        self.assertEqual(tokens[0].value, '""')

    def test_simple_string(self):
        """Test simple string with regular characters"""
        tokens = list(self.lexer.tokenize('"Hello World"'))
        self.assertEqual(len(tokens), 1)
        self.assertEqual(tokens[0].type, TokenType.STRING_LITERAL.value)
        self.assertEqual(tokens[0].value, '"Hello World"')

    def test_string_with_numbers_and_symbols(self):
        """Test string containing numbers, spaces, and symbols"""
        tokens = list(self.lexer.tokenize('"The answer is 42! @#$%^&*()"'))
        self.assertEqual(len(tokens), 1)
        self.assertEqual(tokens[0].type, TokenType.STRING_LITERAL.value)

    def test_string_with_single_quotes(self):
        """Test string containing single quotes (no escaping needed)"""
        input = """"It's a beautiful day" """
        tokens = list(self.lexer.tokenize(input))
        self.assertEqual(len(tokens), 1)
        self.assertEqual(tokens[0].type, TokenType.STRING_LITERAL.value)

    def test_string_with_escaped_double_quote(self):
        """Test string with escaped double quote"""
        tokens = list(self.lexer.tokenize('"\\"Hello\\" she said"'))
        self.assertEqual(len(tokens), 1)
        self.assertEqual(tokens[0].type, TokenType.STRING_LITERAL.value)

    def test_string_with_escaped_backslash(self):
        """Test string with escaped backslash"""
        tokens = list(self.lexer.tokenize('"Path: C:\\\\Users\\\\Name"'))
        self.assertEqual(len(tokens), 1)
        self.assertEqual(tokens[0].type, TokenType.STRING_LITERAL.value)

    def test_string_with_escape_sequences(self):
        """Test string with various escape sequences"""
        tokens = list(
            self.lexer.tokenize('"Line 1\\nLine 2\\tTabbed\\rCarriage Return"')
        )
        self.assertEqual(len(tokens), 1)
        self.assertEqual(tokens[0].type, TokenType.STRING_LITERAL.value)

    def test_string_with_all_standard_escapes(self):
        """Test string containing all standard escape sequences"""
        # Test string with: \a \b \e \f \n \r \t \v \' \" \\
        test_string = '"Bell:\\a Back:\\b Esc:\\e Form:\\f New:\\n Ret:\\r Tab:\\t Vert:\\v Quote:\\\\\\""'
        tokens = list(self.lexer.tokenize(test_string))
        self.assertEqual(len(tokens), 1)
        self.assertEqual(tokens[0].type, TokenType.STRING_LITERAL.value)

    def test_string_with_hex_escapes(self):
        """Test string with hexadecimal escape sequences"""
        tokens = list(self.lexer.tokenize('"ASCII A=\\x41, Space=\\x20, Tilde=\\x7E"'))
        self.assertEqual(len(tokens), 1)
        self.assertEqual(tokens[0].type, TokenType.STRING_LITERAL.value)

    def test_string_with_mixed_content(self):
        """Test string with mix of regular chars, escapes, and hex codes"""
        test_string = (
            '"Name: John\\tAge: 25\\nStatus: \\x41ctive\\nPath: C:\\\\temp\\\\file.txt"'
        )
        tokens = list(self.lexer.tokenize(test_string))
        self.assertEqual(len(tokens), 1)
        self.assertEqual(tokens[0].type, TokenType.STRING_LITERAL.value)

    # Bonus tests for context

    def test_multiple_strings_in_sequence(self):
        """Test multiple string literals in one input"""
        tokens = list(self.lexer.tokenize('"First" "Second" "Third"'))
        string_tokens = [t for t in tokens if t.type == TokenType.STRING_LITERAL.value]
        self.assertEqual(len(string_tokens), 3)

    def test_string_in_print_statement(self):
        """Test string literal within a print statement"""
        tokens = list(self.lexer.tokenize('print "Hello, World!";'))
        expected_types = [TokenType.PRINT.value, TokenType.STRING_LITERAL.value, ";"]
        self.assertEqual([t.type for t in tokens], expected_types)

    def test_string_with_literal_control_chars(self):
        """Test that literal control characters work in strings (unlike char literals)"""
        # This creates a string with actual newline and tab characters
        test_input = '"Line 1\\nLine 2\\tTabbed"'  # \n, \t are valid escapes in strings
        tokens = list(self.lexer.tokenize(test_input))
        self.assertEqual(len(tokens), 1)
        self.assertEqual(tokens[0].type, TokenType.STRING_LITERAL.value)

    def test_very_long_string(self):
        """Test a long string to ensure no length limitations"""
        long_content = "A" * 100  # 100 A's
        test_string = f'"{long_content}"'
        tokens = list(self.lexer.tokenize(test_string))
        self.assertEqual(len(tokens), 1)
        self.assertEqual(tokens[0].type, TokenType.STRING_LITERAL.value)

    def test_string_edge_cases(self):
        """Test strings with edge case characters"""
        edge_cases = [
            '""',  # Empty
            '" "',  # Just space
            # Exclamation (ASCII 33, first printable after space)
            '"!"',
            '"~"',  # Tilde (ASCII 126, last printable)
            '"\\x20\\x21\\x7E"',  # Space, !, ~ as hex escapes
        ]

        for test_case in edge_cases:
            with self.subTest(string=test_case):
                tokens = list(self.lexer.tokenize(test_case))
                self.assertEqual(len(tokens), 1)
                self.assertEqual(tokens[0].type, TokenType.STRING_LITERAL.value)

    def test_string_with_simple_comments(self):
        """Test string literals that include comment-like sequences"""
        comment_tests = [
            '"This is not a // comment"',
            '"Neither is this a /* comment */"',
            '"Mixing // and /* comments */ in one line"',
        ]

        for test_string in comment_tests:
            with self.subTest(string=test_string):
                tokens = list(self.lexer.tokenize(test_string))
                self.assertEqual(len(tokens), 1)
                self.assertEqual(tokens[0].type, TokenType.STRING_LITERAL.value)

    def test_string_with_multiline_content(self):
        """Test string literals that span multiple lines using escape sequences"""
        multiline_string = '"Line 1\\nLine 2\\nLine 3"'
        tokens = list(self.lexer.tokenize(multiline_string))
        self.assertEqual(len(tokens), 1)
        self.assertEqual(tokens[0].type, TokenType.STRING_LITERAL.value)

    def test_string_with_multiline_comments(self):
        """Test string literals that include multiline comment-like sequences"""
        test_string = '"This is not a /* multiline comment */"'
        tokens = list(self.lexer.tokenize(test_string))
        self.assertEqual(len(tokens), 1)
        self.assertEqual(tokens[0].type, TokenType.STRING_LITERAL.value)
        self.assertEqual(tokens[0].value, '"This is not a /* multiline comment */"')

    def test_string_with_string_content(self):
        input_string = '"string"'  # valid string literal no keyword
        tokens = list(self.lexer.tokenize(input_string))
        self.assertEqual(len(tokens), 1)
        self.assertEqual(tokens[0].type, TokenType.STRING_LITERAL.value)

    def test_spaces_in_string(self):
        input_string = '"   "'
        tokens = list(self.lexer.tokenize(input_string))
        self.assertEqual(len(tokens), 1)
        self.assertEqual(tokens[0].type, TokenType.STRING_LITERAL.value)
        self.assertEqual(tokens[0].value, input_string)

    def test_question_mark_in_string(self):
        input_string = '"What?"'
        tokens = list(self.lexer.tokenize(input_string))
        self.assertEqual(len(tokens), 1)
        self.assertEqual(tokens[0].type, TokenType.STRING_LITERAL.value)
        self.assertEqual(tokens[0].value, input_string)

    def test_double_quotes_in_string(self):
        input_string = '"She said, \\"Hello!\\""'
        tokens = list(self.lexer.tokenize(input_string))
        self.assertEqual(len(tokens), 1)
        self.assertEqual(tokens[0].type, TokenType.STRING_LITERAL.value)
        self.assertEqual(tokens[0].value, input_string)

    def test_literals(self):
        input_test = "()[]{};:,.+-*/%&|^~!=<>?@#'"

        for char_test in input_test:
            with self.subTest(char=char_test):
                tokens = list(self.lexer.tokenize(f'"{char_test}"'))
                self.assertEqual(len(tokens), 1)
                self.assertEqual(tokens[0].type, TokenType.STRING_LITERAL.value)

    def test_literals_quotes(self):
        input_test = ['"', "\\"]

        for char_test in input_test:
            # Escapar el carácter para que se represente correctamente dentro del string
            if char_test == '"':
                escaped = r"\""
            elif char_test == "\\":
                escaped = r"\\"
            else:
                escaped = char_test

            with self.subTest(char=char_test):
                # Construir el string con comillas dobles alrededor
                source = f'"{escaped}"'
                tokens = list(self.lexer.tokenize(source))
                self.assertEqual(len(tokens), 1)
                self.assertEqual(tokens[0].type, TokenType.STRING_LITERAL.value)
