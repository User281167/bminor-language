import unittest
from parser.model import *

from ir import IRGenerator, run_llvm_clang_ir
from utils import clear_errors, errors_detected


class TestChainedAssignment(unittest.TestCase):
    def setUp(self):
        clear_errors()

    def get_ir_and_output(self, code):
        """Helper para generar IR y ejecutar."""
        ir_generator = IRGenerator()
        generated_ir = ir_generator.generate_from_code(code)

        self.assertFalse(
            errors_detected(),
            "Errores semánticos detectados durante la generación de IR",
        )

        output = ""
        try:
            output = run_llvm_clang_ir(str(generated_ir), add_runtime=True)
            output = output.strip()
        except Exception as e:
            print(f"Error al ejecutar LLVM/Clang IR: {e}")
            print("--- LLVM IR Generado ---")
            print(str(generated_ir))
            print("------------------------")
            self.fail(f"La ejecución del IR falló: {e}")

        return generated_ir, output

    # --- Test 1: Enteros Básicos (a = b = 10) ---
    def test_integer_chain(self):
        """
        Prueba la asignación encadenada simple con enteros.
        """
        code = """
        main: function void () = {
            a: integer = 1;
            b: integer;

            // Ambos deben terminar siendo 10
            a = b = 10;
            
            print a, " ", b;
        }
        """
        expected_output = "10 10"
        _, output = self.get_ir_and_output(code)
        self.assertEqual(output, expected_output)

    # --- Test 2: Array a la Izquierda (res[0] = a = 10) ---
    def test_array_left_chain(self):
        """
        Prueba: res[0] = a = 10.
        El valor 10 se asigna a 'a', y el resultado (10) se asigna a 'res[0]'.
        """
        code = """
        main: function void () = {
            res: array [1] integer = {1};
            a: integer = 1;

            res[0] = a = 10;

            print a, " ", res[0];
        }
        """
        expected_output = "10 10"
        _, output = self.get_ir_and_output(code)
        self.assertEqual(output, expected_output)

    # --- Test 3: Array en el Medio (a = res[0] = 10) ---
    def test_array_middle_chain(self):
        """
        Prueba: a = res[0] = 10.
        El valor 10 se asigna a 'res[0]', y el resultado se asigna a 'a'.
        """
        code = """
        main: function void () = {
            res: array [1] integer = {1};
            a: integer = 1;

            a = res[0] = 10;

            print a, " ", res[0];
        }
        """
        expected_output = "10 10"
        _, output = self.get_ir_and_output(code)
        self.assertEqual(output, expected_output)

    # --- Test 4: Strings Encadenados (Independencia de Memoria) ---
    def test_string_chain_independence(self):
        """
        Prueba CRÍTICA: a = b = "Hello".
        Verifica que ambos sean "Hello", PERO que sean copias distintas.
        Si modificamos 'b' después, 'a' NO debe cambiar.
        """
        code = """
        main: function void () = {
            a: string = "";
            b: string = "";

            // Asignación encadenada
            a = b = "Hello";
            
            print "Before: ", a, " ", b, "\\n";

            // Modificar 'b'
            b = "World";

            // 'a' debe seguir siendo "Hello"
            print "After: ", a, " ", b;
        }
        """
        # Nota: Python requiere escapar el \n en el string esperado
        expected_output = "Before: Hello Hello\nAfter: Hello World"
        _, output = self.get_ir_and_output(code)
        self.assertEqual(output.replace("\r\n", "\n"), expected_output)

    # --- Test 5: Array y Strings (res[0] = a = "Val") ---
    def test_array_string_chain(self):
        """
        Combina arrays y strings.
        res[0] = a = "10".
        Verifica valores y unicidad.
        """
        code = """
        main: function void () = {
            res: array [1] string = {"1"};
            a: string;

            // Cadena de asignación
            res[0] = a = "10";
            
            print a, " ", res[0], "\\n";

            // Modificar 'a' para probar independencia del array
            a = "99";
            
            print a, " ", res[0];
        }
        """
        expected_output = "10 10\n99 10"
        _, output = self.get_ir_and_output(code)
        self.assertEqual(output.replace("\r\n", "\n"), expected_output)

    # --- Test 6: Cadena Larga y Expresiones ---
    def test_long_chain_expression(self):
        """
        Prueba una cadena más larga y con expresiones matemáticas.
        x = y = z = 5 + 5
        """
        code = """
        main: function void () = {
            x: integer;
            y: integer;
            z: integer;

            x = y = z = 5 + 5;

            print x, y, z;
        }
        """
        expected_output = "101010"
        _, output = self.get_ir_and_output(code)
        self.assertEqual(output, expected_output)

    # --- Test 7: Cadena con Índices Calculados ---
    def test_chain_calculated_index(self):
        """
        Prueba que los efectos secundarios o cálculos de índices funcionen.
        arr[0] = val = 5
        """
        code = """
        main: function void () = {
            arr: array [2] integer = {0, 0};
            idx: integer = 0;
            val: integer;

            // arr[0] = val = 5
            arr[idx] = val = 5;

            // arr[1] = val = 6
            arr[idx + 1] = val = 6;

            print arr[0], arr[1], val;
        }
        """
        expected_output = "566"
        _, output = self.get_ir_and_output(code)
        self.assertEqual(output, expected_output)
