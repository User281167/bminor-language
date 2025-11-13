import unittest
from parser.model import *  # Asegúrate de que esta importación sea correcta

from ir import IRGenerator, run_llvm_clang_ir
from utils import clear_errors, errors_detected


class TestForLoop(unittest.TestCase):
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
        except Exception as e:
            print(f"Error al ejecutar LLVM/Clang IR: {e}")
            print("--- LLVM IR ---")
            print(str(gen))
            print("---------------")
            self.fail(f"La ejecución del IR falló: {e}")

        return gen, out

    def test_for_loop_basic(self):
        code = """
        main: function void() = {
            i: integer;
            for (i = 0; i <= 2; i++) {
                print i;
            }
        }
        """
        _, out = self.get_ir(code)
        self.assertEqual(out, "012")

    def test_for_loop_with_if(self):
        code = """
        main: function void() = {
            i: integer;
            for (i = 0; i <= 2; i++) {
                if (i < 2) {
                    print i;
                }
            }
        }
        """
        _, out = self.get_ir(code)
        self.assertEqual(out, "01")

    def test_for_loop_with_print_and_space(self):
        code = """
        main: function void() = {
            i: integer;
            for (i = 0; i <= 2; i++) {
                print i;
                print ' ';
            }
        }
        """
        _, out = self.get_ir(code)
        self.assertEqual(out, "0 1 2 ")

    def test_for_loop_decrement(self):
        code = """
        main: function void() = {
            i: integer;
            for (i = 2; i >= 0; i--) {
                print i;
            }
        }
        """
        _, out = self.get_ir(code)
        self.assertEqual(out, "210")

    def test_for_loop_with_declaration_and_if(self):
        code = """
        main: function void() = {
            i: integer;
            for (i = 0; i <= 3; i++) {
                j: integer = i * 2;
                if (j < 5) {
                    print j;
                }
            }
        }
        """
        _, out = self.get_ir(code)
        self.assertEqual(out, "024")

    def test_for_loop_no_init(self):
        code = """
        main: function void() = {
            i: integer = 0;
            for (; i <= 2; i++) {
                print i;
            }
        }
        """
        _, out = self.get_ir(code)
        self.assertEqual(out, "012")

    def test_for_loop_nested(self):
        code = """
        main: function void() = {
            i: integer;
            j: integer;
            for (i = 0; i < 2; i++) {
                for (j = 0; j < 3; j++) {
                    print i;
                    print j;
                }
            }
        }
        """
        _, out = self.get_ir(code)
        self.assertEqual(out, "000102101112")

    def test_for_loop_nested_with_if(self):
        code = """
        main: function void() = {
            i: integer;
            j: integer;
            for (i = 0; i < 3; i++) {
                for (j = 0; j < 3; j++) {
                    if (i != j) {
                        print i;
                        print j;
                    }
                }
            }
        }
        """
        _, out = self.get_ir(code)
        self.assertEqual(out, "010210122021")

    def test_for_loop_complex_condition(self):
        code = """
        main: function void() = {
            i: integer;
            for (i = 0; i <= 10; i++) {
                if ((i * i) < 50) {
                    print i;
                }
            }
        }
        """
        _, out = self.get_ir(code)
        self.assertEqual(out, "01234567")

    def test_for_renew_var(self):
        code = """
        main: function void() = {
            i: integer;
            x: integer;

            for (i = 0; i < 3; i++) {
                x: integer = i;
                print x;
            }
        }
        """
        _, out = self.get_ir(code)
        self.assertEqual(out, "012")
