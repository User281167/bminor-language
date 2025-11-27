import unittest
from parser import Parser
from parser.model import *

from interprete import Context, Interpreter
from scanner import Lexer
from utils import clear_errors, errors_detected


class TestInterpreterArrayUse(unittest.TestCase):
    def setUp(self):
        clear_errors()

    def get_output(self, code):
        """Ejecuta el código y devuelve la salida concatenada."""
        parser = Parser()
        tokens = Lexer().tokenize(code)
        ast = parser.parse(tokens)

        interpreter = Interpreter(Context(code), get_output=True)
        interpreter.interpret(ast)

        if errors_detected():
            self.fail(f"Errores detectados en el intérprete:\n{code}")

        return interpreter.output

    # =========================================================================
    # TESTS DE USO DE ARRAYS
    # =========================================================================

    def test_global_array_init_and_access(self):
        """
        Prueba inicialización y expresiones en la declaración (concatenación).
        """
        code = """
        nums: array [3] integer = {10, 20, 30};

        // El intérprete debe resolver "World" + "!" al evaluar la lista
        strs: array [2] string = {"Hello", "World" + "!"};

        print nums[0], "-", nums[2];
        print strs[0], " ", strs[1];
        """
        expected = "10-30Hello World!"
        self.assertEqual(self.get_output(code), expected)

    def test_array_mutation(self):
        """
        Prueba lectura y escritura (mutabilidad).
        """
        code = """
        vals: array [2] integer = {1, 1};
        names: array [2] string = {"Old", "Name"};

        // Modificar enteros
        vals[0] = 50;
        vals[1] = vals[0] + 50; // 100

        // Modificar strings
        names[0] = "New";
        names[1] = names[0] + " Value";

        print vals[0], " ", vals[1], " ";
        print names[0], " ", names[1];
        """
        expected = "50 100 New New Value"
        self.assertEqual(self.get_output(code), expected)

    def test_copy_semantics_on_assignment(self):
        """
        Prueba CRÍTICA: Semántica de valor.
        Al asignar `item = inventory[0]`, se debe copiar el valor.
        Modificar `item` NO debe alterar el array.
        """
        code = """
        inventory: array [1] string = {"Sword"};

        // 1. Copia de valor
        item: string = inventory[0];

        print inventory[0], item;

        // 2. Modificar variable local
        item = "Shield";

        // 3. El array debe seguir intacto
        print inventory[0], item;
        """
        expected = "SwordSwordSwordShield"
        self.assertEqual(self.get_output(code), expected)

    def test_copy_semantics_on_param(self):
        """
        Prueba: Pasar un elemento de array a una función.
        La función recibe una copia, el array original no cambia.
        """
        code = """
        data: array [1] string = {"Original"};

        modify_val: function void (s: string) = {
            s = "Modified";
            print "Inside:", s, " ";
        }

        modify_val(data[0]);
        print "Outside:", data[0];
        """
        expected = "Inside:Modified Outside:Original"
        self.assertEqual(self.get_output(code), expected)

    def test_loop_iteration_dynamic_index(self):
        """
        Iteración usando variable 'i' como índice.
        Prueba que el visitor evalúe la expresión dentro de [ ].
        """
        code = """
        nums: array [4] integer = {10, 20, 30, 40};
        i: integer = 0;
        sum: integer = 0;

        for(i=0; i<4; i++) {
            sum = sum + nums[i];
        }

        print sum;

        words: array [3] string = {"A", "B", "C"};
        for(i=0; i<3; i++) {
            print words[i];
        }
        """
        expected = "100ABC"
        self.assertEqual(self.get_output(code), expected)

    def test_local_array_init_complex(self):
        """
        Inicialización de array local con expresiones complejas (llamadas a función).
        """
        code = """
        get_suffix: function string() = { return "Func"; }

        main_test: function void () = {
            // El array se crea en el stack de la función
            // Evalua: Literal, Concatenación, Llamada
            local_arr: array [3] string = {"Lit", "A"+"B", get_suffix()};

            print local_arr[0], local_arr[1], local_arr[2];
        }

        main_test();
        """
        expected = "LitABFunc"
        self.assertEqual(self.get_output(code), expected)

    def test_calculated_indexes(self):
        """
        Índices matemáticos: arr[base + 2].
        """
        code = """
        arr: array [5] integer = {0, 10, 20, 30, 40};
        base: integer = 1;

        // arr[1 + 2] -> arr[3] -> 30
        print arr[base + 2];

        // arr[1 - 1] -> arr[0] -> 0
        print arr[base - 1];
        """
        expected = "300"
        self.assertEqual(self.get_output(code), expected)

    def test_array_index_evaluation_order(self):
        """
        Prueba de orden de evaluación (para intérpretes robustos).
        Verifica que el índice se calcula antes de acceder.
        """
        code = """
        arr: array [2] integer = {88, 99};

        get_idx: function integer() = {
            print "CalcularIndex ";
            return 1;
        }

        // Debería imprimir "CalcularIndex" antes de imprimir "99"
        print arr[get_idx()];
        """
        expected = "CalcularIndex 99"
        self.assertEqual(self.get_output(code), expected)
