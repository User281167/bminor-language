import unittest
from parser import Parser
from parser.model import *

from interprete import Context, Interpreter
from scanner import Lexer
from utils import clear_errors, errors_detected


class TestBreakStmt(unittest.TestCase):
    def setUp(self):
        clear_errors()

    def get_output(self, code):
        """Ejecuta código y retorna la salida concatenada."""
        parser = Parser()
        tokens = Lexer().tokenize(code)
        ast = parser.parse(tokens)

        interpreter = Interpreter(Context(code), get_output=True)
        interpreter.interpret(ast)
        return interpreter.output

    def get_interpreter_error(self, code):
        """Espera un error semántico (break fuera de bucle)."""
        parser = Parser()
        tokens = Lexer().tokenize(code)
        ast = parser.parse(tokens)

        interpreter = Interpreter(Context(code), get_output=True)
        try:
            interpreter.interpret(ast)
        except Exception:
            pass
        self.assertTrue(errors_detected(), f"Se esperaba error en: {code}")

    # =========================================================================
    # 1. FOR LOOP (Break standard)
    # =========================================================================

    def test_break_basic(self):
        """Romper el bucle al llegar a 5."""
        code = """
        i: integer;
        for (i = 0; i < 10; i++) {
            if (i == 5) {
                break;
            }
            print i;
        }
        """
        # 0, 1, 2, 3, 4. Al llegar a 5, break antes del print.
        expected = "01234"
        self.assertEqual(self.get_output(code), expected)

    def test_break_at_start(self):
        """Break en la primera instrucción. No imprime nada."""
        code = """
        i: integer;
        for (i = 0; i < 3; i++) {
            break;
            print i;
        }
        """
        expected = ""
        self.assertEqual(self.get_output(code), expected)

    def test_break_in_else(self):
        """
        i=0 (par) -> print 0
        i=1 (impar) -> else -> break
        """
        code = """
        i: integer;
        for (i = 0; i < 5; i++) {
            if (i % 2 == 0) {
                print i;
            } else {
                break;
            }
        }
        """
        expected = "0"
        self.assertEqual(self.get_output(code), expected)

    def test_break_skip_update(self):
        """
        Verifica que break salte inmediatamente, IGNORANDO el update (i++).
        Si break ejecutara el update, 'i' valdría 3 al salir.
        """
        code = """
        i: integer;
        for (i = 0; i < 10; i++) {
            if (i == 2) {
                break;
            }
        }
        print i; 
        """
        # i=0, i=1, i=2 -> entra al if -> break. Valor final de i es 2.
        expected = "2"
        self.assertEqual(self.get_output(code), expected)

    # =========================================================================
    # 2. WHILE & DO-WHILE
    # =========================================================================

    def test_break_while_loop(self):
        code = """
        i: integer = 0;
        while (i < 5) {
            if (i == 3) {
                break;
            }
            print i;
            i = i + 1;
        }
        """
        # 0, 1, 2. Al ser 3, break.
        expected = "012"
        self.assertEqual(self.get_output(code), expected)

    def test_break_do_while_loop(self):
        code = """
        i: integer = 0;
        do {
            if (i == 3) {
                break;
            }
            print i;
            i = i + 1;
        } while (i < 5);
        """
        expected = "012"
        self.assertEqual(self.get_output(code), expected)

    # =========================================================================
    # 3. LOOPS ANIDADOS (NESTED)
    # =========================================================================

    def test_break_nested_inner(self):
        """
        Break solo debe romper el bucle MÁS CERCANO (el interno).
        """
        code = """
        i: integer;
        j: integer;
        for (i = 0; i < 3; i++) {
            for (j = 0; j < 3; j++) {
                if (j == 1) {
                    break; // Rompe loop J
                }
                print i, j;
            }
        }
        """
        # i=0: print 00. j=1 break.
        # i=1: print 10. j=1 break.
        # i=2: print 20. j=1 break.
        expected = "001020"
        self.assertEqual(self.get_output(code), expected)

    def test_break_inner_based_on_outer(self):
        """
        Condición basada en variable externa, pero break está en el interno.
        """
        code = """
        i: integer;
        j: integer;
        for (i = 0; i < 3; i++) {
            for (j = 0; j < 3; j++) {
                if (i == 1) {
                    // Cuando i es 1, rompe el loop J inmediatamente en su primera vuelta (j=0)
                    break; 
                }
                print i, j;
            }
        }
        """
        # i=0: 00, 01, 02
        # i=1: (entra loop J, if true, break J). No imprime nada.
        # i=2: 20, 21, 22
        expected = "000102202122"
        self.assertEqual(self.get_output(code), expected)

    def test_break_nested_multiple_levels(self):
        """
        3 niveles de anidamiento. Break en el nivel 3 vuelve al 2.
        """
        code = """
        i: integer;
        j: integer;
        k: integer;
        for (i = 0; i < 1; i++) {
            for (j = 0; j < 2; j++) {
                print "M", j; // Medio
                for (k = 0; k < 5; k++) {
                    if (k == 1) break; // Rompe K
                    print k;
                }
            }
        }
        """
        # i=0 -> j=0 -> Print M0 -> k=0 (print 0) -> k=1 (break)
        #     -> j=1 -> Print M1 -> k=0 (print 0) -> k=1 (break)
        expected = "M00M10"
        self.assertEqual(self.get_output(code), expected)

    # =========================================================================
    # 4. SINTAXIS Y ERRORES
    # =========================================================================

    def test_break_inline_syntax(self):
        """Probar sintaxis sin llaves."""
        code = """
        i: integer;
        for (i = 0; i < 5; i++)
            if (i == 2) break; else print i;
        """
        # 0, 1 -> break
        expected = "01"
        self.assertEqual(self.get_output(code), expected)

    def test_error_break_outside_loop(self):
        """Break fuera de loop debe ser error semántico."""
        code = """
        if (true) {
            break;
        }
        """
        self.get_interpreter_error(code)
