import unittest
from scanner import Lexer, TokenType, LiteralType, OperatorType


class TestArrayAndLoopTokens(unittest.TestCase):
    def setUp(self):
        self.lexer = Lexer()

    def test_array_declaration(self):
        input_test = "a: array [5] integer;"
        tokens = list(self.lexer.tokenize(input_test))
        expected_types = [
            TokenType.ID.value,
            LiteralType.COLON.value,
            TokenType.ARRAY.value,
            "[",
            TokenType.INTEGER_LITERAL.value,
            "]",
            TokenType.INTEGER.value,
            ";",
        ]
        self.assertEqual([t.type for t in tokens], expected_types)

    def test_array_initialization(self):
        input_test = "a: array [5] integer = {1,2,3,4,5};"
        tokens = list(self.lexer.tokenize(input_test))
        expected_types = [
            TokenType.ID.value,
            LiteralType.COLON.value,
            TokenType.ARRAY.value,
            "[",
            TokenType.INTEGER_LITERAL.value,
            "]",
            TokenType.INTEGER.value,
            "=",
            "{",
            TokenType.INTEGER_LITERAL.value,
            ",",
            TokenType.INTEGER_LITERAL.value,
            ",",
            TokenType.INTEGER_LITERAL.value,
            ",",
            TokenType.INTEGER_LITERAL.value,
            ",",
            TokenType.INTEGER_LITERAL.value,
            "}",
            ";",
        ]
        self.assertEqual([t.type for t in tokens], expected_types)

    def test_for_loop_tokens(self):
        input_test = "for(i=0; i<10; i++) { print i; }"
        tokens = list(self.lexer.tokenize(input_test))
        expected_types = [
            TokenType.FOR.value,
            "(",
            TokenType.ID.value,
            "=",
            TokenType.INTEGER_LITERAL.value,
            ";",
            TokenType.ID.value,
            OperatorType.LT.value,
            TokenType.INTEGER_LITERAL.value,
            ";",
            TokenType.ID.value,
            OperatorType.INC.value,
            ")",
            "{",
            TokenType.PRINT.value,
            TokenType.ID.value,
            ";",
            "}",
        ]
        self.assertEqual([t.type for t in tokens], expected_types)

    def test_unclosed_bracket(self):
        input_test = "array [5"
        tokens = list(self.lexer.tokenize(input_test))
        expected_types = [TokenType.ARRAY.value, "[", TokenType.INTEGER_LITERAL.value]
        self.assertEqual([t.type for t in tokens], expected_types)
