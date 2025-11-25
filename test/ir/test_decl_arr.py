import unittest
from parser.model import *

from ir import IRGenerator, run_llvm_clang_ir
from utils import clear_errors, errors_detected


class TestArrayTypesAndAuto(unittest.TestCase):
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

    # --- Test 1: Array de Enteros ---
    def test_integer_array(self):
        """
        Prueba declaración explícita de enteros y recorrido con for.
        """
        code = """
        arr: array [5] integer = {1, 2, 3, 4, 5};

        main: function void () = {
            i: integer;
            // Recorrido e impresión
            for(i=0; i<5; i++) {
                print arr[i];
                if (i < 4) print ",";
            }
        }
        """
        expected_output = "1,2,3,4,5"
        _, output = self.get_ir_and_output(code)
        self.assertEqual(output, expected_output)

    # --- Test 2: Array de Floats ---
    def test_float_array(self):
        """
        Prueba declaración de floats.
        Nota: El output de float depende de tu runtime print_float (usualmente %f o %g).
        Asumiremos un formato estándar con decimales, o simplificado.
        """
        code = """
        // Inicialización mixta integer/float si tu parser lo soporta, o float puro
        arr: array [3] float = {1.1, 2.2, 3.3};

        main: function void () = {
            i: integer;
            for(i=0; i<3; i++) {
                print arr[i], " ";
            }
        }
        """
        # Ajusta este expected_output según cómo imprima tu runtime de C (6 decimales es default en printf %f)
        # Si usas %g podría ser "1.1 2.2 3.3"
        expected_output = "1.100000 2.200000 3.300000"

        _, output = self.get_ir_and_output(code)
        self.assertEqual(output, expected_output)

    # --- Test 3: Array de Caracteres (Char) ---
    def test_char_array(self):
        """
        Prueba declaración de caracteres.
        """
        code = """
        arr: array [4] char = {'L', 'L', 'V', 'M'};

        main: function void () = {
            i: integer;
            for(i=0; i<4; i++) {
                print arr[i];
            }
        }
        """
        expected_output = "LLVM"
        _, output = self.get_ir_and_output(code)
        self.assertEqual(output, expected_output)

    # --- Test 4: Array de Booleanos ---
    def test_boolean_array(self):
        """
        Prueba declaración de booleanos.
        Verifica si se imprimen como true/false o 1/0 según tu runtime.
        """
        code = """
        arr: array [3] boolean = {true, false, true};

        main: function void () = {
            i: integer;
            for(i=0; i<3; i++) {
                print arr[i], "-";
            }
        }
        """
        # Asumiendo que tu print_bool imprime "true" o "false"
        expected_output = "true-false-true-"
        _, output = self.get_ir_and_output(code)
        self.assertEqual(output, expected_output)

    # --- Test 5: Array de Strings ---
    def test_string_array(self):
        """
        Prueba declaración explícita de strings (gestión de memoria).
        """
        code = """
        arr: array [3] string = {"Code", "Gen", "Rocks"};

        main: function void () = {
            i: integer;
            res: string = "";

            for(i=0; i<3; i++) {
                res = res + arr[i] + " ";
            }
            print res;
        }
        """
        expected_output = "Code Gen Rocks"
        _, output = self.get_ir_and_output(code)
        # Normalizar espacios
        self.assertEqual(output.strip(), expected_output.strip())

    # --- Test 6: Inferencia de Tipos (AUTO) con Enteros ---
    def test_auto_array_integer(self):
        """
        Prueba 'arr: auto = {...}' infiriendo tipo INTEGER.
        El compilador debe deducir el tipo y el tamaño (si implementaste deducción de tamaño)
        o al menos el tipo base.
        """
        code = """
        // El tipo debe inferirse como array [4] integer
        arr: auto = {10, 20, 30, 40};

        main: function void () = {
            i: integer;
            sum: integer = 0;

            for(i=0; i<4; i++) {
                sum = sum + arr[i];
            }
            print sum;
        }
        """
        expected_output = "100"
        _, output = self.get_ir_and_output(code)
        self.assertEqual(output, expected_output)

    # --- Test 7: Inferencia de Tipos (AUTO) con Strings ---
    def test_auto_array_string(self):
        """
        Prueba 'arr: auto = {...}' infiriendo tipo STRING.
        """
        code = """
        // El tipo debe inferirse como array [2] string
        arr: auto = {"Auto", "Matic"};

        main: function void () = {
            print arr[0], arr[1];
        }
        """
        expected_output = "AutoMatic"
        _, output = self.get_ir_and_output(code)
        self.assertEqual(output, expected_output)

    # --- Test 8: Array Local con Auto (Stack) ---
    def test_local_const_array(self):
        """
        Prueba la inferencia 'constant' dentro de una función (Stack Allocation).
        """
        code = """
        main: function void () = {
            // Local constant array
            vals: constant = {5, 5, 5};

            i: integer;
            total: integer = 0;

            for(i=0; i<3; i++) {
                total = total + vals[i];
            }
            print total;
        }
        """
        expected_output = "15"
        _, output = self.get_ir_and_output(code)
        self.assertEqual(output, expected_output)
