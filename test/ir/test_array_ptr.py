import unittest
from parser.model import *

from ir import IRGenerator, run_llvm_clang_ir
from utils import clear_errors, errors_detected


class TestArrayParamsAndRef(unittest.TestCase):
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

    # --- Test 1: Enteros Básicos (Referencia Simple) ---
    def test_integer_reference(self):
        """
        Prueba básica: Cambiar un entero dentro de la función afecta al original.
        """
        code = """
        set_neg: function void(arr: array [] integer) = {
            arr[0] = -1;
            arr[1] = -2;
        }

        main: function void() = {
            // Declaración explícita
            nums: array [2] integer = {10, 20};
            
            set_neg(nums);
            
            print nums[0], " ", nums[1];
        }
        """
        expected_output = "-1 -2"
        _, output = self.get_ir_and_output(code)
        self.assertEqual(output, expected_output)

    # --- Test 2: Strings por Referencia (Gestión de Memoria) ---
    def test_string_reference_mutation(self):
        """
        Prueba CRÍTICA: Modificar un array de strings en una función.
        El runtime debe liberar el string viejo y asignar el nuevo correctamente
        en la memoria del array original.
        """
        code = """
        greet: function void(words: array [] string) = {
            // Esto libera el valor viejo y asigna uno nuevo en el Heap
            words[0] = "Hello";
            words[1] = words[1] + " World";
        }

        main: function void() = {
            // Declaración con 'auto'
            data: auto = {"Hi", "BMinor"};
            
            greet(data);
            
            print data[0], " ", data[1];
        }
        """
        expected_output = "Hello BMinor World"
        _, output = self.get_ir_and_output(code)
        self.assertEqual(output, expected_output)

    # --- Test 3: Booleanos (Lógica Inversa) ---
    def test_boolean_toggle(self):
        """
        Prueba lógica booleana modificando el array in-place.
        """
        code = """
        toggle: function void(bits: array [] boolean) = {
            // Asumiendo un array de tamaño 2
            // Invertimos valores manualmente
            if (bits[0]) bits[0] = false; else bits[0] = true;
            bits[1] = true;
        }

        main: function void() = {
            flags: array [2] boolean = {true, false};
            
            toggle(flags);
            
            print flags[0], " ", flags[1];
        }
        """
        expected_output = "false true"
        _, output = self.get_ir_and_output(code)
        self.assertEqual(output, expected_output)

    # --- Test 4: Floats (Cálculo Matemático) ---
    def test_float_scaling(self):
        """
        Prueba modificación de floats (escalado).
        """
        code = """
        scale: function void(vals: array [] float) = {
            // Duplicar el primer valor
            vals[0] = 1.5;
            vals[1] = 2.5;
        }

        main: function void() = {
            f: array [2] float = {0.0, 0.0};
            scale(f);
            // Print estándar de float suele ser con decimales
            print f[0], " ", f[1];
        }
        """
        expected_output = "1.500000 2.500000"
        _, output = self.get_ir_and_output(code)
        self.assertEqual(output, expected_output)

    # --- Test 5: Char (Encriptación simple) ---
    def test_char_substitution(self):
        """
        Prueba modificación de caracteres individuales en un array.
        """
        code = """
        to_upper: function void(chars: array [] char) = {
            // Cambiar minúsculas a mayúsculas manualmente
            chars[0] = 'A';
            chars[2] = 'C';
        }

        main: function void() = {
            letters: array [3] char = {'a', 'b', 'c'};
            
            to_upper(letters);
            
            print letters[0], letters[1], letters[2];
        }
        """
        expected_output = "AbC"
        _, output = self.get_ir_and_output(code)
        self.assertEqual(output, expected_output)

    # --- Test 6: Declaración 'const' con Elementos Mutables ---
    def test_const_array_mutable_elements(self):
        """
        Verifica la regla: "array = array no, pero array[N] = val, si".
        Un array declarado 'const' pasa su puntero, y la función
        puede modificar el contenido de la memoria a la que apunta.
        """
        code = """
        reset: function void(arr: array [] integer) = {
            arr[0] = 0;
            arr[1] = 0;
        }

        main: function void() = {
            // Array constante (el puntero es constante, los datos no necesariamente)
            fixed: constant = {99, 88};

            reset(fixed);

            print fixed[0], "-", fixed[1];
        }
        """
        expected_output = "0-0"
        _, output = self.get_ir_and_output(code)
        self.assertEqual(output, expected_output)

    # --- Test 7: Swap (Intercambio de valores) ---
    def test_array_swap(self):
        """
        Prueba algorítmica: Intercambiar dos elementos del mismo array.
        Requiere leer temp, escribir A, escribir B.
        """
        code = """
        swap: function void(arr: array [] integer) = {
            temp: integer = arr[0];
            arr[0] = arr[1];
            arr[1] = temp;
        }

        main: function void() = {
            pair: auto = {10, 20};
            swap(pair);
            print pair[0], " ", pair[1];
        }
        """
        expected_output = "20 10"
        _, output = self.get_ir_and_output(code)
        self.assertEqual(output, expected_output)

    # --- Test 8: Llamadas en Cadena (Nested Ref Passing) ---
    def test_chained_calls(self):
        """
        Main -> FuncA -> FuncB.
        El array debe pasar por referencia a través de múltiples stack frames.
        """
        code = """
        step2: function void(a: array [] integer) = {
            a[0] = a[0] + 1; // 1 + 1 = 2
        }

        step1: function void(a: array [] integer) = {
            a[0] = 1;
            step2(a); // Pasa la referencia a la siguiente
        }

        main: function void() = {
            x: array [1] integer = {0};
            step1(x);
            print x[0];
        }
        """
        expected_output = "2"
        _, output = self.get_ir_and_output(code)
        self.assertEqual(output, expected_output)

    # --- Test 9: Array como acumulador "Out Parameter" ---
    def test_out_parameter(self):
        """
        Usar un array para retornar múltiples valores (simulado).
        """
        code = """
        calc_stats: function void(results: array [] integer) = {
            // results[0] será suma, results[1] será resta
            results[0] = 10 + 5;
            results[1] = 10 - 5;
        }

        main: function void() = {
            // Inicializar vacío/ceros
            res: array [2] integer = {0, 0};
            
            calc_stats(res);
            
            print "Sum:", res[0], " Diff:", res[1];
        }
        """
        expected_output = "Sum:15 Diff:5"
        _, output = self.get_ir_and_output(code)
        self.assertEqual(output, expected_output)

    # --- Test 10: Recorrido y Modificación con Bucle ---
    def test_loop_modification(self):
        """
        Modifica todos los elementos de un array usando un bucle dentro de la función.
        Prueba la aritmética de punteros en el lado izquierdo de la asignación.
        """
        code = """
        fill_ones: function void(arr: array [] integer) = {
            i: integer;
            // Llena los primeros 3
            for(i=0; i<3; i++) {
                arr[i] = 1;
            }
        }

        main: function void() = {
            grid: array [3] integer = {0, 0, 0};
            
            fill_ones(grid);
            
            print grid[0], grid[1], grid[2];
        }
        """
        expected_output = "111"
        _, output = self.get_ir_and_output(code)
        self.assertEqual(output, expected_output)
