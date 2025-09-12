import unittest
from scanner import Lexer, TokenType, OperatorType, LiteralType


class TestValidFunctionTokens(unittest.TestCase):
    def setUp(self):
        self.lexer = Lexer()

    def test_simple_function_declaration(self):
        tokens = list(self.lexer.tokenize(
            'square: function integer ( x: integer ) = { return x^2; }'))
        expected_types = [
            TokenType.ID.value,         # square
            LiteralType.COLON.value,   # :
            TokenType.FUNCTION.value,   # function
            TokenType.INTEGER.value,    # integer
            LiteralType.LPAREN.value,  # (
            TokenType.ID.value,         # x
            LiteralType.COLON.value,   # :
            TokenType.INTEGER.value,    # integer
            LiteralType.RPAREN.value,  # )
            LiteralType.EQUAL.value,   # =
            LiteralType.LBRACE.value,  # {
            TokenType.RETURN.value,     # return
            TokenType.ID.value,         # x
            LiteralType.CARET.value,   # ^
            TokenType.INTEGER_LITERAL.value,  # 2
            LiteralType.SEMICOLON.value,     # ;
            LiteralType.RBRACE.value   # }
        ]
        self.assertEqual([t.type for t in tokens], expected_types)

    def test_void_function_with_multiple_params(self):
        tokens = list(self.lexer.tokenize('''
            printSum: function void ( a: integer, b: integer ) = {
                print a + b;
                return;
            }
        '''))
        expected_types = [
            TokenType.ID.value,         # printSum
            LiteralType.COLON.value,   # :
            TokenType.FUNCTION.value,   # function
            TokenType.VOID.value,       # void
            LiteralType.LPAREN.value,  # (
            TokenType.ID.value,         # a
            LiteralType.COLON.value,   # :
            TokenType.INTEGER.value,    # integer
            LiteralType.COMMA.value,   # ,
            TokenType.ID.value,         # b
            LiteralType.COLON.value,   # :
            TokenType.INTEGER.value,    # integer
            LiteralType.RPAREN.value,  # )
            LiteralType.EQUAL.value,   # =
            LiteralType.LBRACE.value,  # {
            TokenType.PRINT.value,      # print
            TokenType.ID.value,         # a
            LiteralType.PLUS.value,    # +
            TokenType.ID.value,         # b
            LiteralType.SEMICOLON.value,  # ;
            TokenType.RETURN.value,     # return
            LiteralType.SEMICOLON.value,  # ;
            LiteralType.RBRACE.value   # }
        ]
        self.assertEqual([t.type for t in tokens], expected_types)

    def test_function_with_array_param(self):
        tokens = list(self.lexer.tokenize('''
            sum: function integer ( arr: array [] integer ) = {
                i: integer = 0;
                sum: integer = 0;
                for(i=0;i<10;i++) {
                    sum = sum + arr[i];
                }
                return sum;
            }
        '''))
        expected_types = [
            TokenType.ID.value,         # sum
            LiteralType.COLON.value,   # :
            TokenType.FUNCTION.value,   # function
            TokenType.INTEGER.value,    # integer
            LiteralType.LPAREN.value,  # (
            TokenType.ID.value,         # arr
            LiteralType.COLON.value,   # :
            TokenType.ARRAY.value,      # array
            LiteralType.LBRACKET.value,  # [
            LiteralType.RBRACKET.value,  # ]
            TokenType.INTEGER.value,    # integer
            LiteralType.RPAREN.value,  # )
            LiteralType.EQUAL.value,   # =
            LiteralType.LBRACE.value,  # {
            TokenType.ID.value,         # i
            LiteralType.COLON.value,   # :
            TokenType.INTEGER.value,    # integer
            LiteralType.EQUAL.value,   # =
            TokenType.INTEGER_LITERAL.value,  # 0
            LiteralType.SEMICOLON.value,  # ;
            TokenType.ID.value,         # sum
            LiteralType.COLON.value,   # :
            TokenType.INTEGER.value,    # integer
            LiteralType.EQUAL.value,   # =
            TokenType.INTEGER_LITERAL.value,  # 0
            LiteralType.SEMICOLON.value,  # ;
            TokenType.FOR.value,        # for
            LiteralType.LPAREN.value,  # (
            TokenType.ID.value,         # i
            LiteralType.EQUAL.value,   # =
            TokenType.INTEGER_LITERAL.value,  # 0
            LiteralType.SEMICOLON.value,  # ;
            TokenType.ID.value,         # i
            OperatorType.LT.value,        # <
            TokenType.INTEGER_LITERAL.value,  # 10
            LiteralType.SEMICOLON.value,  # ;
            TokenType.ID.value,         # i
            OperatorType.INC.value,  # ++
            LiteralType.RPAREN.value,  # )
            LiteralType.LBRACE.value,  # {
            TokenType.ID.value,         # sum
            LiteralType.EQUAL.value,   # =
            TokenType.ID.value,         # sum
            LiteralType.PLUS.value,    # +
            TokenType.ID.value,         # arr
            LiteralType.LBRACKET.value,  # [
            TokenType.ID.value,         # i
            LiteralType.RBRACKET.value,  # ]
            LiteralType.SEMICOLON.value,  # ;
            LiteralType.RBRACE.value,  # }
            TokenType.RETURN.value,     # return
            TokenType.ID.value,         # sum
            LiteralType.SEMICOLON.value,  # ;
            LiteralType.RBRACE.value   # }
        ]
        self.assertEqual([t.type for t in tokens], expected_types)

    def test_function_with_if_else_body(self):
        tokens = list(self.lexer.tokenize('''
            max: function integer ( a: integer, b: integer ) = {
                if(a > b) {
                    return a;
                } else {
                    return b;
                }
            }
        '''))
        expected_types = [
            TokenType.ID.value,         # max
            LiteralType.COLON.value,   # :
            TokenType.FUNCTION.value,   # function
            TokenType.INTEGER.value,    # integer
            LiteralType.LPAREN.value,  # (
            TokenType.ID.value,         # a
            LiteralType.COLON.value,   # :
            TokenType.INTEGER.value,    # integer
            LiteralType.COMMA.value,   # ,
            TokenType.ID.value,         # b
            LiteralType.COLON.value,   # :
            TokenType.INTEGER.value,    # integer
            LiteralType.RPAREN.value,  # )
            LiteralType.EQUAL.value,   # =
            LiteralType.LBRACE.value,  # {
            TokenType.IF.value,         # if
            LiteralType.LPAREN.value,  # (
            TokenType.ID.value,         # a
            OperatorType.GT.value,        # >
            TokenType.ID.value,         # b
            LiteralType.RPAREN.value,  # )
            LiteralType.LBRACE.value,  # {
            TokenType.RETURN.value,     # return
            TokenType.ID.value,         # a
            LiteralType.SEMICOLON.value,  # ;
            LiteralType.RBRACE.value,  # }
            TokenType.ELSE.value,       # else
            LiteralType.LBRACE.value,  # {
            TokenType.RETURN.value,     # return
            TokenType.ID.value,         # b
            LiteralType.SEMICOLON.value,  # ;
            LiteralType.RBRACE.value,  # }
            LiteralType.RBRACE.value   # }
        ]
        self.assertEqual([t.type for t in tokens], expected_types)

    def test_function_with_string_param(self):
        tokens = list(self.lexer.tokenize('''
            print_n_times: function void ( msg: string, n: integer ) = {
                i: integer;
                for(i=0;i<n;i++) {
                    print msg;
                }
            }
        '''))
        expected_types = [
            TokenType.ID.value,         # print_n_times
            LiteralType.COLON.value,   # :
            TokenType.FUNCTION.value,   # function
            TokenType.VOID.value,       # void
            LiteralType.LPAREN.value,  # (
            TokenType.ID.value,         # msg
            LiteralType.COLON.value,   # :
            TokenType.STRING.value,     # string
            LiteralType.COMMA.value,   # ,
            TokenType.ID.value,         # n
            LiteralType.COLON.value,   # :
            TokenType.INTEGER.value,    # integer
            LiteralType.RPAREN.value,  # )
            LiteralType.EQUAL.value,   # =
            LiteralType.LBRACE.value,  # {
            TokenType.ID.value,         # i
            LiteralType.COLON.value,   # :
            TokenType.INTEGER.value,    # integer
            LiteralType.SEMICOLON.value,  # ;
            TokenType.FOR.value,        # for
            LiteralType.LPAREN.value,  # (
            TokenType.ID.value,         # i
            LiteralType.EQUAL.value,   # =
            TokenType.INTEGER_LITERAL.value,  # 0
            LiteralType.SEMICOLON.value,  # ;
            TokenType.ID.value,         # i
            OperatorType.LT.value,        # <
            TokenType.ID.value,         # n
            LiteralType.SEMICOLON.value,  # ;
            TokenType.ID.value,         # i
            OperatorType.INC.value,  # ++
            LiteralType.RPAREN.value,  # )
            LiteralType.LBRACE.value,  # {
            TokenType.PRINT.value,      # print
            TokenType.ID.value,         # msg
            LiteralType.SEMICOLON.value,  # ;
            LiteralType.RBRACE.value,  # }
            LiteralType.RBRACE.value   # }
        ]
        self.assertEqual([t.type for t in tokens], expected_types)

    def test_function_with_no_space_after_colon(self):
        # Missing space after colon (should still work, testing for robustness)
        tokens = list(self.lexer.tokenize('func:function void () = { }'))
        # Should tokenize correctly despite missing space
        expected_types = [
            TokenType.ID.value,         # func
            ':',                        # :
            TokenType.FUNCTION.value,   # function
            TokenType.VOID.value,       # void
            '(',                        # (
            ')',                        # )
            '=',                        # =
            '{',                        # {
            '}',                        # }
        ]
        self.assertEqual([t.type for t in tokens], expected_types)
