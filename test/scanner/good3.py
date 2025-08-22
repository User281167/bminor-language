import unittest
from scanner import Lexer, TokenType, OperatorType, LiteralType


class TestOperators(unittest.TestCase):
    def setUp(self):
        self.lexer = Lexer()

    def test_comparison_operators(self):
        test_input = "< <= > >= == !="
        tokens = list(self.lexer.tokenize(test_input))
        expected_types = [
            OperatorType.LT.value,
            OperatorType.LE.value,
            OperatorType.GT.value,
            OperatorType.GE.value,
            OperatorType.EQ.value,
            OperatorType.NE.value
        ]
        self.assertEqual([t.type for t in tokens], expected_types)

    def test_logical_operators(self):
        test_input = "&& `"
        tokens = list(self.lexer.tokenize(test_input))
        expected_types = [
            OperatorType.LAND.value,
            OperatorType.LOR.value
        ]
        self.assertEqual([t.type for t in tokens], expected_types)

    def test_unary_operator(self):
        test_input = "!"
        tokens = list(self.lexer.tokenize(test_input))
        # '!' is not defined as a token, should be a literal
        self.assertEqual(len(tokens), 1)
        self.assertEqual(tokens[0].type, LiteralType.BANG.value)

    def test_operator_hierarchy(self):
        test_input = "<="
        tokens = list(self.lexer.tokenize(test_input))
        self.assertEqual(len(tokens), 1)
        self.assertEqual(tokens[0].type, OperatorType.LE.value)

        test_input = "< ="
        tokens = list(self.lexer.tokenize(test_input))
        self.assertEqual(len(tokens), 2)
        self.assertEqual(tokens[0].type, OperatorType.LT.value)
        self.assertEqual(tokens[1].type, '=')
