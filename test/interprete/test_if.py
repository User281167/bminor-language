import unittest
from parser import Parser
from parser.model import *

from interprete import Context, Interpreter
from scanner import Lexer
from utils import clear_errors, errors_detected


class TestIfComplex(unittest.TestCase):
    def setUp(self):
        clear_errors()

    def get_output(self, code):
        """Ejecuta el código y devuelve la salida concatenada."""
        parser = Parser()
        tokens = Lexer().tokenize(code)
        ast = parser.parse(tokens)

        interpreter = Interpreter(Context(code), get_output=True)
        interpreter.interpret(ast)
        return interpreter.output

    # =========================================================================
    # 1. TEST BÁSICO DE RAMAS (True/False)
    # =========================================================================

    def test_if_true_branch(self):
        code = """
        if (true) {
            print 1;
        }
        """
        self.assertEqual(self.get_output(code), "1")

    def test_if_false_branch_no_else(self):
        code = """
        if (false) {
            print 1;
        }
        print 2;
        """
        self.assertEqual(self.get_output(code), "2")

    def test_if_else_true(self):
        code = """
        if (true) {
            print 1;
        } else {
            print 2;
        }
        print 3;
        """
        self.assertEqual(self.get_output(code), "13")

    def test_if_else_false(self):
        code = """
        if (false) {
            print 1;
        } else {
            print 2;
        }
        print 3;
        """
        self.assertEqual(self.get_output(code), "23")

    # =========================================================================
    # 2. TEST CON VARIABLES Y EXPRESIONES
    # =========================================================================

    def test_if_variable_condition_true(self):
        code = """
        a: boolean = true;
        if (a) {
            print 10;
        }
        print 20;
        """
        self.assertEqual(self.get_output(code), "1020")

    def test_if_expression_condition(self):
        code = """
        x: integer = 5;
        if (x > 3) {
            print 1;
        } else {
            print 2;
        }
        print 3;
        """
        self.assertEqual(self.get_output(code), "13")

    def test_complex_boolean_logic(self):
        """Prueba AND/OR en la condición."""
        code = """
        x: integer = 10;
        y: integer = 20;

        if (x == 10 && y > 100) {
            print "Rama1";
        } else {
            print "Rama2";
        }
        """
        # true LAND false -> false -> Rama2
        self.assertEqual(self.get_output(code), "Rama2")

    # =========================================================================
    # 3. TEST DE ESTRUCTURA "ELSE IF" (Simulada o Directa)
    # =========================================================================

    def test_chain_val_0(self):
        """Simula if - else if - else para valor 0."""
        code = """
        val: integer = 0;
        if (val == 0) {
            print 1;
        } else {
            if (val == 1) {
                print 2;
            } else {
                print 3;
            }
        }
        print 4;
        """
        self.assertEqual(self.get_output(code), "14")

    def test_chain_val_1(self):
        """Simula if - else if - else para valor 1."""
        code = """
        val: integer = 1;
        if (val == 0) {
            print 1;
        } else {
            if (val == 1) {
                print 2;
            } else {
                print 3;
            }
        }
        print 4;
        """
        self.assertEqual(self.get_output(code), "24")

    def test_chain_val_2(self):
        """Simula if - else if - else para valor 2 (cae en el último else)."""
        code = """
        val: integer = 2;
        if (val == 0) {
            print 1;
        } else {
            if (val == 1) {
                print 2;
            } else {
                print 3;
            }
        }
        print 4;
        """
        self.assertEqual(self.get_output(code), "34")

    # =========================================================================
    # 4. TEST DE ANIDAMIENTO PROFUNDO
    # =========================================================================

    def test_nested_ifs_mixed(self):
        code = """
        a: integer = 1;
        b: integer = 2;

        if (a == 1) {
            print 1;
            if (b == 2) {
                print 2;
            } else {
                print 3;
            }
            print 4;
        } else {
            print 5;
        }
        print 6;
        """
        # Traza: a==1(True) -> print 1 -> b==2(True) -> print 2 -> print 4 -> sale -> print 6
        self.assertEqual(self.get_output(code), "1246")

    def test_nested_ifs_inner_false(self):
        code = """
        a: integer = 1;
        b: integer = 99;

        if (a == 1) {
            print 1;

            if (b == 2) {
                print 2;
            } else {
                print 3; // b no es 2
            }

            print 4;
        } else {
            print 5;
        }

        print 6;
        """
        # Traza: a==1(True) -> print 1 -> b!=2(False) -> else -> print 3 -> print 4 -> print 6
        self.assertEqual(self.get_output(code), "1346")

    # =========================================================================
    # 5. TEST DE SCOPE (Shadowing en If/Else)
    # =========================================================================

    def test_scope_shadowing_if(self):
        """Verifica que declarar dentro del IF no afecte afuera."""
        code = """
        x: integer = 0;
        if (true) {
            x: integer = 10; // Variable nueva local al if
            print x;
        }
        print x; // Debe ser la original
        """
        self.assertEqual(self.get_output(code), "100")

    def test_scope_shadowing_else(self):
        """Verifica que declarar dentro del ELSE no afecte afuera."""
        code = """
        x: integer = 0;
        if (false) {
            print "No";
        } else {
            x: integer = 20; // Variable nueva local al else
            print x;
        }
        print x; // Debe ser la original
        """
        self.assertEqual(self.get_output(code), "200")

    def test_scope_assignment_mutation(self):
        """
        Verifica que SI NO declaramos (shadowing), podemos modificar
        la variable del padre.
        """
        code = """
        flag: boolean = false;
        if (true) {
            flag = true; // Modifica la variable externa
        }
        print flag;
        """
        self.assertEqual(self.get_output(code), "true")
