import unittest
from parser.model import *

from ir import IRGenerator, run_llvm_clang_ir
from utils import clear_errors, errors_detected


class TestDoWhileLoop(unittest.TestCase):
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

    def test_do_while_loop_basic(self):
        code = """
        main: function void() = {
            i: integer = 0;
            do {
                print i;
                i = i + 1;
            } while (i < 3);
        }
        """
        _, out = self.get_ir(code)
        self.assertEqual(out, "012")

    def test_do_while_loop_with_if(self):
        code = """
        main: function void() = {
            i: integer = 0;
            do {
                if (i < 2) {
                    print i;
                }
                i = i + 1;
            } while (i < 3);
        }
        """
        _, out = self.get_ir(code)
        self.assertEqual(out, "01")

    def test_do_while_loop_with_declaration(self):
        code = """
        main: function void() = {
            i: integer = 0;
            do {
                x: integer = i * 2;
                print x;
                i = i + 1;
            } while (i < 3);
        }
        """
        _, out = self.get_ir(code)
        self.assertEqual(out, "024")

    def test_do_while_loop_nested(self):
        code = """
        main: function void() = {
            i: integer = 0;
            do {
                j: integer = 0;
                do {
                    print i;
                    print j;
                    j = j + 1;
                } while (j < 3);
                i = i + 1;
            } while (i < 2);
        }
        """
        _, out = self.get_ir(code)
        self.assertEqual(out, "000102101112")

    def test_do_while_loop_complex_condition(self):
        code = """
        main: function void() = {
            i: integer = 0;
            do {
                print i;
                i = i + 1;
            } while ((i * i) < 10);
        }
        """
        _, out = self.get_ir(code)
        self.assertEqual(out, "0123")

    def test_do_while_loop_always_runs_once(self):
        code = """
        main: function void() = {
            i: integer = 5;
            do {
                print i;
                i = i + 1;
            } while (i < 3);
        }
        """
        _, out = self.get_ir(code)
        self.assertEqual(out, "5")

    def test_do_while_loop_no_body(self):
        code = """
        main: function void() = {
            i: integer = 0;
            do i = i + 1; while (i < 3);
            print i;
        }
        """
        _, out = self.get_ir(code)
        self.assertEqual(out, "3")
