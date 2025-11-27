import unittest
from parser import Parser
from parser.model import *

from interprete import Context, Interpreter
from scanner import Lexer
from utils import clear_errors, errors_detected


class TestInterpreterArrayParams(unittest.TestCase):
    def setUp(self):
        clear_errors()

    def get_output(self, code):
        """Ejecuta el código y devuelve la salida."""
        parser = Parser()
        tokens = Lexer().tokenize(code)
        ast = parser.parse(tokens)

        # Interpreter ejecutando el AST completo
        interpreter = Interpreter(Context(code), get_output=True)
        interpreter.interpret(ast)

        if errors_detected():
            self.fail(f"Errores detectados en el intérprete:\n{code}")

        return interpreter.output

    # =========================================================================
    # TESTS DE ARRAYS COMO PARÁMETROS (REFERENCIA)
    # =========================================================================

    def test_integer_reference(self):
        """
        Verifica que modificar el array dentro de la función afecta al original.
        """
        code = """
        set_neg: function void(arr: array [] integer) = {
            arr[0] = -1;
            arr[1] = -2;
        }

        // Main logic
        nums: array [2] integer = {10, 20};
        set_neg(nums);

        print nums[0], " ", nums[1];
        """
        expected = "-1 -2"
        self.assertEqual(self.get_output(code), expected)

    def test_string_reference_mutation(self):
        """
        Verifica mutación de arrays de strings.
        """
        code = """
        greet: function void(words: array [] string) = {
            words[0] = "Hello";
            words[1] = words[1] + " World";
        }

        data: auto = {"Hi", "BMinor"};
        greet(data);

        print data[0], " ", data[1];
        """
        expected = "Hello BMinor World"
        self.assertEqual(self.get_output(code), expected)

    def test_boolean_toggle(self):
        """
        Verifica lógica booleana modificando in-place.
        """
        code = """
        toggle: function void(bits: array [] boolean) = {
            if (bits[0]) bits[0] = false; else bits[0] = true;
            bits[1] = true;
        }

        flags: array [2] boolean = {true, false};
        toggle(flags);

        print flags[0], " ", flags[1];
        """
        # Ajusta true/false según tu print
        expected = "false true"
        self.assertEqual(self.get_output(code), expected)

    def test_float_scaling(self):
        """
        Verifica modificación de floats.
        Nota: Python imprime 1.5, C printf suele imprimir 1.500000.
        """
        code = """
        scale: function void(vals: array [] float) = {
            vals[0] = 1.5;
            vals[1] = 2.5;
        }

        f: array [2] float = {0.0, 0.0};
        scale(f);

        print f[0], " ", f[1];
        """
        expected = "1.5 2.5"
        self.assertEqual(self.get_output(code), expected)

    def test_char_substitution(self):
        """
        Verifica sustitución de caracteres.
        """
        code = """
        to_upper: function void(chars: array [] char) = {
            chars[0] = 'A';
            chars[2] = 'C';
        }

        letters: array [3] char = {'a', 'b', 'c'};
        to_upper(letters);

        print letters[0], letters[1], letters[2];
        """
        expected = "AbC"
        self.assertEqual(self.get_output(code), expected)

    def test_const_array_mutable_elements(self):
        """
        Si 'constant' se refiere a la referencia del array (no reasignable)
        pero permite modificar sus elementos, este test debe pasar.
        """
        code = """
        reset: function void(arr: array [] integer) = {
            arr[0] = 0;
            arr[1] = 0;
        }

        // Declarado constante
        fixed: constant = {99, 88};

        // La función modifica el contenido, no la variable 'fixed' en sí
        reset(fixed);

        print fixed[0], "-", fixed[1];
        """
        expected = "0-0"
        self.assertEqual(self.get_output(code), expected)

    def test_array_swap(self):
        """
        Algoritmo Swap clásico.
        """
        code = """
        swap: function void(arr: array [] integer) = {
            temp: integer = arr[0];
            arr[0] = arr[1];
            arr[1] = temp;
        }

        pair: auto = {10, 20};
        swap(pair);
        print pair[0], " ", pair[1];
        """
        expected = "20 10"
        self.assertEqual(self.get_output(code), expected)

    def test_chained_calls(self):
        """
        Paso de referencia a través de múltiples niveles de función.
        Main -> step1 -> step2
        """
        code = """
        step2: function void(a: array [] integer) = {
            a[0] = a[0] + 1;
        }

        step1: function void(a: array [] integer) = {
            a[0] = 1;
            step2(a); // Pasa la referencia recibida
        }

        x: array [1] integer = {0};
        step1(x);
        print x[0];
        """
        expected = "2"
        self.assertEqual(self.get_output(code), expected)

    def test_out_parameter(self):
        """
        Simulación de retorno múltiple usando array como buffer de salida.
        """
        code = """
        calc_stats: function void(results: array [] integer) = {
            results[0] = 10 + 5;
            results[1] = 10 - 5;
        }

        res: array [2] integer = {0, 0};
        calc_stats(res);

        print "Sum:", res[0], " Diff:", res[1];
        """
        expected = "Sum:15 Diff:5"
        self.assertEqual(self.get_output(code), expected)

    def test_loop_modification(self):
        """
        Modificación masiva con bucle for dentro de función.
        """
        code = """
        fill_ones: function void(arr: array [] integer) = {
            i: integer;
            for(i=0; i<3; i++) {
                arr[i] = 1;
            }
        }

        grid: array [3] integer = {0, 0, 0};
        fill_ones(grid);

        print grid[0], grid[1], grid[2];
        """
        expected = "111"
        self.assertEqual(self.get_output(code), expected)
