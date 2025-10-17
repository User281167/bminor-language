import unittest

from scanner import Lexer


class TestComments(unittest.TestCase):
    def setUp(self):
        self.lexer = Lexer()

    def test_invalid_cpp_comment(self):
        # token cannot be ignored
        # / can interpreta as DIVISION token
        test_input = "/ This is a valid C++ comment\n"
        tokens = list(self.lexer.tokenize(test_input))
        self.assertGreater(len(tokens), 0)  # At least one token (the '/')

    def test_invalid_multiline_comment_close(self):
        test_input = "/* This is an unclosed\nmultiline comment \n"
        tokens = list(self.lexer.tokenize(test_input))
        self.assertGreater(len(tokens), 0)

    def test_invalid_multiline_comment_open(self):
        test_input = "This is an unclosed\nmultiline comment */\n"
        tokens = list(self.lexer.tokenize(test_input))
        self.assertGreater(len(tokens), 0)

    def test_invalid_multiline_comment_start(self):
        test_input = "*/ This is an unclosed\nmultiline comment \n"
        tokens = list(self.lexer.tokenize(test_input))
        self.assertGreater(len(tokens), 0)

    def test_close_comment_without_open(self):
        test_input = "*/"
        tokens = list(self.lexer.tokenize(test_input))
        self.assertGreater(len(tokens), 0)

    # def test_valid_nested_comments(self):
    #     test_input = """
    #     /* This is a comment with /* nested multi-line comment */ still in comment \n\n*/
    #     """
    #     tokens = list(self.lexer.tokenize(test_input))
    #     self.assertEqual(len(tokens), 0)
