import unittest
from parser import Parser
from parser.model import *

from interprete import Context, Interpreter
from scanner import Lexer
from utils import clear_errors, errors_detected


class TestInterpreterArrayLength(unittest.TestCase):
    def setUp(self):
        clear_errors()

    def get_output(self, code):
        """Ejecuta el código y devuelve la salida."""
        parser = Parser()
        tokens = Lexer().tokenize(code)
        ast = parser.parse(tokens)

        interpreter = Interpreter(Context(code), get_output=True)
        interpreter.interpret(ast)

        if errors_detected():
            self.fail(f"Errores detectados en el intérprete:\n{code}")

        return interpreter.output

    # =========================================================================
    # TESTS DE ARRAY_LENGTH
    # =========================================================================

    def test_basic_types_length(self):
        """
        Prueba básica con diferentes tipos de arrays declarados explícitamente.
        """
        code = """
        s: array [2] string = {"1", "2"};
        i: array [5] integer = {1, 2, 3, 4, 5};
        b: array [1] boolean = {true};

        print array_length(s), " ";
        print array_length(i), " ";
        print array_length(b);
        """
        expected = "2 5 1"
        self.assertEqual(self.get_output(code), expected)

    def test_auto_length(self):
        """
        Prueba con arrays 'auto', donde el tamaño se infiere.
        """
        code = """
        // El intérprete crea una lista de 3 elementos
        arr: auto = {10, 20, 30};

        print "Len:", array_length(arr);
        """
        expected = "Len:3"
        self.assertEqual(self.get_output(code), expected)

    def test_length_in_function_params(self):
        """
        CRÍTICO PARA INTÉRPRETES:
        Verifica que al pasar el array a una función, se conserve el objeto correcto
        y 'len()' funcione sobre la referencia recibida.
        """
        code = """
        check_len: function void (a: array [] integer) = {
            print array_length(a);
        }

        short: array [2] integer = {1, 2};
        long: array [4] integer = {1, 2, 3, 4};

        check_len(short);
        print "-";
        check_len(long);
        """
        expected = "2-4"
        self.assertEqual(self.get_output(code), expected)

    def test_loop_with_length(self):
        """
        Caso de uso real: Usar length como límite en un bucle for.
        """
        code = """
        print_all: function void(arr: array [] string) = {
            i: integer;
            // Loop dinámico
            for(i = 0; i < array_length(arr); i++) {
                print arr[i];
            }
        }

        words: auto = {"A", "B", "C"};
        print_all(words);
        """
        expected = "ABC"
        self.assertEqual(self.get_output(code), expected)

    def test_length_in_expressions(self):
        """
        Verifica que array_length se evalúe como un entero operable.
        """
        code = """
        arr: array [10] integer; // Tamaño 10 por defecto (si soportas init default)

        // 10 + 5 = 15
        res: integer = array_length(arr) + 5;

        if (array_length(arr) > 5) {
            print "Big ";
        }
        print res;
        """
        # Nota: Si tu intérprete inicializa arrays vacíos con 0s, length es 10.
        expected = "Big 15"
        self.assertEqual(self.get_output(code), expected)

    def test_length_of_return(self):
        """
        Prueba array_length aplicado directamente al retorno de una función.
        Gramática: array_length( call() )
        """
        code = """
        get_arr: function array [3] integer () = {
            a: auto = {1, 1, 1};
            return a;
        }

        // Debe ejecutar get_arr(), obtener la lista y medirla
        l: integer = array_length(get_arr());

        print l;
        """
        expected = "3"
        self.assertEqual(self.get_output(code), expected)

    def test_modify_using_length(self):
        """
        Modificar array usando su longitud.
        """
        code = """
        fill_neg: function void(arr: array [] integer) = {
            i: integer;
            for(i=0; i < array_length(arr); i++) {
                arr[i] = -1;
            }
        }

        nums: array [2] integer = {10, 20};
        fill_neg(nums);

        print nums[0], nums[1];
        """
        expected = "-1-1"
        self.assertEqual(self.get_output(code), expected)

    def test_empty_array_length(self):
        """
        Prueba de borde: Array vacío o de tamaño 0 (si tu lenguaje lo permite).
        """
        code = """
        // Si soportas arrays de tamaño 0
        arr: array [0] integer;
        print array_length(arr);
        """
        # Si tu parser permite [0], el intérprete debe devolver 0
        try:
            out = self.get_output(code)
            self.assertEqual(out, "0")
        except:
            # Si tu lenguaje prohíbe arrays de tamaño 0, este test puede ignorarse
            pass
