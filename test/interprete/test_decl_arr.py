import unittest
from parser import Parser
from parser.model import *

from interprete import Context, Interpreter
from scanner import Lexer
from utils import clear_errors, errors_detected


class TestInterpreterArrays(unittest.TestCase):
    def setUp(self):
        clear_errors()

    def get_output(self, code):
        """Ejecuta el código y devuelve la salida capturada."""
        parser = Parser()
        tokens = Lexer().tokenize(code)
        ast = parser.parse(tokens)

        # Interpreter ejecutando en contexto global
        interpreter = Interpreter(Context(code), get_output=True)
        interpreter.interpret(ast)

        if errors_detected():
            self.fail(f"Se detectaron errores en el intérprete para el código:\n{code}")

        return interpreter.output

    def get_interpreter_error(self, code):
        """Espera que el intérprete lance excepción o marque error interno."""
        parser = Parser()
        tokens = Lexer().tokenize(code)
        ast = parser.parse(tokens)

        interpreter = Interpreter(Context(code), get_output=True)
        try:
            interpreter.interpret(ast)
        except Exception:
            return  # Éxito: El intérprete explotó controladamente (Python Exception)

        # Si no explotó, verificamos flags de error
        self.assertTrue(errors_detected(), f"Se esperaba error en: {code}")

    # =========================================================================
    # TESTS DE ARRAYS (Top-Level Script Style)
    # =========================================================================

    def test_integer_array(self):
        """Declaración y recorrido de array de enteros."""
        code = """
        arr: array [5] integer = {1, 2, 3, 4, 5};
        i: integer = 0;

        for(i=0; i<5; i++) {
            print arr[i];
            if (i < 4) print ",";
        }
        """
        expected = "1,2,3,4,5"
        self.assertEqual(self.get_output(code), expected)

    def test_float_array(self):
        """Declaración de floats."""
        code = """
        arr: array [3] float = {1.1, 2.2, 3.3};
        i: integer = 0;

        for(i=0; i<3; i++) {
            print arr[i], " ";
        }
        """
        # Python print standard (sin ceros extra)
        expected = "1.1 2.2 3.3 "
        self.assertEqual(self.get_output(code), expected)

    def test_char_array(self):
        """Declaración de caracteres."""
        code = """
        arr: array [4] char = {'H', 'o', 'l', 'a'};
        i: integer = 0;

        for(i=0; i<4; i++) {
            print arr[i];
        }
        """
        expected = "Hola"
        self.assertEqual(self.get_output(code), expected)

    def test_boolean_array(self):
        """Declaración de booleanos."""
        code = """
        arr: array [3] boolean = {true, false, true};
        i: integer = 0;

        for(i=0; i<3; i++) {
            print arr[i], "-";
        }
        """
        # Ajusta "true"/"True" según cómo tu intérprete convierta bool a string
        expected = "true-false-true-"
        self.assertEqual(self.get_output(code), expected)

    def test_string_array(self):
        """Array de strings y concatenación."""
        code = """
        names: array [3] string = {"Ana", "Bob", "Dan"};
        res: string = "";
        i: integer = 0;

        for(i=0; i<3; i++) {
            res = res + names[i] + " ";
        }
        print res;
        """
        expected = "Ana Bob Dan "
        self.assertEqual(self.get_output(code), expected)

    # =========================================================================
    # INFERENCIA (AUTO)
    # =========================================================================

    def test_auto_array_integer(self):
        """Inferencia de tipo integer."""
        code = """
        vals: auto = {10, 20, 30};
        sum: integer = 0;
        i: integer = 0;

        for(i=0; i<3; i++) {
            sum = sum + vals[i];
        }
        print sum;
        """
        expected = "60"
        self.assertEqual(self.get_output(code), expected)

    def test_auto_array_string(self):
        """Inferencia de tipo string."""
        code = """
        msgs: auto = {"Hello", "World"};
        print msgs[0], msgs[1];
        """
        expected = "HelloWorld"
        self.assertEqual(self.get_output(code), expected)

    def test_constant_array(self):
        """
        Uso de 'constant' (inmutable).
        Si tu intérprete soporta constantes, intentar cambiar esto debería dar error,
        pero aquí probamos solo lectura exitosa.
        """
        code = """
        fixed: constant = {5, 5};
        total: integer = 0;

        total = fixed[0] + fixed[1];
        print total;
        """
        expected = "10"
        self.assertEqual(self.get_output(code), expected)

    # =========================================================================
    # ROBUSTEZ Y ERRORES
    # =========================================================================

    def test_array_mutability(self):
        """
        Verifica que podemos cambiar valores en índices específicos
        y que el cambio persiste en memoria.
        """
        code = """
        nums: array [3] integer = {0, 0, 0};

        nums[0] = 50;
        nums[1] = 50;

        // Suma basada en los nuevos valores
        nums[2] = nums[0] + nums[1];

        print nums[2];
        """
        expected = "100"
        self.assertEqual(self.get_output(code), expected)

    def test_array_index_out_of_bounds_positive(self):
        """Acceso fuera de rango (índice muy alto)."""
        code = """
        arr: array [2] integer = {10, 20};
        print arr[5];
        """
        self.get_interpreter_error(code)

    def test_array_index_out_of_bounds_negative(self):
        """
        Acceso fuera de rango (índice negativo).
        (Salvo que soportes índices negativos estilo Python intencionalmente).
        """
        code = """
        arr: array [2] integer = {10, 20};
        print arr[-1];
        """
        self.get_interpreter_error(code)

    def test_type_mismatch_assignment(self):
        """Intentar guardar un tipo incorrecto en el array."""
        code = """
        arr: array [2] integer = {1, 2};
        arr[0] = "No soy un numero";
        """
        self.get_interpreter_error(code)

    def test_nested_array_access(self):
        """
        Prueba avanzada: Usar un valor de array como índice de otro.
        arr1[ arr2[0] ]
        """
        code = """
        indices: array [2] integer = {1, 0};
        data: array [2] string = {"Pos0", "Pos1"};

        // indices[0] es 1 -> data[1] es "Pos1"
        print data[ indices[0] ];
        """
        expected = "Pos1"
        self.assertEqual(self.get_output(code), expected)
