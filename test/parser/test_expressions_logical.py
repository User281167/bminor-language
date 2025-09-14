from scanner import OperatorType
import unittest
from parser import Parser
from scanner import Lexer
from model import *


class TestLogicalExpressions(unittest.TestCase):
    def setUp(self):
        self.lexer = Lexer()
        self.parser = Parser()

    def parse(self, code):
        tokens = self.lexer.tokenize(code)
        return self.parser.parse(tokens)

    # ========== LOGICAL EXPRESSIONS ==========

    def test_logical_and(self):
        code = "b: boolean = true && false;"
        ast = self.parse(code)
        decl = ast.body[0]
        self.assertIsInstance(decl, VarDecl)
        self.assertEqual(decl.name, "b")
        self.assertIsInstance(decl.value, BinOper)
        self.assertEqual(decl.value.oper, OperatorType.LAND.value)
        self.assertIsInstance(decl.value.left, Boolean)
        self.assertEqual(decl.value.left.value, True)
        self.assertIsInstance(decl.value.right, Boolean)
        self.assertEqual(decl.value.right.value, False)

    def test_logical_or(self):
        code = "b: boolean = true ` false;"
        ast = self.parse(code)
        decl = ast.body[0]

        self.assertIsInstance(decl, VarDecl)
        self.assertEqual(decl.name, "b")
        self.assertIsInstance(decl.value, BinOper)
        self.assertEqual(decl.value.oper, OperatorType.LOR.value)
        self.assertIsInstance(decl.value.left, Boolean)
        self.assertEqual(decl.value.left.value, True)
        self.assertIsInstance(decl.value.right, Boolean)
        self.assertEqual(decl.value.right.value, False)

    def test_complex_logical_expression(self):
        code = "b: boolean = (5 > 3) && (2 < 4);"
        ast = self.parse(code)
        decl = ast.body[0]
        self.assertIsInstance(decl, VarDecl)
        self.assertEqual(decl.name, "b")

        # expr && expr
        self.assertIsInstance(decl.value, BinOper)
        self.assertEqual(decl.value.oper, OperatorType.LAND.value)

        # 5 > 3
        self.assertIsInstance(decl.value.left, BinOper)
        self.assertEqual(decl.value.left.oper, ">")
        self.assertEqual(decl.value.left.left.value, 5)
        self.assertEqual(decl.value.left.right.value, 3)

        # 2 < 4
        self.assertIsInstance(decl.value.right, BinOper)
        self.assertEqual(decl.value.right.oper, "<")
        self.assertEqual(decl.value.right.left.value, 2)
        self.assertEqual(decl.value.right.right.value, 4)

    # ========== COMPLEX MIXED EXPRESSIONS ==========

    def test_arithmetic_with_comparison(self):
        code = "b: boolean = (2 + 3) > (4 - 1) && (4 - 1) <= (2 + 3);"
        ast = self.parse(code)
        decl = ast.body[0]
        self.assertIsInstance(decl, VarDecl)
        self.assertEqual(decl.name, "b")

        # expr && expr
        self.assertIsInstance(decl.value, BinOper)
        self.assertEqual(decl.value.oper, OperatorType.LAND.value)

        # (2 + 3) > (4 - 1)
        self.assertIsInstance(decl.value.left, BinOper)
        self.assertEqual(decl.value.left.oper, ">")

        # (4 - 1) <= (2 + 3)
        self.assertIsInstance(decl.value.right, BinOper)
        self.assertEqual(decl.value.right.oper, "<=")

    def test_nested_logical_expression(self):
        code = "b: boolean = (5 > 3) && ((2 + 1) == 3) ` false;"
        ast = self.parse(code)

        decl = ast.body[0]
        self.assertIsInstance(decl, VarDecl)
        self.assertEqual(decl.name, "b")

        # (expr && expr) ` expr
        self.assertIsInstance(decl.value, BinOper)
        self.assertEqual(decl.value.oper, OperatorType.LOR.value)

        # expr && expr
        self.assertIsInstance(decl.value.left, BinOper)
        self.assertEqual(decl.value.left.oper, OperatorType.LAND.value)

        # 5 > 3
        self.assertIsInstance(decl.value.left.left, BinOper)
        self.assertEqual(decl.value.left.left.oper, ">")
        self.assertEqual(decl.value.left.left.left.value, 5)
        self.assertEqual(decl.value.left.left.right.value, 3)

        # (2 + 1) == 3
        self.assertIsInstance(decl.value.left.right, BinOper)
        self.assertEqual(decl.value.left.right.oper, "==")
        self.assertIsInstance(decl.value.left.right.left, BinOper)
        self.assertEqual(decl.value.left.right.right.value, 3)

        # false
        self.assertIsInstance(decl.value.right, Boolean)
        self.assertEqual(decl.value.right.value, False)

    def test_not_expression(self):
        code = "b: boolean = !true;"
        ast = self.parse(code)
        decl = ast.body[0]
        self.assertIsInstance(decl, VarDecl)
        self.assertEqual(decl.name, "b")

        self.assertIsInstance(decl.value, UnaryOper)
        self.assertEqual(decl.value.oper, "!")
        self.assertIsInstance(decl.value.expr, Boolean)
        self.assertEqual(decl.value.expr.value, True)

    def test_complex_not_expression(self):
        code = "b: boolean = !(!(5 > 3) && !(2 < 4));"
        ast = self.parse(code)
        decl = ast.body[0]
        self.assertIsInstance(decl, VarDecl)

        # !(!expr && !expr)
        self.assertIsInstance(decl.value, UnaryOper)
        self.assertEqual(decl.value.oper, "!")

        # expr && expr
        self.assertIsInstance(decl.value.expr, BinOper)
        self.assertEqual(decl.value.expr.oper, OperatorType.LAND.value)

        # !(5 > 3)
        self.assertIsInstance(decl.value.expr.left, UnaryOper)
        self.assertEqual(decl.value.expr.left.oper, "!")

        # 5 > 3
        self.assertIsInstance(decl.value.expr.left.expr, BinOper)
        self.assertEqual(decl.value.expr.left.expr.oper, ">")
        self.assertEqual(decl.value.expr.left.expr.left.value, 5)
        self.assertEqual(decl.value.expr.left.expr.right.value, 3)

        # !(2 < 4)
        self.assertIsInstance(decl.value.expr.right, UnaryOper)
        self.assertEqual(decl.value.expr.right.oper, "!")

        # 2 < 4
        self.assertIsInstance(decl.value.expr.right.expr, BinOper)
        self.assertEqual(decl.value.expr.right.expr.oper, "<")
        self.assertEqual(decl.value.expr.right.expr.left.value, 2)
        self.assertEqual(decl.value.expr.right.expr.right.value, 4)
