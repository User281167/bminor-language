from errors import clear_errors
import unittest
from parser import Parser
from scanner import Lexer
from model import *


class TestExpressions(unittest.TestCase):
    def setUp(self):
        clear_errors()
        self.lexer = Lexer()
        self.parser = Parser()

    def parse(self, code):
        clear_errors()
        tokens = self.lexer.tokenize(code)
        return self.parser.parse(tokens)

    # ========== BASIC ARITHMETIC EXPRESSIONS ==========

    def test_simple_addition(self):
        code = "x: integer = 5 + 3;"
        ast = self.parse(code)
        decl = ast.body[0]
        self.assertIsInstance(decl, VarDecl)
        self.assertEqual(decl.name, "x")
        self.assertIsInstance(decl.value, BinOper)
        self.assertEqual(decl.value.oper, "+")
        self.assertIsInstance(decl.value.left, Integer)
        self.assertEqual(decl.value.left.value, 5)
        self.assertIsInstance(decl.value.right, Integer)
        self.assertEqual(decl.value.right.value, 3)

    def test_simple_subtraction(self):
        code = "x: integer = 10 - 4;"
        ast = self.parse(code)
        decl = ast.body[0]
        self.assertIsInstance(decl, VarDecl)
        self.assertEqual(decl.name, "x")
        self.assertIsInstance(decl.value, BinOper)
        self.assertEqual(decl.value.oper, "-")
        self.assertEqual(decl.value.left.value, 10)
        self.assertEqual(decl.value.right.value, 4)

    def test_simple_multiplication(self):
        code = "x: integer = 6 * 7;"
        ast = self.parse(code)
        decl = ast.body[0]
        self.assertIsInstance(decl, VarDecl)
        self.assertEqual(decl.name, "x")
        self.assertIsInstance(decl.value, BinOper)
        self.assertEqual(decl.value.oper, "*")
        self.assertEqual(decl.value.left.value, 6)
        self.assertEqual(decl.value.right.value, 7)

    def test_simple_division(self):
        code = "x: integer = 15 / 3;"
        ast = self.parse(code)
        decl = ast.body[0]
        self.assertIsInstance(decl, VarDecl)
        self.assertEqual(decl.name, "x")
        self.assertIsInstance(decl.value, BinOper)
        self.assertEqual(decl.value.oper, "/")
        self.assertEqual(decl.value.left.value, 15)
        self.assertEqual(decl.value.right.value, 3)

    def test_modulo_operation(self):
        code = "x: integer = 17 % 5;"
        ast = self.parse(code)
        decl = ast.body[0]
        self.assertIsInstance(decl, VarDecl)
        self.assertEqual(decl.name, "x")
        self.assertIsInstance(decl.value, BinOper)
        self.assertEqual(decl.value.oper, "%")
        self.assertEqual(decl.value.left.value, 17)
        self.assertEqual(decl.value.right.value, 5)

    def test_exponentiation(self):
        code = "x: integer = 2 ^ 3;"
        ast = self.parse(code)
        decl = ast.body[0]
        self.assertIsInstance(decl, VarDecl)
        self.assertEqual(decl.name, "x")
        self.assertIsInstance(decl.value, BinOper)
        self.assertEqual(decl.value.oper, "^")
        self.assertEqual(decl.value.left.value, 2)
        self.assertEqual(decl.value.right.value, 3)

    # ========== COMPLEX ARITHMETIC EXPRESSIONS ==========

    def test_operator_precedence_multiplication_over_addition(self):
        code = "x: integer = 2 + 3 * 4;"
        ast = self.parse(code)
        decl = ast.body[0]
        self.assertIsInstance(decl, VarDecl)
        # Should parse as 2 + (3 * 4) due to precedence
        self.assertIsInstance(decl.value, BinOper)
        self.assertEqual(decl.value.oper, "+")
        self.assertEqual(decl.value.left.value, 2)

        # Left side: 3 * 4
        self.assertIsInstance(decl.value.right, BinOper)
        self.assertEqual(decl.value.right.oper, "*")
        self.assertEqual(decl.value.right.left.value, 3)
        self.assertEqual(decl.value.right.right.value, 4)

    def test_operator_precedence_exponentiation_over_multiplication(self):
        code = "x: integer = 2 * 3 ^ 2;"
        ast = self.parse(code)
        decl = ast.body[0]
        self.assertIsInstance(decl, VarDecl)
        # Should parse as 2 * (3 ^ 2) due to precedence
        self.assertIsInstance(decl.value, BinOper)
        self.assertEqual(decl.value.oper, "*")
        self.assertEqual(decl.value.left.value, 2)

        # Left side: 3 ^ 2
        self.assertIsInstance(decl.value.right, BinOper)
        self.assertEqual(decl.value.right.oper, "^")
        self.assertEqual(decl.value.right.left.value, 3)
        self.assertEqual(decl.value.right.right.value, 2)

    def test_parentheses_override_precedence(self):
        code = "x: integer = (2 + 3) * 4;"
        ast = self.parse(code)
        decl = ast.body[0]
        self.assertIsInstance(decl, VarDecl)
        # Should parse as (2 + 3) * 4 due to parentheses
        self.assertIsInstance(decl.value, BinOper)
        self.assertEqual(decl.value.oper, "*")

        # Left side: 2 + 3
        self.assertIsInstance(decl.value.left, BinOper)
        self.assertEqual(decl.value.left.oper, "+")
        self.assertEqual(decl.value.left.left.value, 2)
        self.assertEqual(decl.value.left.right.value, 3)

        self.assertEqual(decl.value.right.value, 4)

    def test_nested_parentheses(self):
        code = "x: integer = ((2 + 3) * 4) ^ 2;"
        ast = self.parse(code)
        decl = ast.body[0]
        self.assertIsInstance(decl, VarDecl)
        # Should parse as ((2 + 3) * 4) ^ 2
        self.assertIsInstance(decl.value, BinOper)
        self.assertEqual(decl.value.oper, "^")
        self.assertEqual(decl.value.right.value, 2)

        # Left side: (2 + 3) * 4
        self.assertIsInstance(decl.value.left, BinOper)
        self.assertEqual(decl.value.left.oper, "*")
        self.assertEqual(decl.value.left.right.value, 4)

        # Left side: (2 + 3)
        self.assertIsInstance(decl.value.left.left, BinOper)
        self.assertEqual(decl.value.left.left.oper, "+")
        self.assertEqual(decl.value.left.left.left.value, 2)
        self.assertEqual(decl.value.left.left.right.value, 3)

    # ========== UNARY OPERATIONS ==========

    def test_unary_negation(self):
        code = "x: integer = -5;"
        ast = self.parse(code)
        decl = ast.body[0]
        self.assertIsInstance(decl, VarDecl)
        self.assertEqual(decl.name, "x")
        self.assertIsInstance(decl.value, UnaryOper)
        self.assertEqual(decl.value.oper, "-")
        self.assertIsInstance(decl.value.expr, Integer)
        self.assertEqual(decl.value.expr.value, 5)

    def test_unary_negation_with_expression(self):
        code = "x: integer = -(3 + 2);"
        ast = self.parse(code)
        decl = ast.body[0]
        self.assertIsInstance(decl, VarDecl)
        self.assertEqual(decl.name, "x")

        self.assertIsInstance(decl.value, UnaryOper)
        self.assertEqual(decl.value.oper, "-")

        # expr: 3 + 2
        self.assertIsInstance(decl.value.expr, BinOper)
        self.assertEqual(decl.value.expr.oper, "+")
        self.assertEqual(decl.value.expr.left.value, 3)
        self.assertEqual(decl.value.expr.right.value, 2)

    def test_min_unary_negation_with_expression(self):
        code = "x: float = pi + -(3 + 2);"
        ast = self.parse(code)
        decl = ast.body[0]
        expr = decl.value

        self.assertIsInstance(expr, BinOper)
        self.assertEqual(expr.oper, "+")

        # Left side: pi
        self.assertIsInstance(expr.left, VarLoc)
        self.assertEqual(expr.left.name, "pi")

        # Right side: -(3 + 2)
        self.assertIsInstance(expr.right, UnaryOper)
        self.assertEqual(expr.right.oper, "-")

        # expr: 3 + 2
        self.assertIsInstance(expr.right.expr, BinOper)
        self.assertEqual(expr.right.expr.oper, "+")
        self.assertEqual(expr.right.expr.left.value, 3)
        self.assertEqual(expr.right.expr.right.value, 2)

    # ========== FLOAT ARITHMETIC EXPRESSIONS ==========

    def test_float_addition(self):
        code = "f: float = 3.14 + 2.71;"
        ast = self.parse(code)
        decl = ast.body[0]
        self.assertIsInstance(decl, VarDecl)
        self.assertEqual(decl.name, "f")
        self.assertIsInstance(decl.value, BinOper)
        self.assertEqual(decl.value.oper, "+")
        self.assertIsInstance(decl.value.left, Float)
        self.assertAlmostEqual(decl.value.left.value, 3.14, places=7)
        self.assertIsInstance(decl.value.right, Float)
        self.assertAlmostEqual(decl.value.right.value, 2.71, places=7)

    def test_float_scientific_notation(self):
        code = "f: float = 1.5e2 + 2.5E-1;"
        ast = self.parse(code)
        decl = ast.body[0]
        self.assertIsInstance(decl, VarDecl)
        self.assertEqual(decl.name, "f")
        self.assertIsInstance(decl.value, BinOper)
        self.assertEqual(decl.value.oper, "+")
        self.assertIsInstance(decl.value.left, Float)
        self.assertAlmostEqual(decl.value.left.value, 150.0, places=7)
        self.assertIsInstance(decl.value.right, Float)
        self.assertAlmostEqual(decl.value.right.value, 0.25, places=7)

    def test_mixed_integer_float_expression(self):
        code = "f: float = 5 + 3.14;"
        ast = self.parse(code)
        decl = ast.body[0]
        self.assertIsInstance(decl, VarDecl)
        self.assertEqual(decl.name, "f")
        self.assertIsInstance(decl.value, BinOper)
        self.assertEqual(decl.value.oper, "+")
        self.assertIsInstance(decl.value.left, Integer)
        self.assertEqual(decl.value.left.value, 5)
        self.assertIsInstance(decl.value.right, Float)
        self.assertAlmostEqual(decl.value.right.value, 3.14, places=7)

    def test_mixed_with_vars(self):
        code = "x: integer = m*x + y;"
        ast = self.parse(code)
        decl = ast.body[0]
        self.assertIsInstance(decl, VarDecl)
        self.assertEqual(decl.name, "x")
        self.assertIsInstance(decl.value, BinOper)
        self.assertEqual(decl.value.oper, "+")
        self.assertIsInstance(decl.value.left, BinOper)
        self.assertEqual(decl.value.left.oper, "*")
        # var decl
        self.assertEqual(decl.value.left.left.name, "m")
        self.assertEqual(decl.value.left.right.name, "x")
        self.assertEqual(decl.value.right.name, "y")

    def test_mixed_with_vars_literals(self):
        code = "x: float = (m*x + y) + 5;"
        ast = self.parse(code)
        decl = ast.body[0]
        self.assertIsInstance(decl, VarDecl)
        self.assertEqual(decl.name, "x")
        self.assertIsInstance(decl.value, BinOper)

        # Right side: expr + expr
        self.assertEqual(decl.value.oper, "+")
        self.assertIsInstance(decl.value.left, BinOper)

        # Left side: m*x + y
        self.assertEqual(decl.value.left.oper, "+")

        # var decl
        self.assertEqual(decl.value.left.left.left.name, "m")
        self.assertEqual(decl.value.left.left.right.name, "x")
        self.assertEqual(decl.value.left.right.name, "y")

        # Literal
        self.assertIsInstance(decl.value.right, Integer)
        self.assertEqual(decl.value.right.value, 5)

    def test_very_complex_expression(self):
        code = "x: integer = ((2 + 3) * 4) ^ 2 - (10 / 2);"
        ast = self.parse(code)
        decl = ast.body[0]
        self.assertIsInstance(decl, VarDecl)
        self.assertEqual(decl.name, "x")
        # This should parse as: ((2 + 3) * 4) ^ 2 - (10 / 2)
        self.assertIsInstance(decl.value, BinOper)
        self.assertEqual(decl.value.oper, "-")

        # Left side: ((2 + 3) * 4) ^ 2
        self.assertIsInstance(decl.value.left, BinOper)
        self.assertEqual(decl.value.left.oper, "^")
        self.assertIsInstance(decl.value.left.left, BinOper)
        self.assertEqual(decl.value.left.left.oper, "*")
        self.assertIsInstance(decl.value.left.left.left, BinOper)
        self.assertEqual(decl.value.left.left.left.oper, "+")
        self.assertEqual(decl.value.left.left.left.left.value, 2)
        self.assertEqual(decl.value.left.left.left.right.value, 3)
        self.assertEqual(decl.value.left.left.right.value, 4)
        self.assertEqual(decl.value.left.right.value, 2)

        # Right side: (10 / 2)
        self.assertIsInstance(decl.value.right, BinOper)
        self.assertEqual(decl.value.right.oper, "/")
        self.assertEqual(decl.value.right.left.value, 10)
        self.assertEqual(decl.value.right.right.value, 2)

    def test_extra_parentheses(self):
        code = "x: integer = ((5 + 3));"
        # This should actually parse correctly due to grouping
        ast = self.parse(code)
        decl = ast.body[0]
        self.assertIsInstance(decl, VarDecl)
        self.assertEqual(decl.name, "x")
        self.assertIsInstance(decl.value, BinOper)
        self.assertEqual(decl.value.oper, "+")
        self.assertEqual(decl.value.left.value, 5)
        self.assertEqual(decl.value.right.value, 3)

    def test_plus_unary_negation_with_expression(self):
        code = "x: float = pi - +(3 + 2);"
        self.parse(code)
        ast = self.parse(code)
        decl = ast.body[0]
        expr = decl.value
        self.assertIsInstance(expr, BinOper)
        self.assertEqual(expr.oper, "-")
        # Left side: pi
        self.assertIsInstance(expr.left, VarLoc)
        self.assertEqual(expr.left.name, "pi")
        # Right side: +(3 + 2)
        self.assertIsInstance(expr.right, UnaryOper)
        self.assertEqual(expr.right.oper, "+")
        self.assertIsInstance(expr.right.expr, BinOper)
        self.assertEqual(expr.right.expr.oper, "+")
        self.assertEqual(expr.right.expr.left.value, 3)
        self.assertEqual(expr.right.expr.right.value, 2)

    def test_invalid_operator_sequence(self):
        code = "x: integer = 5 + + 3;"
        ast = self.parse(code)
        decl = ast.body[0]
        self.assertIsInstance(decl, VarDecl)
        self.assertEqual(decl.name, "x")
        self.assertIsInstance(decl.value, BinOper)
        self.assertEqual(decl.value.oper, "+")
        self.assertIsInstance(decl.value.left, Integer)
        self.assertEqual(decl.value.left.value, 5)
        self.assertIsInstance(decl.value.right, UnaryOper)
        self.assertEqual(decl.value.right.oper, "+")
        self.assertIsInstance(decl.value.right.expr, Integer)
