import unittest
from parser.model import *

from ir import IRGenerator, run_llvm_clang_ir
from utils import clear_errors, errors_detected


class TestArrayLength(unittest.TestCase):
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

    # --- Test 1: Tipos Básicos y Declaración Explícita ---
    def test_basic_types_length(self):
        """
        Prueba array_length en arrays declarados con tamaño explícito
        de diferentes tipos (string, integer, boolean).
        """
        code = """
        main: function void () = {
            s: array [2] string = {"1", "2"};
            i: array [5] integer = {1, 2, 3, 4, 5};
            b: array [1] boolean = {true};

            print array_length(s), " ";
            print array_length(i), " ";
            print array_length(b);
        }
        """
        expected_output = "2 5 1"
        _, output = self.get_ir_and_output(code)
        self.assertEqual(output, expected_output)

    # --- Test 2: Inferencia con Auto ---
    def test_auto_length(self):
        """
        Prueba que array_length funcione correctamente con arrays 'auto',
        donde el tamaño se deduce de la lista de inicialización.
        """
        code = """
        main: function void () = {
            // El compilador deduce tamaño 3
            arr: auto = {10, 20, 30};

            print "Len:", array_length(arr);
        }
        """
        expected_output = "Len:3"
        _, output = self.get_ir_and_output(code)
        self.assertEqual(output, expected_output)

    # --- Test 3: Paso por Referencia (Parámetros) ---
    def test_length_in_function_params(self):
        """
        CRÍTICO: Verifica si el array pasado como parámetro (array [] type)
        conserva su información de longitud dentro de la función.
        Esto valida si estás pasando un struct {size, ptr} o pasando el tamaño oculto.
        """
        code = """
        check_len: function void (a: array [] integer) = {
            print array_length(a);
        }

        main: function void () = {
            short: array [2] integer = {1, 2};
            long: array [4] integer = {1, 2, 3, 4};

            check_len(short);
            print "-";
            check_len(long);
        }
        """
        expected_output = "2-4"
        _, output = self.get_ir_and_output(code)
        self.assertEqual(output, expected_output)

    # --- Test 4: Uso en Bucles (El caso de uso real) ---
    def test_loop_with_length(self):
        """
        Prueba la función print_array genérica usando array_length
        como condición de parada del for.
        """
        code = """
        print_all: function void(arr: array [] string) = {
            i: integer;
            // El límite es dinámico basado en el array recibido
            for(i = 0; i < array_length(arr); i++) {
                print arr[i];
            }
        }

        main: function void () = {
            words: auto = {"A", "B", "C"};
            print_all(words);
        }
        """
        expected_output = "ABC"
        _, output = self.get_ir_and_output(code)
        self.assertEqual(output, expected_output)

    # --- Test 5: Expresiones Matemáticas ---
    def test_length_in_expressions(self):
        """
        Verifica que array_length devuelva un entero usable en operaciones.
        """
        code = """
        main: function void () = {
            arr: array [10] integer; // Sin init, debe tener tamaño 10

            // Calculo: 10 + 5 = 15
            res: integer = array_length(arr) + 5;

            // Condicional
            if (array_length(arr) > 5) {
                print "Big ";
            }

            print res;
        }
        """
        expected_output = "Big 15"
        _, output = self.get_ir_and_output(code)
        self.assertEqual(output, expected_output)

    # --- Test 6: Arrays Anidados / Multidimensionales (Si aplica) ---
    # Nota: Si tu array es array de arrays, array_length debería dar el tamaño externo.
    def test_nested_array_length(self):
        """
        Si soportas arrays multidimensionales, array_length debe devolver
        el tamaño de la dimensión más externa.
        """
        code = """
        // Matriz 2x3 (array de 2 arrays de 3 enteros)
        // Nota: La sintaxis depende de tu parser, asumo arrays planos o sintaxis estándar
        // Si no soportas multi-dimensión real, este test es sobre arrays de arrays

        // Simulación simple si no hay sintaxis multi-dim explicita:
        // array[2] array[3] integer... (omitido si es complejo de declarar)

        main: function void () = {
            // Test simple de consistencia
            a: array [5] integer;
            b: array [5] string;

            sum: integer = array_length(a) + array_length(b);
            print sum;
        }
        """
        expected_output = "10"
        _, output = self.get_ir_and_output(code)
        self.assertEqual(output, expected_output)

    # --- Test 7: Retorno de Función y Length ---
    def test_length_of_return(self):
        """
        Prueba array_length(func()).
        """
        code = """
        get_arr: function array [3] integer () = {
            a: auto = {1, 1, 1};
            return a;
        }

        main: function void () = {
            // array_length aplicado directamente al retorno
            l: integer = array_length(get_arr());
            print l;
        }
        """
        expected_output = "3"
        _, output = self.get_ir_and_output(code)
        self.assertEqual(output, expected_output)

    # --- Test 8: Modificar array dentro de función usando length ---
    def test_modify_using_length(self):
        """
        Usa length para recorrer y modificar un array pasado por referencia.
        """
        code = """
        fill_neg: function void(arr: array [] integer) = {
            i: integer;
            for(i=0; i < array_length(arr); i++) {
                arr[i] = -1;
            }
        }

        main: function void () = {
            nums: array [2] integer = {10, 20};
            fill_neg(nums);
            print nums[0], nums[1];
        }
        """
        expected_output = "-1-1"
        _, output = self.get_ir_and_output(code)
        self.assertEqual(output, expected_output)
