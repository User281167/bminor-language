import unittest
from parser import Parser
from parser.model import *

from interprete import Context, Interpreter
from scanner import Lexer
from utils import clear_errors, errors_detected


class TestDoWhileLoop(unittest.TestCase):
    def setUp(self):
        clear_errors()

    def get_output(self, code):
        """Ejecuta código y retorna la salida."""
        parser = Parser()
        tokens = Lexer().tokenize(code)
        ast = parser.parse(tokens)

        interpreter = Interpreter(Context(code), get_output=True)
        interpreter.interpret(ast)
        return interpreter.output

    def get_interpreter_error(self, code):
        """Ejecuta código esperando un error."""
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
    # 1. COMPORTAMIENTO BÁSICO
    # =========================================================================

    def test_do_while_basic(self):
        """Prueba estándar: 0, 1, 2."""
        code = """
        i: integer = 0;
        do {
            print i;
            i = i + 1;
        } while (i < 3);
        """
        expected = "012"
        self.assertEqual(self.get_output(code), expected)

    def test_do_while_runs_once(self):
        """
        DIFERENCIA CLAVE CON WHILE:
        La condición es falsa desde el inicio, pero el cuerpo debe ejecutarse una vez.
        """
        code = """
        i: integer = 10;
        do {
            print i; // Se imprime 10
            i = i + 1;
        } while (i < 5); // 11 < 5 es falso, termina.
        """
        expected = "10"
        self.assertEqual(self.get_output(code), expected)

    def test_do_while_no_body_braces(self):
        """Sintaxis sin llaves: do stmt; while(cond);"""
        code = """
        i: integer = 0;
        do i = i + 1; while (i < 3);
        print i;
        """
        expected = "3"
        self.assertEqual(self.get_output(code), expected)

    # =========================================================================
    # 2. LOGICA Y ANIDAMIENTO
    # =========================================================================

    def test_do_while_with_if(self):
        code = """
        i: integer = 0;
        do {
            if (i < 2) {
                print i;
            }
            i = i + 1;
        } while (i < 3);
        """
        expected = "01"
        self.assertEqual(self.get_output(code), expected)

    def test_nested_do_while(self):
        code = """
        i: integer = 0;
        do {
            j: integer = 0;
            do {
                print i, j;
                j = j + 1;
            } while (j < 3);
            i = i + 1;
        } while (i < 2);
        """
        # i=0: 00 01 02
        # i=1: 10 11 12
        expected = "000102101112"
        self.assertEqual(self.get_output(code), expected)

    def test_complex_condition(self):
        code = """
        i: integer = 0;
        do {
            print i;
            i = i + 1;
        } while ((i * i) < 10);
        """
        expected = "0123"
        self.assertEqual(self.get_output(code), expected)

    # =========================================================================
    # 3. SCOPE (Explorando problemas de variables)
    # =========================================================================

    def test_scope_declaration_inside(self):
        """Declarar variables dentro del loop."""
        code = """
        i: integer = 0;
        do {
            val: integer = i * 10;
            print val;
            i = i + 1;
        } while (i < 3);
        """
        expected = "01020"
        self.assertEqual(self.get_output(code), expected)

    def test_error_variable_in_condition_scope(self):
        """
        TEST CRÍTICO:
        ¿Puede la condición 'while' ver una variable declarada DENTRO del 'do'?

        En la mayoría de lenguajes (C, Java) esto es ERROR, porque el scope del bloque
        cierra antes de evaluar la condición.

        do {
           x: int = 1;
        } while (x == 1); <--- x no debería existir aquí
        """
        code = """
        do {
            internal: integer = 5;
        } while (internal == 5);
        """
        # Si tu lenguaje permite esto, cambia el test.
        # Pero lo estándar es que sea error.
        self.get_interpreter_error(code)

    def test_shadowing_and_condition(self):
        """
        Verifica qué variable lee la condición si hay shadowing.
        """
        code = """
        x: integer = 10; // Variable externa
        
        do {
            x: integer = 5; // Shadowing interno
            print x;        // Imprime 5 (interna)
            // Al salir del bloque, x interna muere.
        } while (x == 5); 
        
        // La condición evalúa la 'x' externa (10). 
        // 10 == 5 es False. El loop termina.
        // Si evaluara la interna, sería loop infinito.
        
        print "Fin";
        """
        expected = "5Fin"
        self.assertEqual(self.get_output(code), expected)

    # =========================================================================
    # 4. TIPOS
    # =========================================================================

    def test_error_non_bool_condition(self):
        code = """
        do {
            print "loop";
        } while (100); // 100 no es bool
        """
        self.get_interpreter_error(code)
