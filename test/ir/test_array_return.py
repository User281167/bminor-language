import unittest
from parser.model import *

from ir import IRGenerator, run_llvm_clang_ir
from utils import clear_errors, errors_detected


class TestArrayReturn(unittest.TestCase):
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

    # --- Test 1: Retorno Básico de Array Local ---
    def test_return_local_array_integer(self):
        """
        Prueba simple: Una función crea un array local y lo retorna.
        Main captura el puntero e imprime.
        """
        code = """
        get_nums: function array [3] integer () = {
            // Declaración local
            arr: array [3] integer = {10, 20, 30};
            return arr;
        }

        main: function void () = {
            // Capturar el retorno
            res: array [3] integer;
            res = get_nums();

            print res[0], "-", res[1], "-", res[2];
        }
        """
        expected_output = "10-20-30"
        _, output = self.get_ir_and_output(code)
        self.assertEqual(output, expected_output)

    # --- Test 2: Encadenamiento (Chaining) y Modificación ---
    def test_chaining_set_get(self):
        """
        El caso que mencionaste: print(set(get())).
        Prueba que el puntero fluya de una función a otra correctamente.
        """
        code = """
        // 1. Crea y retorna
        get_arr: function array [2] integer () = {
            arr: auto = {1, 2};
            return arr;
        }

        // 2. Recibe, modifica y retorna el MISMO puntero
        set_arr: function array [2] integer (target: array [2] integer) = {
            target[0] = -1;
            return target;
        }

        print_arr: function void(a: array [2] integer) = {
            print a[0], " ", a[1];
        }

        main: function void() = {
            // Flujo: get -> (ptr) -> set -> (ptr) -> print
            print_arr(set_arr(get_arr()));
        }
        """
        expected_output = "-1 2"
        _, output = self.get_ir_and_output(code)
        self.assertEqual(output, expected_output)

    # --- Test 3: Passthrough (Identidad) ---
    def test_passthrough_array(self):
        """
        Prueba una función que simplemente devuelve lo que recibe.
        Verifica que no se pierda la referencia.
        """
        code = """
        identity: function array [1] integer (in: array [1] integer) = {
            return in;
        }

        main: function void () = {
            orig: array [1] integer = {777};

            // Recibimos el mismo puntero de vuelta
            same: array [1] integer;
            same = identity(orig);

            print same[0];
        }
        """
        expected_output = "777"
        _, output = self.get_ir_and_output(code)
        self.assertEqual(output, expected_output)

    # --- Test 4: Retorno de Array de Strings (Gestión de Memoria) ---
    def test_return_string_array(self):
        """
        Prueba crítica: Retornar un array de strings.
        Verifica que los punteros a los strings (char*) dentro del array
        se mantengan válidos al volver al main.
        """
        code = """
        get_messages: function array [2] string () = {
            // Inicialización con literales y concat
            msgs: array [2] string = {"Hello", "World" + "!"};
            return msgs;
        }

        main: function void () = {
            data: array [2] string;
            data =get_messages();

            print data[0], " ", data[1];
        }
        """
        expected_output = "Hello World!"
        _, output = self.get_ir_and_output(code)
        self.assertEqual(output, expected_output)

    # --- Test 5: Retorno con Auto Inference ---
    def test_return_auto_declared(self):
        """
        Prueba retornando una variable declarada con 'auto'.
        """
        code = """
        create_point: function array [2] integer () = {
            // Inferencia de tipo array [2] integer
            p: auto = {100, 200};
            return p;
        }

        main: function void () = {
            pt: array [2] integer;
            pt = create_point();
            print "X:", pt[0], " Y:", pt[1];
        }
        """
        expected_output = "X:100 Y:200"
        _, output = self.get_ir_and_output(code)
        self.assertEqual(output, expected_output)

    # --- Test 6: Retorno de Floats (Nested Calls) ---
    def test_return_float_nested(self):
        """
        Prueba con floats y llamadas anidadas para verificar tipos.
        """
        code = """
        make_floats: function array [2] float () = {
            f: array [2] float = {1.1, 2.2};
            return f;
        }

        sum_floats: function float (arr: array [2] float) = {
            return arr[0] + arr[1];
        }

        main: function void () = {
            // make_floats retorna puntero, sum_floats lo consume
            res: float = sum_floats(make_floats());

            // Asumiendo formato estandar printf %f
            print res;
        }
        """
        # 1.1 + 2.2 = 3.3. Floats en C suelen imprimir 6 decimales.
        expected_output = "3.300000"
        _, output = self.get_ir_and_output(code)
        self.assertEqual(output, expected_output)

    # --- Test 7: Array dentro de expresión de retorno ---
    # def test_return_array_access_direct(self):
    #     """
    #     Acceder directamente al elemento de un array retornado sin guardarlo en variable.
    #     print get()[0];
    #     """
    #     code = """
    #     get_values: function array [3] integer () = {
    #         v: auto = {5, 6, 7};
    #         return v;
    #     }

    #     main: function void () = {
    #         // Acceso directo al retorno
    #         print get_values()[1];
    #     }
    #     """
    #     expected_output = "6"
    #     _, output = self.get_ir_and_output(code)
    #     self.assertEqual(output, expected_output)
