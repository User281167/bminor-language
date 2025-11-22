import unittest
from parser.model import *

from ir import IRGenerator, run_llvm_clang_ir
from utils import clear_errors, errors_detected


class TestBlock(unittest.TestCase):
    def setUp(self):
        clear_errors()

    def get_ir(self, code):
        gen = IRGenerator().generate_from_code(code)
        out = ""
        self.assertFalse(
            errors_detected(), "Errores detectados durante la generación de IR"
        )

        try:
            out = run_llvm_clang_ir(str(gen), add_runtime=True)
            out = out.strip()
        except Exception as e:
            print(f"Error al ejecutar LLVM/Clang IR: {e}")
            print("--- LLVM IR ---")
            print(str(gen))
            print("---------------")
            self.fail(f"La ejecución del IR falló: {e}")

        return gen, out

    # --- Test 1: Sombreado de Variables (Variable Shadowing) ---
    def test_variable_shadowing_in_block(self):
        """
        Verifica que una variable declarada dentro de un bloque oculta (sombrea)
        a una variable del mismo nombre en el alcance exterior, y que la variable
        exterior se restaura al salir del bloque.
        """
        code = """
        main: function void() = {
            x: integer = 10;
            print x; // Debe imprimir 10

            {
                x: integer = 99; // Nueva 'x', sombrea a la exterior
                print x; // Debe imprimir 99
            }

            print x; // El bloque terminó, debe imprimir 10 de nuevo
        }
        """
        _, out = self.get_ir(code)
        self.assertEqual(out, "109910")

    # --- Test 2: Acceso a Variables del Alcance Exterior ---
    def test_block_accessing_outer_scope_variable(self):
        """
        Verifica que un bloque puede leer y modificar variables del alcance
        inmediatamente superior si no las sombrea.
        """
        code = """
        main: function void() = {
            a: integer = 5;
            b: integer = 8;
            {
                print a; // Accede a 'a' exterior -> 5
                b = 12;  // Modifica a 'b' exterior
            }
            print b; // Debe imprimir el valor modificado -> 12
        }
        """
        _, out = self.get_ir(code)
        self.assertEqual(out, "512")

    # --- Test 3: Bloques Anidados y Múltiples Niveles de Sombreado ---
    def test_nested_blocks_and_shadowing(self):
        """
        Prueba múltiples niveles de anidamiento y sombreado para asegurar
        que la cadena de 'padres' de Symtab funciona correctamente.
        """
        code = """
        main: function void() = {
            val: integer = 1;
            print val; // -> 1
            {
                val: integer = 2;
                print val; // -> 2
                {
                    val: integer = 3;
                    print val; // -> 3
                }
                print val; // -> 2
            }
            print val; // -> 1
        }
        """
        _, out = self.get_ir(code)
        self.assertEqual(out, "12321")

    # --- Test 4: Bloque dentro de una Estructura de Control (if) ---
    def test_block_inside_if_statement(self):
        """
        Asegura que el alcance del bloque funciona correctamente cuando
        es el cuerpo de una sentencia 'if'.
        """
        code = """
        main: function void() = {
            x: integer = 100;
            if (true) {
                y: integer = 25;
                x = x + y; // Modifica la 'x' exterior
                print x; // -> 125
            }
            print x; // -> 125
        }
        """
        _, out = self.get_ir(code)
        self.assertEqual(out, "125125")

    # --- Test 5: Sombreado de Funciones ---
    def test_function_shadowing_in_block(self):
        """
        Un caso avanzado: verifica que una función declarada dentro de un bloque
        puede sombrear a otra con el mismo nombre, y el alcance se restaura
        correctamente.
        """
        code = """
        do_print: function void() = {
            print "[EXTERNO]";
        }
        
        main: function void() = {
            do_print(); // Llama a la función global

            {
                do_print: function void() = {
                    print "[INTERNO]";
                }
                do_print(); // Llama a la función local del bloque
            }

            do_print(); // Llama a la función global de nuevo
        }
        """
        _, out = self.get_ir(code)
        self.assertEqual(out, "[EXTERNO][INTERNO][EXTERNO]")

    # --- Test 6: Variable Global vs. Múltiples Variables Locales ---
    def test_global_vs_local_shadowing(self):
        """
        Verifica la jerarquía completa: una variable global, una local
        a una función, y otra local a un bloque, todas con el mismo nombre.
        """
        code = """
        x: integer = 1; // Global

        main: function void() = {
            print x; // Imprime la global -> 1

            x: integer = 2; // Local a main
            print x; // Imprime la de main -> 2

            {
                x: integer = 3; // Local al bloque
                print x; // Imprime la del bloque -> 3
            }

            print x; // Imprime la de main de nuevo -> 2
        }
        """
        # La llamada a `get_ir` probablemente ejecuta `main`, no el scope global directamente.
        # Por lo tanto, no veremos el 'print x' global si estuviera fuera de una función.
        _, out = self.get_ir(code)
        self.assertEqual(out, "1232")
