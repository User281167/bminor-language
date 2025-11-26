import unittest
from parser import Parser
from parser.model import *

from interprete import Context, Interpreter
from scanner import Lexer
from utils import clear_errors, errors_detected


class TestContinueStmt(unittest.TestCase):
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

    def get_interpreter_error(self, code):
        """Espera un error (ej: continue fuera de bucle)."""
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
    # 1. FOR LOOP (El caso más complejo por el update step)
    # =========================================================================

    def test_continue_basic(self):
        """Saltar una iteración específica."""
        code = """
        i: integer;
        for (i = 0; i < 5; i++) {
            if (i == 2) {
                continue;
            }
            print i;
        }
        """
        # 0, 1, (salta 2), 3, 4
        expected = "0134"
        self.assertEqual(self.get_output(code), expected)

    def test_continue_scope_start(self):
        """Continue al inicio del bloque: no imprime nada."""
        code = """
        i: integer;
        for (i = 0; i < 5; i++) {
            continue;
            print i; # Código muerto
        }
        """
        expected = ""
        self.assertEqual(self.get_output(code), expected)

    def test_continue_at_end(self):
        """Continue al final (redundante pero válido)."""
        code = """
        i: integer;
        for (i = 0; i < 3; i++) {
            print i;
            if (i == 1) {
                continue;
            }
        }
        """
        expected = "012"
        self.assertEqual(self.get_output(code), expected)

    def test_continue_in_else(self):
        """Uso dentro de estructuras if/else."""
        code = """
        i: integer;
        // Imprime solo pares
        for (i = 0; i < 5; i++) {
            if (i % 2 == 0) {
                print i;
            } else {
                continue;
            }
        }
        """
        expected = "024"
        self.assertEqual(self.get_output(code), expected)

    def test_continue_no_body_braces(self):
        """Sintaxis inline."""
        code = """
        i: integer;
        for (i = 0; i < 5; i++)
            if (i == 2) continue; else print i;
        """
        expected = "0134"
        self.assertEqual(self.get_output(code), expected)

    # =========================================================================
    # 2. WHILE & DO-WHILE
    # =========================================================================

    def test_continue_while_loop(self):
        """
        NOTA: En while, el incremento debe estar ANTES del continue
        o se crea un bucle infinito.
        """
        code = """
        i: integer = 0;
        while (i < 5) {
            i = i + 1;
            if (i == 3) {
                continue; // Salta el print
            }
            print i;
        }
        """
        # i=1(print), i=2(print), i=3(continue), i=4(print), i=5(print) -> sal del while
        expected = "1245"
        self.assertEqual(self.get_output(code), expected)

    def test_continue_do_while_loop(self):
        code = """
        i: integer = 0;
        do {
            i = i + 1;
            if (i == 3) {
                continue;
            }
            print i;
        } while (i < 5);
        """
        expected = "1245"
        self.assertEqual(self.get_output(code), expected)

    # =========================================================================
    # 3. ANIDAMIENTO (NESTED LOOPS)
    # =========================================================================

    def test_continue_nested_inner(self):
        """Continue afecta solo al bucle más interno."""
        code = """
        i: integer;
        j: integer;
        for (i = 0; i < 3; i++) {
            for (j = 0; j < 3; j++) {
                if (j == 1) {
                    continue; // Salta j=1
                }
                print i, j;
            }
        }
        """
        # i=0: 00, 02
        # i=1: 10, 12
        # i=2: 20, 22
        expected = "000210122022"
        self.assertEqual(self.get_output(code), expected)

    def test_continue_nested_logic_outer(self):
        """
        Lógica condicional basada en variable externa,
        pero el continue se ejecuta en el interno.
        """
        code = """
        i: integer;
        j: integer;
        for (i = 0; i < 3; i++) {
            for (j = 0; j < 3; j++) {
                if (i == 1) {
                    continue; 
                    // Esto salta la iteración actual de J.
                    // Como i es constante para todo el ciclo J,
                    // efectivamente salta TODAS las impresiones cuando i=1.
                }
                print i, j;
            }
        }
        """
        # i=0: 00, 01, 02
        # i=1: (nada se imprime porque en cada j entra al continue)
        # i=2: 20, 21, 22
        expected = "000102202122"
        self.assertEqual(self.get_output(code), expected)

    # =========================================================================
    # 4. CASOS CRÍTICOS Y ERRORES
    # =========================================================================

    def test_for_loop_continue_update(self):
        """
        CRÍTICO: Verificar que 'continue' NO salte la actualización (i++).
        Si el intérprete está mal hecho, esto será un bucle infinito o 'i' no cambiará.
        """
        code = """
        i: integer;
        // Si el continue saltara el i++, i siempre sería 0 -> bucle infinito.
        for (i = 0; i < 5; i++) {
            continue; 
        }
        print i; // Debe imprimir 5 (valor final al salir)
        """
        expected = "5"
        self.assertEqual(self.get_output(code), expected)

    def test_error_continue_outside_loop(self):
        """Continue fuera de un bucle es un error semántico."""
        code = """
        print "Hola";
        continue;
        """
        self.get_interpreter_error(code)
