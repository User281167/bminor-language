import unittest
from parser.model import *

from ir import IRGenerator, run_llvm_clang_ir
from utils import clear_errors, errors_detected


class TestArrayUse(unittest.TestCase):
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

    # --- Test 1: Inicialización Global y Acceso Básico ---
    def test_global_array_init_and_access(self):
        """
        Prueba que los arrays globales se inicialicen correctamente,
        incluyendo expresiones constantes en la inicialización (concat).
        """
        code = """
        // Array de enteros
        nums: array [3] integer = {10, 20, 30};

        // Array de strings con concatenación estática
        strs: array [2] string = {"Hello", "World" + "!"};

        main: function void () = {
            print nums[0], "-", nums[2], "\\n";
            print strs[0], " ", strs[1];
        }
        """
        expected_output = "10-30\nHello World!"
        _, output = self.get_ir_and_output(code)
        self.assertEqual(output.replace("\r\n", "\n"), expected_output)

    # --- Test 2: Mutación de Arrays (Integer & String) ---
    def test_array_mutation(self):
        """
        Verifica que:
        1. Se pueda escribir en una posición del array (arr[i] = ...).
        2. El cambio persista.
        3. Para strings, verifique implícitamente que no explote (gestión de memoria básica).
        """
        code = """
        vals: array [2] integer = {1, 1};
        names: array [2] string = {"Old", "Name"};

        main: function void () = {
            // Modificar enteros
            vals[0] = 50;
            vals[1] = vals[0] + 50;

            // Modificar strings (Debe liberar "Old" y asignar "New")
            names[0] = "New";
            names[1] = names[0] + " Value";

            print vals[0], " ", vals[1], "\\n";
            print names[0], " ", names[1];
        }
        """
        expected_output = "50 100\nNew New Value"
        _, output = self.get_ir_and_output(code)
        self.assertEqual(output.replace("\r\n", "\n"), expected_output)

    # --- Test 3: Semántica de Copia (Assignment) ---
    def test_copy_semantics_on_assignment(self):
        """
        Prueba CRÍTICA basada en tu descripción:
        'item: string = str[0]' crea una copia.
        Modificar 'item' NO debe afectar al array original.
        """
        code = """
        inventory: array [1] string = {"Sword"};

        main: function void () = {
            // 1. Extraer valor (debe ser una copia)
            item: string = inventory[0];

            print "Before: ", inventory[0], " - ", item, "\\n";

            // 2. Modificar la variable local
            item = "Shield";

            // 3. Verificar que el array SIGUE siendo "Sword"
            print "After: ", inventory[0], " - ", item;
        }
        """
        expected_output = "Before: Sword - Sword\nAfter: Sword - Shield"
        _, output = self.get_ir_and_output(code)
        self.assertEqual(output.replace("\r\n", "\n"), expected_output)

    # --- Test 4: Semántica de Copia (Parámetros) ---
    def test_copy_semantics_on_param(self):
        """
        Verifica que pasar un elemento de array (arr[i]) a una función
        pasa una copia del valor (o referencia a copia), de modo que
        la función no modifique el array original.
        """
        code = """
        data: array [1] string = {"Original"};

        modify_val: function void (s: string) = {
            s = "Modified";
            print "Inside: ", s, "\\n";
        }

        main: function void () = {
            // Pasamos data[0]. El compilador debe crear un temporal/copia.
            modify_val(data[0]);

            // El array debe permanecer intacto
            print "Outside: ", data[0];
        }
        """
        expected_output = "Inside: Modified\nOutside: Original"
        _, output = self.get_ir_and_output(code)
        self.assertEqual(output.replace("\r\n", "\n"), expected_output)

    # --- Test 5: Iteración con Bucles (Indices Dinámicos) ---
    def test_loop_iteration_dynamic_index(self):
        """
        Verifica el acceso a arrays usando variables como índices (no constantes),
        lo cual prueba la generación correcta de instrucciones GEP (GetElementPtr).
        """
        code = """
        nums: array [4] integer = {10, 20, 30, 40};

        main: function void () = {
            i: integer;
            sum: integer = 0;

            // Recorrer y sumar
            for(i=0; i<4; i++) {
                sum = sum + nums[i];
            }

            print "Sum: ", sum, "\\n";

            // Recorrer e imprimir strings
            words: array [3] string = {"A", "B", "C"};
            for(i=0; i<3; i++) {
                print words[i];
            }
        }
        """
        expected_output = "Sum: 100\nABC"
        _, output = self.get_ir_and_output(code)
        self.assertEqual(output.replace("\r\n", "\n"), expected_output)

    # --- Test 6: Inicialización Local Compleja ---
    def test_local_array_init(self):
        """
        Prueba la inicialización de arrays dentro de funciones (Stack allocation),
        asegurando que se copien los valores correctamente.
        """
        code = """
        get_word: function string() = { return "Func"; }

        main: function void () = {
            // Inicialización mixta: literal, concat, llamada a función
            local_arr: array [3] string = {"Lit", "A"+"B", get_word()};

            print local_arr[0], local_arr[1], local_arr[2];
        }
        """
        expected_output = "LitABFunc"
        _, output = self.get_ir_and_output(code)
        self.assertEqual(output, expected_output)

    # --- Test 7: Índices calculados (Expresiones) ---
    def test_calculated_indexes(self):
        """
        Verifica que el índice pueda ser una expresión matemática compleja.
        """
        code = """
        arr: array [5] integer = {0, 10, 20, 30, 40};

        main: function void () = {
            base: integer = 1;

            // Acceso: arr[1 + 2] -> arr[3] -> 30
            print arr[base + 2];

            // Acceso: arr[0]
            print arr[base - 1];
        }
        """
        expected_output = "300"
        _, output = self.get_ir_and_output(code)
        self.assertEqual(output, expected_output)
