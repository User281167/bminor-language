import unittest
from parser import Parser
from parser.model import *

from interprete import Context, Interpreter
from scanner import Lexer
from utils import clear_errors, errors_detected


class TestInterpreterChainedAssignment(unittest.TestCase):
    def setUp(self):
        clear_errors()

    def get_output(self, code):
        """Ejecuta el código y devuelve la salida concatenada."""
        parser = Parser()
        tokens = Lexer().tokenize(code)
        ast = parser.parse(tokens)

        # Interpreter global (sin main)
        interpreter = Interpreter(Context(code), get_output=True)
        interpreter.interpret(ast)

        if errors_detected():
            self.fail(f"Errores detectados en el intérprete:\n{code}")

        return interpreter.output

    # =========================================================================
    # TESTS DE ASIGNACIÓN ENCADENADA
    # =========================================================================

    def test_integer_chain(self):
        """
        Prueba básica: a = b = 10.
        Verifica asociatividad por derecha.
        """
        code = """
        a: integer = 1;
        b: integer;

        // b toma 10, y el resultado (10) se asigna a a
        a = b = 10;

        print a, " ", b;
        """
        expected = "10 10"
        self.assertEqual(self.get_output(code), expected)

    def test_array_left_chain(self):
        """
        Prueba: res[0] = a = 10.
        El valor fluye hacia la izquierda dentro del array.
        """
        code = """
        res: array [1] integer = {1};
        a: integer = 1;

        // a = 10 devuelve 10, que se asigna a res[0]
        res[0] = a = 10;

        print a, " ", res[0];
        """
        expected = "10 10"
        self.assertEqual(self.get_output(code), expected)

    def test_array_middle_chain(self):
        """
        Prueba: a = res[0] = 10.
        El valor se asigna al array, y el array devuelve el valor para asignarlo a la variable.
        Esta prueba es crítica para verificar que 'visit_ArrayAssign' devuelve valor.
        """
        code = """
        res: array [1] integer = {1};
        a: integer = 1;

        // res[0] = 10 devuelve 10, que se asigna a 'a'
        a = res[0] = 10;

        print a, " ", res[0];
        """
        expected = "10 10"
        self.assertEqual(self.get_output(code), expected)

    def test_array_mixed_complex_chain(self):
        """
        Prueba solicitada explícitamente: b = a[0] = 2.
        """
        code = """
        b: integer = 0;
        a: array [1] integer = {99};

        // a[0] se hace 2, y devuelve 2, que se asigna a b
        b = a[0] = 2;

        print b, " ", a[0];
        """
        expected = "2 2"
        self.assertEqual(self.get_output(code), expected)

    def test_string_chain_independence(self):
        """
        Prueba de memoria/referencia con Strings.
        a = b = "Hello". Si cambio b, a NO debe cambiar.
        En Python (intérprete) esto es comportamiento por defecto (inmutabilidad),
        pero es bueno testearlo para asegurar que no estemos compartiendo punteros mutables incorrectamente.
        """
        code = """
        a: string = "";
        b: string = "";

        a = b = "Hello";
        print a, b, " ";

        // Modificar b
        b = "World";

        // a debe seguir siendo Hello
        print a, b;
        """
        # HelloHello HelloWorld
        expected = "HelloHello HelloWorld"
        self.assertEqual(self.get_output(code), expected)

    def test_array_string_chain(self):
        """
        Encadenamiento con Arrays de Strings.
        res[0] = a = "10".
        """
        code = """
        res: array [1] string = {"1"};
        a: string;

        res[0] = a = "10";
        print a, " ", res[0], " ";

        // Cambio variable local, array no cambia
        a = "99";
        print a, " ", res[0];
        """
        expected = "10 10 99 10"
        self.assertEqual(self.get_output(code), expected)

    def test_long_chain_expression(self):
        """
        Cadena larga con expresión matemática: x = y = z = 5 + 5.
        """
        code = """
        x: integer;
        y: integer;
        z: integer;

        x = y = z = 5 + 5;

        print x, y, z;
        """
        expected = "101010"
        self.assertEqual(self.get_output(code), expected)

    def test_chain_calculated_index(self):
        """
        Verifica el orden de evaluación.
        arr[idx] = val = 5
        Primero se resuelve val=5, y luego se asigna a arr[idx].
        """
        code = """
        arr: array [2] integer = {0, 0};
        idx: integer = 0;
        val: integer;

        arr[idx] = val = 5;
        arr[idx + 1] = val = 6;

        print arr[0], arr[1], val;
        """
        expected = "566"
        self.assertEqual(self.get_output(code), expected)

    def test_nested_array_assignment_chain(self):
        """
        Prueba avanzada: Usar un array para indexar otro en una cadena.
        data[ indices[0] ] = x = 7
        """
        code = """
        indices: array [1] integer = {0};
        data: array [1] integer = {100};
        x: integer;

        // indices[0] es 0 -> data[0] = x = 7
        data[ indices[0] ] = x = 7;

        print data[0], x;
        """
        expected = "77"
        self.assertEqual(self.get_output(code), expected)
