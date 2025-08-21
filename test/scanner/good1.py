import unittest
from scanner import Lexer, TokenType


class TestNumbers(unittest.TestCase):
    def setUp(self):
        self.lexer = Lexer()

    def test_valid_integer(self):
        test_input = "42\n"
        tokens = list(self.lexer.tokenize(test_input))
        self.assertEqual(len(tokens), 1)
        self.assertEqual(tokens[0].type, TokenType.INTEGER.value)
        self.assertEqual(tokens[0].value, 42)

    def test_valid_integer_with_leading_zeros(self):
        test_input = "0042\n"
        tokens = list(self.lexer.tokenize(test_input))
        self.assertEqual(len(tokens), 1)
        self.assertEqual(tokens[0].type, TokenType.INTEGER.value)
        self.assertEqual(tokens[0].value, 42)

    def test_valid_big_integer(self):
        test_input = '231432443'
        tokens = list(self.lexer.tokenize(test_input))
        self.assertEqual(len(tokens), 1)
        self.assertEqual(tokens[0].type, TokenType.INTEGER.value)
        self.assertEqual(tokens[0].value, 231432443)

    def test_valid_plus_integer(self):
        test_input = "+42\n"
        tokens = list(self.lexer.tokenize(test_input))
        self.assertEqual(len(tokens), 2)
        self.assertEqual(tokens[1].type, TokenType.INTEGER.value)
        self.assertEqual(tokens[1].value, 42)

    def test_valid_minus_integer(self):
        test_input = "-42+\n"
        tokens = list(self.lexer.tokenize(test_input))
        self.assertEqual(len(tokens), 3)
        self.assertEqual(tokens[1].type, TokenType.INTEGER.value)
        self.assertEqual(tokens[1].value, 42)

    def test_valid_float(self):
        test_input = "3.14\n"
        tokens = list(self.lexer.tokenize(test_input))
        print(tokens)
        self.assertEqual(len(tokens), 1)
        self.assertEqual(tokens[0].type, TokenType.FLOAT.value)
        # is instantiated as float and not int
        self.assertTrue(isinstance(tokens[0].value, float))

    def test_valid_float_with_leading_zeros(self):
        test_input = "0003.14\n"
        tokens = list(self.lexer.tokenize(test_input))
        self.assertEqual(len(tokens), 1)
        self.assertEqual(tokens[0].type, TokenType.FLOAT.value)
        self.assertTrue(isinstance(tokens[0].value, float))

    def test_valid_float_with_trailing_zeros(self):
        test_input = "3.140000\n"
        tokens = list(self.lexer.tokenize(test_input))
        self.assertEqual(len(tokens), 1)
        self.assertEqual(tokens[0].type, TokenType.FLOAT.value)
        self.assertTrue(isinstance(tokens[0].value, float))

    def test_valid_float_with_leading_and_trailing_zeros(self):
        test_input = "0003.140000\n"
        tokens = list(self.lexer.tokenize(test_input))
        self.assertEqual(len(tokens), 1)
        self.assertEqual(tokens[0].type, TokenType.FLOAT.value)
        self.assertTrue(isinstance(tokens[0].value, float))

    def test_valid_starts_with_float(self):
        test_input = ".42\n"
        tokens = list(self.lexer.tokenize(test_input))
        self.assertEqual(len(tokens), 1)
        self.assertEqual(tokens[0].type, TokenType.FLOAT.value)
        self.assertTrue(isinstance(tokens[0].value, float))

    def test_valid_notation(self):
        test_input = "3.14e10\n"
        tokens = list(self.lexer.tokenize(test_input))
        self.assertEqual(len(tokens), 1)
        self.assertEqual(tokens[0].type, TokenType.FLOAT.value)
        self.assertTrue(isinstance(tokens[0].value, float))

    def test_valid_notation_with_leading_zeros(self):
        test_input = "0003.14e10\n"
        tokens = list(self.lexer.tokenize(test_input))
        self.assertEqual(len(tokens), 1)
        self.assertEqual(tokens[0].type, TokenType.FLOAT.value)
        self.assertTrue(isinstance(tokens[0].value, float))

    def test_valid_notation_with_plus(self):
        test_input = "3.14e+10\n"
        tokens = list(self.lexer.tokenize(test_input))
        self.assertEqual(len(tokens), 1)
        self.assertEqual(tokens[0].type, TokenType.FLOAT.value)
        self.assertTrue(isinstance(tokens[0].value, float))

    def test_valid_notation_with_minus(self):
        test_input = "3.14e-10\n"
        tokens = list(self.lexer.tokenize(test_input))
        self.assertEqual(len(tokens), 1)
        self.assertEqual(tokens[0].type, TokenType.FLOAT.value)
        self.assertTrue(isinstance(tokens[0].value, float))

    def test_valid_integer_and_float(self):
        test_input = '42.42 5 3.14 .42\n 0093 .54 2e10 2e-1'
        tokens = list(self.lexer.tokenize(test_input))
        self.assertEqual(len(tokens), 8)

        expected = [
            (TokenType.FLOAT.value, 42.42),
            (TokenType.INTEGER.value, 5),
            (TokenType.FLOAT.value, 3.14),
            (TokenType.FLOAT.value, 0.42),
            (TokenType.INTEGER.value, 93),
            (TokenType.FLOAT.value, 0.54),
            (TokenType.FLOAT.value, 2e10),
            (TokenType.FLOAT.value, 2e-1)
        ]

        for i in range(len(tokens)):
            self.assertEqual(
                tokens[i].value, expected[i][1],
                f'Expected {expected[i][1]} but got {tokens[i].value} at index {i}'
            )

            self.assertEqual(
                tokens[i].type, expected[i][0],
                f'Expected {expected[i][0]} but got {tokens[i].type} at index {i}'
            )
