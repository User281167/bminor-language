import unittest
from parser import Parser
from parser.model import *

from interprete import Context, Interpreter
from scanner import Lexer
from utils import clear_errors, errors_detected


class TestInterpreterAutoAndConstant(unittest.TestCase):
    def setUp(self):
        clear_errors()

    def get_output(self, code):
        """Ejecuta código esperando éxito y retorna la salida."""
        parser = Parser()
        tokens = Lexer().tokenize(code)
        ast = parser.parse(tokens)

        # Interpreter en modo script global
        interpreter = Interpreter(Context(code), get_output=True)
        interpreter.interpret(ast)

        if errors_detected():
            self.fail(f"Errores detectados en el intérprete:\n{code}")

        return interpreter.output

    def get_interpreter_error(self, code):
        """
        Ejecuta código esperando un ERROR (semántico o de ejecución).
        Útil para probar que 'constant' no deja reasignar.
        """
        parser = Parser()
        tokens = Lexer().tokenize(code)
        ast = parser.parse(tokens)

        interpreter = Interpreter(Context(code), get_output=True)
        try:
            interpreter.interpret(ast)
        except Exception:
            return  # Éxito: El intérprete lanzó excepción

        # Si no hubo excepción, debe haber flag de error activado
        self.assertTrue(errors_detected(), f"Se esperaba un error en:\n{code}")

    # =========================================================================
    # 1. TESTS DE 'AUTO' (Inferencia y Mutabilidad)
    # =========================================================================

    def test_auto_scalar_inference_and_mutation(self):
        """
        Prueba que 'auto' infiere tipos básicos y permite cambios.
        """
        code = """
        x: auto = 10;      // Infiere integer
        y: auto = 3.14;    // Infiere float
        z: auto = true;    // Infiere boolean
        
        print x, y, z;
        
        // Mutación permitida en 'auto'
        x = 20;
        z = false;
        
        print x, z;
        """
        # Ajusta el formato de float/bool según tu intérprete
        expected = "103.14true20false"
        self.assertEqual(self.get_output(code), expected)

    def test_auto_array_inference(self):
        """
        Prueba que 'auto' infiere arrays basándose en la lista {...}.
        """
        code = """
        // Debe inferir: array [3] integer
        arr: auto = {10, 20, 30};
        
        i: integer = 0;
        sum: integer = 0;
        
        for (i=0; i<3; i++) {
            sum = sum + arr[i];
        }
        print sum;
        """
        expected = "60"
        self.assertEqual(self.get_output(code), expected)

    def test_auto_array_mutation(self):
        """
        Prueba CRÍTICA: Un array declarado con 'auto' DEBE ser mutable.
        """
        code = """
        // Array mutable
        vec: auto = {1, 1, 1};
        
        // Modificamos sus elementos
        vec[0] = 5;
        vec[1] = 5;
        vec[2] = vec[0] + vec[1]; // 10
        
        print vec[2];
        """
        expected = "10"
        self.assertEqual(self.get_output(code), expected)

    # =========================================================================
    # 2. TESTS DE 'CONSTANT' (Inferencia e Inmutabilidad)
    # =========================================================================

    def test_constant_scalar_read(self):
        """
        Prueba que 'constant' se puede leer y operar correctamente.
        """
        code = """
        PI: constant = 3.1415;
        R: auto = 2.0;
        
        // Area = PI * R * R
        area: auto = PI * R * R;
        
        print PI;
        """
        expected = "3.1415"
        self.assertEqual(self.get_output(code), expected)

    def test_constant_scalar_write_error(self):
        """
        Prueba que intentar reasignar una variable 'constant' da error.
        """
        code = """
        MAX_VAL: constant = 100;
        print MAX_VAL;
        
        // ESTO DEBE FALLAR
        MAX_VAL = 200; 
        """
        self.get_interpreter_error(code)

    def test_constant_array_read(self):
        """
        Prueba lectura de arrays constantes.
        """
        code = """
        // Array constante (lookup table)
        DIGITS: constant = {0, 1, 2, 3, 4};
        
        print DIGITS[4];
        """
        expected = "4"
        self.assertEqual(self.get_output(code), expected)

    def test_constant_array_reassignment_error(self):
        """
        Prueba: Intentar reasignar toda la variable array constante.
        """
        code = """
        CONFIG: constant = {1, 0};

        // ESTO DEBE FALLAR: Reasignar la variable entera
        // Asumiendo que tu lenguaje soporta asignación de arrays, si no, fallará igual.
        CONFIG = {2, 2};
        """
        self.get_interpreter_error(code)

    # =========================================================================
    # 3. TESTS MIXTOS Y DE EXPRESIONES
    # =========================================================================

    def test_auto_from_expression(self):
        """
        'auto' inicializado desde una expresión compleja.
        """
        code = """
        a: integer = 5;
        b: integer = 5;
        
        // c se infiere integer (10)
        c: auto = a + b; 
        
        print c;
        """
        expected = "10"
        self.assertEqual(self.get_output(code), expected)

    def test_constant_from_expression(self):
        """
        'constant' inicializado desde expresión (debe calcularse al momento de declaración).
        """
        code = """
        // VAL se calcula una vez y se congela
        VAL: constant = 10 * 10; 
        print VAL;
        """
        expected = "100"
        self.assertEqual(self.get_output(code), expected)

    def test_type_mismatch_auto_init(self):
        """
        Verifica que la inferencia de array sea consistente.
        No puedes tener un array auto con tipos mezclados (si tu lenguaje es estático).
        """
        code = """
        // Error: Mezcla de integer y string en inicializador
        arr: auto = {1, "texto"}; 
        """
        self.get_interpreter_error(code)
