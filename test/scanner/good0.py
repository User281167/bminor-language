import unittest
from scanner import Lexer


class TestComments(unittest.TestCase):
    def setUp(self):
        self.lexer = Lexer()

    def test_valid_cpp_comment(self):
        test_input = "// This is a valid C++ comment\n"
        tokens = list(self.lexer.tokenize(test_input))
        self.assertEqual(len(tokens), 0)

    def test_valid_multiline_comment(self):
        test_input = "/* This is a valid\nmultiline comment */\n"
        tokens = list(self.lexer.tokenize(test_input))
        self.assertEqual(len(tokens), 0)

    def test_valid_nested_comments(self):
        # valid nested comments
        test_input = "/* This is a comment with // nested single-line comment */"
        tokens = list(self.lexer.tokenize(test_input))
        self.assertEqual(len(tokens), 0)

        # invalid nested comments
        # cannot detect valid end comment
        test_input2 = "/* comment /* nested */ remaining */"
        tokens2 = list(self.lexer.tokenize(test_input2))
        # because first */ close comment and  remaining */ is not ignored
        self.assertTrue(len(tokens2) > 0)

    def test_inline_comment(self):
        test_input = "x = 42; // This is an inline comment\n"
        tokens = list(self.lexer.tokenize(test_input))
        self.assertEqual(len(tokens), 4)  # x, =, 42, ;

    def test_comment_with_newlines(self):
        test_input = "/* This is a comment\nthat spans multiple\nlines */\n"
        tokens = list(self.lexer.tokenize(test_input))
        self.assertEqual(len(tokens), 0)
        self.assertEqual(self.lexer.lineno, 4)  # 4 newlines in comment

    def test_comment_with_newlines_and_tokens(self):
        test_input = "x = 42;/* This is a comment\nthat spans multiple\nlines */\n"
        tokens = list(self.lexer.tokenize(test_input))
        self.assertEqual(len(tokens), 4)  # x, =, 42, ;
        self.assertEqual(self.lexer.lineno, 4)  # 4 newline counting comment

    def test_comment_tokens_in_comment(self):
        test_input = "/* This is a comment\nthat spans multiple\nlines x = 42;\n a: float = 32; */\n"
        tokens = list(self.lexer.tokenize(test_input))
        self.assertEqual(len(tokens), 0)

    def test_ignored_tabs_and_spaces(self):
        test_input = "    \t   // Comment with spaces and tabs\n"
        tokens = list(self.lexer.tokenize(test_input))
        self.assertEqual(len(tokens), 0)

    # def test_comment_delimiters_in_string(self):
    #     test_input = '"This is not a comment: /* */"'
    #     tokens = list(self.lexer.tokenize(test_input))
    #     # Should not be treated as comment
    #     self.assertIn('STRING', [token.type for token in tokens])
