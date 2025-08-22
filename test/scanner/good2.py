import unittest
from scanner import Lexer, TokenType


class TestKeywords(unittest.TestCase):
    def setUp(self):
        self.lexer = Lexer()

    def test_keywords_and_numbers_and_symbols(self):
        test_input = (
            "array auto boolean char else false float for function if integer print return string true void while     // this is a comment"
        )
        tokens = list(self.lexer.tokenize(test_input))
        expected = [
            TokenType.ARRAY.value,
            TokenType.AUTO.value,
            TokenType.BOOLEAN.value,
            TokenType.CHAR.value,
            TokenType.ELSE.value,
            TokenType.FALSE.value,
            TokenType.FLOAT.value,
            TokenType.FOR.value,
            TokenType.FUNCTION.value,
            TokenType.IF.value,
            TokenType.INTEGER.value,
            TokenType.PRINT.value,
            TokenType.RETURN.value,
            TokenType.STRING.value,
            TokenType.TRUE.value,
            TokenType.VOID.value,
            TokenType.WHILE.value,
        ]
        # Check token types
        self.assertEqual([t.type for t in tokens], expected)

    def test_array_keyword(self):
        tokens = list(self.lexer.tokenize("array"))
        self.assertEqual(len(tokens), 1)
        self.assertEqual(tokens[0].type, TokenType.ARRAY.value)

    def test_auto_keyword(self):
        tokens = list(self.lexer.tokenize("auto"))
        self.assertEqual(len(tokens), 1)
        self.assertEqual(tokens[0].type, TokenType.AUTO.value)

    def test_boolean_keyword(self):
        tokens = list(self.lexer.tokenize("boolean"))
        self.assertEqual(len(tokens), 1)
        self.assertEqual(tokens[0].type, TokenType.BOOLEAN.value)

    def test_char_keyword(self):
        tokens = list(self.lexer.tokenize("char"))
        self.assertEqual(len(tokens), 1)
        self.assertEqual(tokens[0].type, TokenType.CHAR.value)

    def test_else_keyword(self):
        tokens = list(self.lexer.tokenize("else"))
        self.assertEqual(len(tokens), 1)
        self.assertEqual(tokens[0].type, TokenType.ELSE.value)

    def test_false_keyword(self):
        tokens = list(self.lexer.tokenize("false"))
        self.assertEqual(len(tokens), 1)
        self.assertEqual(tokens[0].type, TokenType.FALSE.value)

    def test_float_keyword(self):
        tokens = list(self.lexer.tokenize("float"))
        self.assertEqual(len(tokens), 1)
        self.assertEqual(tokens[0].type, TokenType.FLOAT.value)

    def test_for_keyword(self):
        tokens = list(self.lexer.tokenize("for"))
        self.assertEqual(len(tokens), 1)
        self.assertEqual(tokens[0].type, TokenType.FOR.value)

    def test_function_keyword(self):
        tokens = list(self.lexer.tokenize("function"))
        self.assertEqual(len(tokens), 1)
        self.assertEqual(tokens[0].type, TokenType.FUNCTION.value)

    def test_if_keyword(self):
        tokens = list(self.lexer.tokenize("if"))
        self.assertEqual(len(tokens), 1)
        self.assertEqual(tokens[0].type, TokenType.IF.value)

    def test_integer_keyword(self):
        tokens = list(self.lexer.tokenize("integer"))
        self.assertEqual(len(tokens), 1)
        self.assertEqual(tokens[0].type, TokenType.INTEGER.value)

    def test_print_keyword(self):
        tokens = list(self.lexer.tokenize("print"))
        self.assertEqual(len(tokens), 1)
        self.assertEqual(tokens[0].type, TokenType.PRINT.value)

    def test_return_keyword(self):
        tokens = list(self.lexer.tokenize("return"))
        self.assertEqual(len(tokens), 1)
        self.assertEqual(tokens[0].type, TokenType.RETURN.value)

    def test_string_keyword(self):
        tokens = list(self.lexer.tokenize("string"))
        self.assertEqual(len(tokens), 1)
        self.assertEqual(tokens[0].type, TokenType.STRING.value)

    def test_true_keyword(self):
        tokens = list(self.lexer.tokenize("true"))
        self.assertEqual(len(tokens), 1)
        self.assertEqual(tokens[0].type, TokenType.TRUE.value)

    def test_void_keyword(self):
        tokens = list(self.lexer.tokenize("void"))
        self.assertEqual(len(tokens), 1)
        self.assertEqual(tokens[0].type, TokenType.VOID.value)

    def test_while_keyword(self):
        tokens = list(self.lexer.tokenize("while"))
        self.assertEqual(len(tokens), 1)
        self.assertEqual(tokens[0].type, TokenType.WHILE.value)

    def test_keywords_integers_floats_mixed(self):
        test_input = "array 123 float 3.14 integer 42 for .42"
        tokens = list(self.lexer.tokenize(test_input))
        expected = [
            TokenType.ARRAY.value,
            TokenType.INTEGER_LITERAL.value,
            TokenType.FLOAT.value,
            TokenType.FLOAT_LITERAL.value,
            TokenType.INTEGER.value,
            TokenType.INTEGER_LITERAL.value,
            TokenType.FOR.value,
            TokenType.FLOAT_LITERAL.value
        ]
        self.assertEqual([t.type for t in tokens], expected)
        self.assertEqual(tokens[1].value, 123)
        self.assertEqual(tokens[3].value, 3.14)
        self.assertEqual(tokens[5].value, 42)
        self.assertEqual(tokens[7].value, 0.42)

    def test_keywords_and_numbers_with_symbols(self):
        test_input = "if 1 + 2.0 - else 0.5;"
        tokens = list(self.lexer.tokenize(test_input))
        expected = [
            TokenType.IF.value,
            TokenType.INTEGER_LITERAL.value,
            '+',
            TokenType.FLOAT_LITERAL.value,
            '-',
            TokenType.ELSE.value,
            TokenType.FLOAT_LITERAL.value,
            ';'
        ]
        self.assertEqual([t.type for t in tokens], expected)
        self.assertEqual(tokens[1].value, 1)
        self.assertEqual(tokens[3].value, 2.0)
        self.assertEqual(tokens[6].value, 0.5)

    def test_keywords_and_numbers_with_multiple_lines(self):
        test_input = "print 10\nreturn 2.5\nwhile 0"
        tokens = list(self.lexer.tokenize(test_input))
        expected = [
            TokenType.PRINT.value,
            TokenType.INTEGER_LITERAL.value,
            TokenType.RETURN.value,
            TokenType.FLOAT_LITERAL.value,
            TokenType.WHILE.value,
            TokenType.INTEGER_LITERAL.value
        ]
        self.assertEqual([t.type for t in tokens], expected)
        self.assertEqual(tokens[1].value, 10)
        self.assertEqual(tokens[3].value, 2.5)
        self.assertEqual(tokens[5].value, 0)

    def test_initializations_with_keywords(self):
        test_input = (
            "x : integer = 42;\n"
            "y : float = 3.14;\n"
            "flag : boolean = true;\n"
            "msg : string = false;"
        )
        tokens = list(self.lexer.tokenize(test_input))
        expected_types = [
            TokenType.ID.value, ':', TokenType.INTEGER.value, '=', TokenType.INTEGER_LITERAL.value, ';',
            TokenType.ID.value, ':', TokenType.FLOAT.value, '=', TokenType.FLOAT_LITERAL.value, ';',
            TokenType.ID.value, ':', TokenType.BOOLEAN.value, '=', TokenType.TRUE.value, ';',
            TokenType.ID.value, ':', TokenType.STRING.value, '=', TokenType.FALSE.value, ';'
        ]
        self.assertEqual([t.type for t in tokens], expected_types)
        self.assertEqual(tokens[0].value, 'x')
        self.assertEqual(tokens[4].value, 42)
        self.assertEqual(tokens[6].value, 'y')
        self.assertEqual(tokens[10].value, 3.14)
        self.assertEqual(tokens[12].value, 'flag')
        self.assertEqual(tokens[16].type, TokenType.TRUE.value)
        self.assertEqual(tokens[18].value, 'msg')
        self.assertEqual(tokens[22].type, TokenType.FALSE.value)
