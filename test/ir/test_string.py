import unittest

from ir import IRGenerator, run_llvm_clang_ir
from utils import clear_errors, errors_detected


class TestStrings(unittest.TestCase):
    def setUp(self):
        clear_errors()

    def get_ir(self, code):
        gen = IRGenerator().generate_from_code(code)
        out = ""
        self.assertFalse(
            errors_detected(), "Errores detectados durante la generación de IR"
        )

        try:
            # Asumimos que run_llvm_clang_ir puede enlazar con un runtime.c
            # que tiene una función `print_string(char*)`.
            out = run_llvm_clang_ir(str(gen), add_runtime=True)
            out = out.strip()
        except Exception as e:
            print(f"Error al ejecutar LLVM/Clang IR: {e}")
            print("--- LLVM IR ---")
            print(str(gen))
            print("---------------")
            self.fail(f"La ejecución del IR falló: {e}")

        return gen, out

    # --- Tests Básicos ---
    def test_print_simple_string(self):
        code = """
        main: function void () = {
            print "Hola, mundo!";
        }
        """
        _, out = self.get_ir(code)
        self.assertEqual(out, "Hola, mundo!")

    def test_print_empty_string(self):
        code = """
        main: function void () = {
            print "";
        }
        """
        _, out = self.get_ir(code)
        self.assertEqual(out, "")

    def test_multiple_string_prints(self):
        code = """
        main: function void () = {
            print "uno";
            print "dos";
            print "tres";
        }
        """
        _, out = self.get_ir(code)
        self.assertEqual(out, "unodostres")

    def test_string_and_integer_prints(self):
        code = """
        main: function void () = {
            print "El numero es: ";
            print 42;
            print "!";
        }
        """
        _, out = self.get_ir(code)
        self.assertEqual(out, "El numero es: 42!")

    # --- Tests de Secuencias de Escape ---
    def test_print_string_with_newline(self):
        code = """
        main: function void () = {
            print "linea 1\\nlinea 2";
        }
        """
        _, out = self.get_ir(code)
        # El strip() en get_ir() podría eliminar el último \n, así que comparamos con cuidado.
        self.assertEqual(out, "linea 1\nlinea 2")

    def test_print_string_with_tab(self):
        code = """
        main: function void () = {
            print "Columna1\\tColumna2";
        }
        """
        _, out = self.get_ir(code)
        self.assertEqual(out, "Columna1\tColumna2")

    def test_print_string_with_escaped_quote(self):
        # Este es el caso que mencionaste.
        code = """
        main: function void () = {
            print "El dijo: \\"Hola!\\"";
        }
        """
        _, out = self.get_ir(code)
        self.assertEqual(out, 'El dijo: "Hola!"')

    def test_print_string_with_escaped_backslash(self):
        code = """
        main: function void () = {
            print "La ruta es C:\\\\Users\\\\Temp";
        }
        """
        _, out = self.get_ir(code)
        self.assertEqual(out, "La ruta es C:\\Users\\Temp")

    def test_print_complex_escaped_string(self):
        code = """
        main: function void () = {
            print "Inicio\\n\\t- Item 1\\n\\t- Item 2: \\"Valor\\"\\\\Fin";
        }
        """
        expected_output = 'Inicio\n\t- Item 1\n\t- Item 2: "Valor"\\Fin'
        _, out = self.get_ir(code)
        self.assertEqual(out, expected_output)
