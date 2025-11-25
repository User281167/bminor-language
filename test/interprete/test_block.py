import unittest
from parser import Parser
from parser.model import *

from interprete import Context, Interpreter
from scanner import Lexer
from utils import clear_errors, errors_detected


class TestBlock(unittest.TestCase):
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
        """Ejecuta el código esperando un error."""
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
    # 1. MUTACIÓN (Modificar variable del padre)
    # =========================================================================
    def test_block_mutation(self):
        """
        Caso: x = 0;
        Al NO declarar el tipo, se busca la variable en el scope superior
        y se modifica. El cambio persiste al salir.
        """
        code = """
        x: integer = 12;
        {
            x = 0; // Asignación a variable existente
        }
        print x;
        """
        expected = "0"
        self.assertEqual(self.get_output(code), expected)

    def test_access_outer_scope(self):
        """Lectura y escritura de variables externas."""
        code = """
        a: integer = 5;
        b: integer = 8;
        {
            print a; // Lee 'a' externa -> 5
            b = 12;  // Modifica 'b' externa
        }
        print b; // -> 12
        """
        expected = "512"
        self.assertEqual(self.get_output(code), expected)

    # =========================================================================
    # 2. SOMBREADO / SHADOWING (Declarar nueva variable)
    # =========================================================================
    def test_block_shadowing(self):
        """
        Caso: x: integer = 0;
        Al declarar el tipo, se crea una NUEVA variable en el scope actual.
        La variable externa queda intacta.
        """
        code = """
        x: integer = 12;
        {
            x: integer = 0; // Nueva variable, tapa a la de afuera
            print x;        // Imprime 0
        }
        print x;            // Imprime 12 (la original)
        """
        expected = "012"
        self.assertEqual(self.get_output(code), expected)

    # =========================================================================
    # 3. BLOQUES ANIDADOS (La "Cebolla")
    # =========================================================================
    def test_nested_blocks_shadowing(self):
        """
        Prueba múltiples niveles.
        Scope Global -> Scope Bloque 1 -> Scope Bloque 2
        """
        code = """
        val: integer = 1;
        print val; // 1
        {
            val: integer = 2; // Shadowing nivel 1
            print val; // 2
            {
                val: integer = 3; // Shadowing nivel 2
                print val; // 3
            }
            print val; // De vuelta al nivel 1 -> 2
        }
        print val; // De vuelta al global -> 1
        """
        expected = "12321"
        self.assertEqual(self.get_output(code), expected)

    # =========================================================================
    # 4. BLOQUES DENTRO DE CONTROL FLOW (IF)
    # =========================================================================
    def test_block_inside_if(self):
        """
        Prueba la interacción entre IF y bloques explícitos.
        (Aunque el IF ya crea un scope, un bloque {} dentro crea otro más si tu parser lo maneja así,
         o simplemente valida que las sentencias funcionen).
        """
        code = """
        x: integer = 100;
        if (true) {
            // Bloque del IF
            y: integer = 25;
            x = x + y; // Modifica externa
            print x;   // 125
        }
        print x; // 125
        """
        expected = "125125"
        self.assertEqual(self.get_output(code), expected)

    def test_explicit_block_inside_if(self):
        """
        Un bloque anónimo DENTRO de un if.
        """
        code = """
        a: integer = 10;
        if (true) {
            // Scope del IF
            a = 20;
            {
                // Scope del bloque interno
                a: integer = 999; 
                print a;
            }
            print a; // Debe ser 20
        }
        """
        expected = "99920"
        self.assertEqual(self.get_output(code), expected)

    # =========================================================================
    # 5. VIDA DE VARIABLES (Scope Isolation)
    # =========================================================================
    def test_variable_lifetime(self):
        """
        Una variable creada dentro de un bloque debe morir al cerrarse la llave.
        """
        code = """
        {
            temp: integer = 50;
        }
        # Aquí 'temp' no debería existir
        print temp;
        """
        self.get_interpreter_error(code)

    def test_block_does_not_leak(self):
        """Verifica que el scope se limpia correctamente (pop del env)."""
        code = """
        x: integer = 1;
        {
            y: integer = 2;
        }
        // Si el scope no se limpió, y podría ser accesible o causar conflictos
        x = 5;
        print x;
        """
        # Si falla (ej: error buscando y), es un error. Si imprime 5, está bien.
        expected = "5"
        self.assertEqual(self.get_output(code), expected)
