import unittest
from parser import Parser
from parser.model import *

from interprete import Context, Interpreter
from scanner import Lexer
from utils import clear_errors, errors_detected


class TestForLoop(unittest.TestCase):
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
        """Espera un error (semántico o de tipos)."""
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
    # 1. TEST BÁSICOS (Incremento / Decremento)
    # =========================================================================

    def test_countdown_example(self):
        """
        El ejemplo que pusiste en el prompt:
        for (i = 10; i > 0; i--) ...
        """
        code = """
        i: integer = 0;
        for (i = 10; i > 0; i--) {
            print i; 
        }
        """
        # Esperado: 10987654321
        expected = "10987654321"
        self.assertEqual(self.get_output(code), expected)

    def test_basic_increment(self):
        """Equivalente a test_for_loop_basic"""
        code = """
        i: integer;
        for (i = 0; i <= 2; i++) {
            print i;
        }
        """
        expected = "012"
        self.assertEqual(self.get_output(code), expected)

    def test_decrement(self):
        """Equivalente a test_for_loop_decrement"""
        code = """
        i: integer;
        for (i = 2; i >= 0; i--) {
            print i;
        }
        """
        expected = "210"
        self.assertEqual(self.get_output(code), expected)

    # =========================================================================
    # 2. LOGICA INTERNA Y CONDICIONALES
    # =========================================================================

    def test_loop_with_if(self):
        """Equivalente a test_for_loop_with_if"""
        code = """
        i: integer;
        for (i = 0; i <= 2; i++) {
            if (i < 2) {
                print i;
            }
        }
        """
        # 0 < 2 (print), 1 < 2 (print), 2 < 2 (no print)
        expected = "01"
        self.assertEqual(self.get_output(code), expected)

    def test_complex_condition(self):
        """Equivalente a test_for_loop_complex_condition"""
        code = """
        i: integer;
        // Loop mientras i^2 < 50
        // 0, 1, 2, 3, 4, 5, 6, 7 (49<50 ok), 8 (64<50 false)
        for (i = 0; i <= 10; i++) {
            if ((i * i) < 50) {
                print i;
            }
        }
        """
        expected = "01234567"
        self.assertEqual(self.get_output(code), expected)

    # =========================================================================
    # 3. MANEJO DE SCOPE EN EL CUERPO
    # =========================================================================

    def test_scope_inside_loop(self):
        """
        Equivalente a test_for_loop_with_declaration_and_if.
        Verifica que se puedan declarar variables DENTRO del loop.
        """
        code = """
        i: integer;
        for (i = 0; i <= 3; i++) {
            j: integer = i * 2;
            if (j < 5) {
                print j;
            }
        }
        """
        # i=0 -> j=0 (print)
        # i=1 -> j=2 (print)
        # i=2 -> j=4 (print)
        # i=3 -> j=6 (no print)
        expected = "024"
        self.assertEqual(self.get_output(code), expected)

    def test_renew_var_in_scope(self):
        """
        Equivalente a test_for_renew_var.
        Cada iteración debe crear/reiniciar la variable local.
        """
        code = """
        i: integer;
        // x no está declarada afuera
        for (i = 0; i < 3; i++) {
            x: integer = i; // Declaración local válida por iteración
            print x;
        }
        """
        expected = "012"
        self.assertEqual(self.get_output(code), expected)

    # =========================================================================
    # 4. VARIACIONES EN LA SINTAXIS (INIT, NESTED)
    # =========================================================================

    def test_empty_init(self):
        """
        Equivalente a test_for_loop_no_init.
        El intérprete debe manejar `None` o vacío en la parte de inicialización.
        """
        code = """
        i: integer = 0;
        for (; i <= 2; i++) {
            print i;
        }
        """
        expected = "012"
        self.assertEqual(self.get_output(code), expected)

    def test_nested_loops(self):
        """Equivalente a test_for_loop_nested"""
        code = """
        i: integer;
        j: integer;
        for (i = 0; i < 2; i++) {
            for (j = 0; j < 3; j++) {
                print i, j;
            }
        }
        """
        # i=0: 00, 01, 02
        # i=1: 10, 11, 12
        expected = "000102101112"
        self.assertEqual(self.get_output(code), expected)

    def test_nested_with_logic(self):
        """Equivalente a test_for_loop_nested_with_if"""
        code = """
        i: integer;
        j: integer;
        for (i = 0; i < 3; i++) {
            for (j = 0; j < 3; j++) {
                if (i != j) {
                    print i, j;
                }
            }
        }
        """
        # 01, 02
        # 10, 12
        # 20, 21
        expected = "010210122021"
        self.assertEqual(self.get_output(code), expected)

    # =========================================================================
    # 5. VALIDACIONES Y ERRORES
    # =========================================================================

    def test_error_non_bool_condition(self):
        """La condición del for debe ser booleana."""
        code = """
        i: integer;
        // Error: i + 1 retorna integer, no boolean
        for (i = 0; i + 1; i++) {
            print i;
        }
        """
        self.get_interpreter_error(code)

    def test_variable_persistence(self):
        """
        Verifica que la variable de control (si fue declarada afuera)
        mantiene su valor al salir del loop.
        """
        code = """
        i: integer = 0;
        for (i = 0; i < 5; i++) {
            print;
        }
        print i;
        """
        # Al terminar el loop, i se incrementó a 5, falló la condición y salió.
        expected = "5"
        self.assertEqual(self.get_output(code), expected)

    def test_update_cond(self):
        """
        Verifica que la variable de control (si fue declarada afuera)
        mantiene su valor al salir del loop.
        """
        code = """
        x: integer = 10; // Variable externa
        
        for(x=0;x<10;x++) {
            x: integer = 5; // Shadowing interno
            print x;        // Imprime 5 (interna)
            // Al salir del bloque, x interna muere.
        } 
        // La condición evalúa la 'x' externa (10). 
        // 10 == 5 es False. El loop termina.
        // Si evaluara la interna, sería loop infinito.
        """
        # Al terminar el loop, i se incrementó a 5, falló la condición y salió.
        expected = "5555555555"
        self.assertEqual(self.get_output(code), expected)
