import unittest
from parser import Parser
from parser.model import *

from interprete import Context, Interpreter
from scanner import Lexer
from utils import clear_errors, errors_detected


class TestWhileLoop(unittest.TestCase):
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
    # 1. TEST BÁSICOS
    # =========================================================================

    def test_while_loop_basic(self):
        """Bucle simple de 0 a 2."""
        code = """
        i: integer = 0;
        while (i < 3) {
            print i;
            i = i + 1;
        }
        """
        expected = "012"
        self.assertEqual(self.get_output(code), expected)

    def test_while_loop_no_entry(self):
        """Verifica que si la condición inicia en falso, no entra."""
        code = """
        i: integer = 10;
        while (i < 5) {
            print i;
        }
        print "Fin";
        """
        expected = "Fin"
        self.assertEqual(self.get_output(code), expected)

    # =========================================================================
    # 2. LÓGICA INTERNA Y CONDICIONES
    # =========================================================================

    def test_while_loop_with_if(self):
        """While con IF anidado."""
        code = """
        i: integer = 0;
        while (i < 3) {
            if (i < 2) {
                print i;
            }
            i = i + 1;
        }
        """
        expected = "01"
        self.assertEqual(self.get_output(code), expected)

    def test_while_loop_complex_condition(self):
        """Expresión matemática en la condición."""
        code = """
        i: integer = 0;
        // 0^2=0, 1^2=1, 2^2=4, 3^2=9 (todos < 10).
        // 4^2=16 (falso).
        while ((i * i) < 10) {
            print i;
            i = i + 1;
        }
        """
        expected = "0123"
        self.assertEqual(self.get_output(code), expected)

    # =========================================================================
    # 3. SCOPE Y DECLARACIONES
    # =========================================================================

    def test_while_loop_with_declaration(self):
        """Declarar variables dentro del bucle (Scope local)."""
        code = """
        i: integer = 0;
        while (i < 3) {
            x: integer = i * 2;
            print x;
            i = i + 1;
        }
        """
        expected = "024"
        self.assertEqual(self.get_output(code), expected)

    def test_while_scope_isolation(self):
        """
        Verifica que la variable declarada adentro muere al terminar la iteración.
        (O al menos no es accesible desde afuera).
        """
        code = """
        i: integer = 0;
        while (i < 1) {
            temp: integer = 99;
            i = i + 1;
        }
        // Error: temp no existe aquí
        print temp;
        """
        self.get_interpreter_error(code)

    # =========================================================================
    # 4. BUCLES ANIDADOS
    # =========================================================================

    def test_while_loop_nested(self):
        """While dentro de While."""
        code = """
        i: integer = 0;
        while (i < 2) {
            j: integer = 0;
            while (j < 3) {
                print i, j;
                j = j + 1;
            }
            i = i + 1;
        }
        """
        # i=0: 00 01 02
        # i=1: 10 11 12
        expected = "000102101112"
        self.assertEqual(self.get_output(code), expected)

    # =========================================================================
    # 5. SINTAXIS SIN LLAVES (BODY SIMPLE)
    # =========================================================================

    def test_while_loop_no_body_braces(self):
        """
        Prueba 'while (cond) stmt;' sin bloque {}.
        El intérprete debe ejecutar la sentencia única repetidamente.
        """
        code = """
        i: integer = 0;
        while (i < 3) i = i + 1;
        print i;
        """
        expected = "3"
        self.assertEqual(self.get_output(code), expected)

    # =========================================================================
    # 6. VALIDACIONES Y ERRORES
    # =========================================================================

    def test_error_non_bool_condition(self):
        """La condición debe evaluar a booleano."""
        code = """
        while (1 + 1) {
            print "Error";
        }
        """
        self.get_interpreter_error(code)

    def test_error_assignment_in_condition(self):
        """
        Evitar asignaciones accidentales en lugar de comparaciones.
        Ej: while (i = 0) ... debe ser error si '=' retorna integer.
        """
        code = """
        i: integer = 0;
        while (i = 1) {
            print "Infinito?";
        }
        """
        self.get_interpreter_error(code)

    def test_env_while(self):
        """
        Evitar asignaciones accidentales en lugar de comparaciones.
        Ej: while (i = 0) ... debe ser error si '=' retorna integer.
        """
        code = """
        x: integer = 1; // Variable externa
        
        while(x++ < 10) {
            x: integer = 5; // Shadowing interno
            print x;        // Imprime 5 (interna)
            // Al salir del bloque, x interna muere.
        } 
        // La condición evalúa la 'x' externa (10). 
        // 10 == 5 es False. El loop termina.
        // Si evaluara la interna, sería loop infinito.
        
        print "Fin";
        """
        expected = "555555555Fin"
        self.assertEqual(self.get_output(code), expected)
