import unittest
from parser.model import *  # Asegúrate de que esta importación sea correcta

from ir import IRGenerator, run_llvm_clang_ir
from utils import clear_errors, errors_detected


class TestContinueStmt(unittest.TestCase):
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

    def test_continue_scope(self):
        code = """
        main: function void() = {
            i: integer;
            for (i = 0; i < 5; i++) {
                continue;
                print i;
            }
        }
        """
        _, out = self.get_ir(code)
        self.assertEqual(out, "")

    def test_continue_basic(self):
        code = """
        main: function void() = {
            i: integer;
            for (i = 0; i < 5; i++) {
                if (i == 2) {
                    continue;
                }
                print i;
            }
        }
        """
        _, out = self.get_ir(code)
        self.assertEqual(out, "0134")

    def test_continue_at_end_of_loop(self):
        code = """
        main: function void() = {
            i: integer;
            for (i = 0; i < 3; i++) {
                print i;
                if (i == 1) {
                    continue;
                }
            }
        }
        """
        _, out = self.get_ir(code)
        self.assertEqual(out, "012")

    def test_continue_in_else(self):
        code = """
        main: function void() = {
            i: integer;
            for (i = 0; i < 5; i++) {
                if (i % 2 == 0) {
                    print i;
                } else {
                    continue;
                }
            }
        }
        """
        _, out = self.get_ir(code)
        self.assertEqual(out, "024")

    def test_continue_nested_if(self):
        code = """
        main: function void() = {
            i: integer;
            for (i = 0; i < 5; i++) {
                if (i > 1) {
                    if (i < 4) {
                        continue;
                    }
                }
                print i;
            }
        }
        """
        _, out = self.get_ir(code)
        self.assertEqual(out, "014")

    def test_continue_nested_loops(self):
        code = """
        main: function void() = {
            i: integer;
            j: integer;
            for (i = 0; i < 3; i++) {
                for (j = 0; j < 3; j++) {
                    if (j == 1) {
                        continue; // Continue inner loop
                    }
                    print i;
                    print j;
                }
            }
        }
        """
        _, out = self.get_ir(code)
        self.assertEqual(out, "000210122022")

    def test_continue_nested_loops_outer(self):
        code = """
        main: function void() = {
            i: integer;
            j: integer;
            for (i = 0; i < 3; i++) {
                for (j = 0; j < 3; j++) {
                    if (i == 1) {
                        continue; // Continue outer loop
                    }
                    print i;
                    print j;
                }
            }
        }
        """
        _, out = self.get_ir(code)
        self.assertEqual(out, "000102202122")

    def test_continue_while_loop(self):
        code = """
        main: function void() = {
            i: integer = 0;
            while (i < 5) {
                i = i + 1;
                if (i == 3) {
                    continue;
                }
                print i;
            }
        }
        """
        _, out = self.get_ir(code)
        self.assertEqual(out, "1245")

    def test_continue_do_while_loop(self):
        code = """
        main: function void() = {
            i: integer = 0;
            do {
                i = i + 1;
                if (i == 3) {
                    continue;
                }
                print i;
            } while (i < 5);
        }
        """
        _, out = self.get_ir(code)
        self.assertEqual(out, "1245")

    def test_continue_no_body_for_loop(self):
        code = """
        main: function void() = {
            i: integer;
            for (i = 0; i < 5; i++)
                if (i == 2) continue; else print i;
        }
        """
        _, out = self.get_ir(code)
        self.assertEqual(out, "0134")
