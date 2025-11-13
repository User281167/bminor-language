import unittest
from parser.model import *  # Asegúrate de que esta importación sea correcta

from ir import IRGenerator, run_llvm_clang_ir
from utils import clear_errors, errors_detected


class TestBreakStmt(unittest.TestCase):
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

    def test_break_basic(self):
        code = """
        main: function void() = {
            i: integer;
            for (i = 0; i < 10; i++) {
                if (i == 5) {
                    break;
                }
                print i;
            }
        }
        """
        _, out = self.get_ir(code)
        self.assertEqual(out, "01234")

    def test_break_at_end_of_loop(self):
        code = """
        main: function void() = {
            i: integer;
            for (i = 0; i < 3; i++) {
                print i;
                break;
            }
        }
        """
        _, out = self.get_ir(code)
        self.assertEqual(out, "0")

    def test_break_in_else(self):
        code = """
        main: function void() = {
            i: integer;
            for (i = 0; i < 5; i++) {
                if (i % 2 == 0) {
                    print i;
                } else {
                    break;
                }
            }
        }
        """
        _, out = self.get_ir(code)
        self.assertEqual(out, "0")

    def test_break_nested_if(self):
        code = """
        main: function void() = {
            i: integer;
            for (i = 0; i < 5; i++) {
                if (i > 1) {
                    if (i < 4) {
                        break;
                    }
                }
                print i;
            }
        }
        """
        _, out = self.get_ir(code)
        self.assertEqual(out, "01")

    def test_break_nested_loops(self):
        code = """
        main: function void() = {
            i: integer;
            j: integer;
            for (i = 0; i < 3; i++) {
                for (j = 0; j < 3; j++) {
                    if (j == 1) {
                        break; // Break inner loop
                    }
                    print i;
                    print j;
                }
            }
        }
        """
        _, out = self.get_ir(code)
        self.assertEqual(out, "001020")

    def test_break_nested_loops_outer(self):
        code = """
        main: function void() = {
            i: integer;
            j: integer;
            for (i = 0; i < 3; i++) {
                for (j = 0; j < 3; j++) {
                    if (i == 1) {
                        break; // Break outer loop
                    }
                    print i;
                    print j;
                }
            }
        }
        """
        _, out = self.get_ir(code)
        self.assertEqual(out, "000102202122")

    def test_break_while_loop(self):
        code = """
        main: function void() = {
            i: integer = 0;
            while (i < 5) {
                if (i == 3) {
                    break;
                }
                print i;
                i = i + 1;
            }
        }
        """
        _, out = self.get_ir(code)
        self.assertEqual(out, "012")

    def test_break_do_while_loop(self):
        code = """
        main: function void() = {
            i: integer = 0;
            do {
                if (i == 3) {
                    break;
                }
                print i;
                i = i + 1;
            } while (i < 5);
        }
        """
        _, out = self.get_ir(code)
        self.assertEqual(out, "012")

    def test_break_no_body_for_loop(self):
        code = """
        main: function void() = {
            i: integer;
            for (i = 0; i < 5; i++)
                if (i == 2) break; else print i;
        }
        """
        _, out = self.get_ir(code)
        self.assertEqual(out, "01")
