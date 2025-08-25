import unittest
from scanner import Lexer, TokenType, LiteralType


class TestVariableDeclarations(unittest.TestCase):
    def setUp(self):
        self.lexer = Lexer()

    def test_simple_declaration(self):
        """Test simple variable declaration without initialization"""
        input_test = "x: integer;"
        tokens = list(self.lexer.tokenize(input_test))
        expected_types = [TokenType.ID.value,
                          ':', TokenType.INTEGER.value, ';']
        self.assertEqual([t.type for t in tokens], expected_types)

    def test_integer_initialization(self):
        """Test integer variable initialization"""
        input_test = "y: integer = 123;"
        tokens = list(self.lexer.tokenize(input_test))
        expected_types = [TokenType.ID.value, LiteralType.COLON.value,
                          TokenType.INTEGER.value, LiteralType.EQUAL.value,
                          TokenType.INTEGER_LITERAL.value, LiteralType.SEMICOLON.value]
        self.assertEqual([t.type for t in tokens], expected_types)

    def test_float_initialization(self):
        """Test float variable initialization"""
        input_test = "f: float = 45.67;"
        tokens = list(self.lexer.tokenize(input_test))
        expected_types = [TokenType.ID.value, LiteralType.COLON.value,
                          TokenType.FLOAT.value, LiteralType.EQUAL.value,
                          TokenType.FLOAT_LITERAL.value, LiteralType.SEMICOLON.value]
        self.assertEqual([t.type for t in tokens], expected_types)

    def test_boolean_initialization(self):
        """Test boolean variable initialization"""
        input_test = "b: boolean = false;"
        tokens = list(self.lexer.tokenize(input_test))
        expected_types = [TokenType.ID.value, LiteralType.COLON.value,
                          TokenType.BOOLEAN.value, LiteralType.EQUAL.value,
                          TokenType.FALSE.value, LiteralType.SEMICOLON.value]
        self.assertEqual([t.type for t in tokens], expected_types)

    def test_char_initialization(self):
        """Test char variable initialization"""
        input_test = "c: char = 'q';"
        tokens = list(self.lexer.tokenize(input_test))
        expected_types = [TokenType.ID.value, LiteralType.COLON.value,
                          TokenType.CHAR.value, LiteralType.EQUAL.value,
                          TokenType.CHAR_LITERAL.value, LiteralType.SEMICOLON.value]
        self.assertEqual([t.type for t in tokens], expected_types)

    def test_string_initialization(self):
        """Test string variable initialization"""
        input_test = 's: string = "hello bminor\\n";'
        tokens = list(self.lexer.tokenize(input_test))
        expected_types = [TokenType.ID.value, LiteralType.COLON.value,
                          TokenType.STRING.value, LiteralType.EQUAL.value,
                          TokenType.STRING_LITERAL.value, LiteralType.SEMICOLON.value]
        self.assertEqual([t.type for t in tokens], expected_types)

    def test_multiple_declarations(self):
        """Test multiple declarations with mixed comments"""
        # this
        input_test = """
        // First declaration
        x: integer;
        /* Second declaration */
        y: integer = 123;
        // Float declaration
        f: float = 45.67;
        """
        tokens = list(self.lexer.tokenize(input_test))

        expected_types = [
            TokenType.ID.value, LiteralType.COLON.value, TokenType.INTEGER.value,
            LiteralType.SEMICOLON.value,
            TokenType.ID.value, LiteralType.COLON.value, TokenType.INTEGER.value,
            LiteralType.EQUAL.value, TokenType.INTEGER_LITERAL.value, LiteralType.SEMICOLON.value,
            TokenType.ID.value, LiteralType.COLON.value, TokenType.FLOAT.value,
            LiteralType.EQUAL.value, TokenType.FLOAT_LITERAL.value, LiteralType.SEMICOLON.value
        ]
        self.assertEqual([t.type for t in tokens], expected_types)

        def test_invalid_initializations(self):
            """Test invalid variable initializations"""
            # valid token but invalid initialization combinations parser should catch
            invalid_inits = [
                'x: integer = false;',  # Missing value after =
                'x: integer = "5";',    # Type mismatch (string for integer)
                'x: string = 12.3;',      # Type mismatch (integer for string)
                'x: char = "c";',       # Wrong quote type for char
                'x: boolean = 1;',      # Invalid boolean value
                'x: float = true;',     # Invalid float value
            ]

            expected = [
                TokenType.FALSE.value,
                TokenType.STRING_LITERAL.value,
                TokenType.FLOAT_LITERAL.value,
                TokenType.STRING_LITERAL.value,
                TokenType.INTEGER_LITERAL.value,
                TokenType.TRUE.value
            ]

            for test_case, expected_type in zip(invalid_inits, expected):
                with self.subTest(initialization=test_case):
                    log, tokens = self.capture_lexer_log(test_case)
                    # Check that the expected invalid token type is present
                    self.assertTrue(
                        any(t.type == expected_type for t in tokens)
                    )
