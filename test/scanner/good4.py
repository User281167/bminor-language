import unittest
from scanner import Lexer, TokenType


class TestValidIDs(unittest.TestCase):
    def setUp(self):
        self.lexer = Lexer()

    def test_simple_id(self):
        tokens = list(self.lexer.tokenize("x"))
        self.assertEqual(len(tokens), 1)
        self.assertEqual(tokens[0].type, TokenType.ID.value)
        self.assertEqual(tokens[0].value, "x")

    def test_id_with_underscore(self):
        tokens = list(self.lexer.tokenize("_foo"))
        self.assertEqual(len(tokens), 1)
        self.assertEqual(tokens[0].type, TokenType.ID.value)
        self.assertEqual(tokens[0].value, "_foo")

    def test_id_with_digits(self):
        tokens = list(self.lexer.tokenize("bar123"))
        self.assertEqual(len(tokens), 1)
        self.assertEqual(tokens[0].type, TokenType.ID.value)
        self.assertEqual(tokens[0].value, "bar123")

    def test_id_with_multiple_underscores(self):
        tokens = list(self.lexer.tokenize("a_b_c"))
        self.assertEqual(len(tokens), 1)
        self.assertEqual(tokens[0].type, TokenType.ID.value)
        self.assertEqual(tokens[0].value, "a_b_c")

    def test_id_with_leading_underscore_and_digits(self):
        tokens = list(self.lexer.tokenize("_x99"))
        self.assertEqual(len(tokens), 1)
        self.assertEqual(tokens[0].type, TokenType.ID.value)
        self.assertEqual(tokens[0].value, "_x99")

    def test_long_id(self):
        tokens = list(self.lexer.tokenize("BigLongName55"))
        self.assertEqual(len(tokens), 1)
        self.assertEqual(tokens[0].type, TokenType.ID.value)
        self.assertEqual(tokens[0].value, "BigLongName55")

    def test_id_with_only_letters(self):
        tokens = list(self.lexer.tokenize("fog"))
        self.assertEqual(len(tokens), 1)
        self.assertEqual(tokens[0].type, TokenType.ID.value)
        self.assertEqual(tokens[0].value, "fog")

    def test_id_with_mixed_case(self):
        tokens = list(self.lexer.tokenize("myStr"))
        self.assertEqual(len(tokens), 1)
        self.assertEqual(tokens[0].type, TokenType.ID.value)
        self.assertEqual(tokens[0].value, "myStr")

    def test_id_with_trailing_underscore(self):
        tokens = list(self.lexer.tokenize("foo_"))
        self.assertEqual(len(tokens), 1)
        self.assertEqual(tokens[0].type, TokenType.ID.value)
        self.assertEqual(tokens[0].value, "foo_")

    def test_multiple_ids(self):
        tokens = list(self.lexer.tokenize("i x mystr fog123 BigLongName55"))
        expected = ["i", "x", "mystr", "fog123", "BigLongName55"]
        self.assertEqual(len(tokens), 5)
        for i, token in enumerate(tokens):
            self.assertEqual(token.type, TokenType.ID.value)
            self.assertEqual(token.value, expected[i])

    def test_valid_ids(self):
        # Valid IDs with numbers, should be tokenized as ID
        for ident in ["au343", "_foo42", "bar_123", "x9", "foo1bar2"]:
            tokens = list(self.lexer.tokenize(ident))
            self.assertEqual(len(tokens), 1)
            self.assertEqual(tokens[0].type, TokenType.ID.value)
            self.assertEqual(tokens[0].value, ident)

    def test_invalid_keyword_case(self):
        # Keywords in uppercase/camelcase should be IDs
        for kw in ["IF", "While", "TRUE", "False"]:
            tokens = list(self.lexer.tokenize(kw))
            self.assertEqual(len(tokens), 1)
            self.assertEqual(tokens[0].type, TokenType.ID.value)
