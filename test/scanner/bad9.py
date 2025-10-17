import unittest
from scanner import Lexer, LexerError, TokenType


class TestInvalidFunctionTokens(unittest.TestCase):
    def setUp(self):
        self.lexer = Lexer()

    def test_function_name_with_utf8(self):
        # Using UTF-8 character π in function name
        tokens = list(
            self.lexer.tokenize(
                "π_func: function integer ( x: integer ) = { return x; }"
            )
        )
        # Should detect π as illegal character
        self.assertTrue(
            any(t.type == LexerError.ILLEGAL_CHARACTER.value for t in tokens)
        )

    def test_function_with_invalid_parameter_name(self):
        # Using @ in parameter name which is illegal
        tokens = list(
            self.lexer.tokenize("func: function integer ( @param: integer ) = { }")
        )
        # Should detect @ as illegal character
        self.assertTrue(
            any(t.type == LexerError.ILLEGAL_CHARACTER.value for t in tokens)
        )

    def test_function_with_emoji_in_body(self):
        # Using emoji in function body
        tokens = list(
            self.lexer.tokenize(
                """
            print_happy: function void () = {
                print "😊";
            }
        """
            )
        )
        # Should detect emoji as illegal character
        self.assertTrue(
            any(t.type == LexerError.ILLEGAL_CHARACTER.value for t in tokens)
        )

    def test_function_with_invalid_symbols(self):
        # Using invalid symbols ¥ and € in function
        tokens = list(
            self.lexer.tokenize("func¥: function integer ( x€: integer ) = { }")
        )
        # Should detect ¥ and € as illegal characters
        self.assertTrue(
            any(t.type == LexerError.ILLEGAL_CHARACTER.value for t in tokens)
        )

    def test_function_with_unexpected_tokens(self):
        # Using unexpected tokens like ..
        tokens = list(
            self.lexer.tokenize("func.. function integer ( x: integer ) = { }")
        )
        # Should detect .. as unexpected tokens
        self.assertTrue(
            any(t.type == LexerError.UNEXPECTED_TOKEN.value for t in tokens)
        )

    def test_function_with_unicode_punctuation(self):
        # Using Unicode quotation marks and brackets
        tokens = list(self.lexer.tokenize("func: function void 【x: integer】 = { }"))
        # Should detect 【】 as illegal characters
        self.assertTrue(
            any(t.type == LexerError.ILLEGAL_CHARACTER.value for t in tokens)
        )

    def test_function_with_invalid_type_chars(self):
        # Using invalid characters in type name
        tokens = list(
            self.lexer.tokenize("func: function intéger ( x: integer ) = { }")
        )
        # Should detect é as illegal character
        self.assertTrue(
            any(t.type == LexerError.ILLEGAL_CHARACTER.value for t in tokens)
        )

    def test_function_with_control_chars(self):
        # Using control characters in function
        tokens = list(self.lexer.tokenize("func: function void () = {\x01 return; }"))
        # Should detect control character as illegal
        self.assertTrue(
            any(t.type == LexerError.ILLEGAL_CHARACTER.value for t in tokens)
        )

    def test_function_with_invalid_operators(self):
        # Using invalid operator combinations
        tokens = list(
            self.lexer.tokenize(
                """
            func: function integer ( x: integer ) = {
                return x ±± 2;
            }
        """
            )
        )
        # Should detect ± as illegal characters
        self.assertTrue(
            any(t.type == LexerError.ILLEGAL_CHARACTER.value for t in tokens)
        )

    def test_function_with_invalid_delimiters(self):
        # Using invalid delimiters
        tokens = list(self.lexer.tokenize("func⟦ function void ⟧ = { }"))
        # Should detect ⟦⟧ as illegal characters
        self.assertTrue(
            any(t.type == LexerError.ILLEGAL_CHARACTER.value for t in tokens)
        )
