import unittest
from scanner import Lexer, TokenType


class TestOperators(unittest.TestCase):
    def setUp(self):
        self.lexer = Lexer()

    def test_comparison_operators(self):
        test_input = "< <= > >= == !="
        tokens = list(self.lexer.tokenize(test_input))
        expected_types = [
            TokenType.LT.value,
            TokenType.LE.value,
            TokenType.GT.value,
            TokenType.GE.value,
            TokenType.EQ.value,
            TokenType.NE.value
        ]
        self.assertEqual([t.type for t in tokens], expected_types)

    def test_logical_operators(self):
        test_input = "&& `"
        tokens = list(self.lexer.tokenize(test_input))
        expected_types = [
            TokenType.LAND.value,
            TokenType.LOR.value
        ]
        self.assertEqual([t.type for t in tokens], expected_types)

    def test_unary_operator(self):
        test_input = "!"
        tokens = list(self.lexer.tokenize(test_input))
        # '!' is not defined as a token, should be a literal
        self.assertEqual(len(tokens), 1)
        self.assertEqual(tokens[0].type, '!')

    def test_operator_hierarchy(self):
        test_input = "<="
        tokens = list(self.lexer.tokenize(test_input))
        self.assertEqual(len(tokens), 1)
        self.assertEqual(tokens[0].type, TokenType.LE.value)

        test_input = "< ="
        tokens = list(self.lexer.tokenize(test_input))
        self.assertEqual(len(tokens), 2)
        self.assertEqual(tokens[0].type, TokenType.LT.value)
        self.assertEqual(tokens[1].type, '=')
