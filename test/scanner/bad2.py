import unittest
from scanner import Lexer, TokenType, LexerError


class TestBadKeywords(unittest.TestCase):
    def setUp(self):
        self.lexer = Lexer()

    def test_uppercase_keywords(self):
        for kw in [
            "ARRAY",
            "AUTO",
            "BOOLEAN",
            "CHAR",
            "ELSE",
            "FALSE",
            "FLOAT",
            "FOR",
            "FUNCTION",
            "IF",
            "INTEGER",
            "PRINT",
            "RETURN",
            "STRING",
            "TRUE",
            "VOID",
            "WHILE",
        ]:
            tokens = list(self.lexer.tokenize(kw))
            self.assertEqual(len(tokens), 1)
            self.assertEqual(tokens[0].type, TokenType.ID.value)

    def test_camelcase_keywords(self):
        for kw in [
            "Array",
            "Auto",
            "Boolean",
            "Char",
            "Else",
            "False",
            "Float",
            "For",
            "Function",
            "If",
            "Integer",
            "Print",
            "Return",
            "String",
            "True",
            "Void",
            "While",
        ]:
            tokens = list(self.lexer.tokenize(kw))
            self.assertEqual(len(tokens), 1)
            self.assertEqual(tokens[0].type, TokenType.ID.value)

    def test_misspelled_keywords(self):
        for kw in [
            "integerr",
            "booleann",
            "floatt",
            "strng",
            "tru",
            "fals",
            "whil",
            "functon",
        ]:
            tokens = list(self.lexer.tokenize(kw))
            self.assertEqual(len(tokens), 1)
            self.assertEqual(tokens[0].type, TokenType.ID.value)

    def test_keywords_with_utf8_similar_characters(self):
        # Replace 'i' with Cyrillic 'і', 'a' with Cyrillic 'а', etc.
        test_cases = [
            "іf",  # Cyrillic 'і' instead of Latin 'i'
            "whіle",  # Cyrillic 'і'
            "truе",  # Cyrillic 'е'
            "fаlse",  # Cyrillic 'а'
            "strіng",  # Cyrillic 'і'
            "vоid",  # Cyrillic 'о'
        ]

        expected = [
            [(LexerError.ILLEGAL_CHARACTER.value, "і"), (TokenType.ID.value, "f")],
            [
                (TokenType.ID.value, "wh"),
                (LexerError.ILLEGAL_CHARACTER.value, "і"),
                (TokenType.ID.value, "le"),
            ],
            [(TokenType.ID.value, "tru"), (LexerError.ILLEGAL_CHARACTER.value, "е")],
            [
                (TokenType.ID.value, "f"),
                (LexerError.ILLEGAL_CHARACTER.value, "а"),
                (TokenType.ID.value, "lse"),
            ],
            [
                (TokenType.ID.value, "str"),
                (LexerError.ILLEGAL_CHARACTER.value, "і"),
                (TokenType.ID.value, "ng"),
            ],
            [
                (TokenType.ID.value, "v"),
                (LexerError.ILLEGAL_CHARACTER.value, "о"),
                (TokenType.ID.value, "id"),
            ],
        ]

        for kw in test_cases:
            tokens = list(self.lexer.tokenize(kw))
            self.assertEqual(len(tokens), len(expected[test_cases.index(kw)]))

            for i in range(len(tokens)):
                # check type and value
                self.assertEqual(tokens[i].type, expected[test_cases.index(kw)][i][0])
                self.assertEqual(tokens[i].value, expected[test_cases.index(kw)][i][1])
