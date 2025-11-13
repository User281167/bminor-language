import unittest
from parser.model import *

from ir import IRGenerator, run_llvm_clang_ir
from utils import clear_errors, errors_detected


class TestWhileLoop(unittest.TestCase):
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

    def test_while_loop_basic(self):
        code = """
        main: function void() = {
            i: integer = 0;
            while (i < 3) {
                print i;
                i = i + 1;
            }
        }
        """
        _, out = self.get_ir(code)
        self.assertEqual(out, "012")

    def test_while_loop_with_if(self):
        code = """
        main: function void() = {
            i: integer = 0;
            while (i < 3) {
                if (i < 2) {
                    print i;
                }
                i = i + 1;
            }
        }
        """
        _, out = self.get_ir(code)
        self.assertEqual(out, "01")

    def test_while_loop_with_declaration(self):
        code = """
        main: function void() = {
            i: integer = 0;
            while (i < 3) {
                x: integer = i * 2;
                print x;
                i = i + 1;
            }
        }
        """
        _, out = self.get_ir(code)
        self.assertEqual(out, "024")

    def test_while_loop_nested(self):
        code = """
        main: function void() = {
            i: integer = 0;
            while (i < 2) {
                j: integer = 0;
                while (j < 3) {
                    print i;
                    print j;
                    j = j + 1;
                }
                i = i + 1;
            }
        }
        """
        _, out = self.get_ir(code)
        self.assertEqual(out, "000102101112")

    def test_while_loop_complex_condition(self):
        code = """
        main: function void() = {
            i: integer = 0;
            while ((i * i) < 10) {
                print i;
                i = i + 1;
            }
        }
        """
        _, out = self.get_ir(code)
        self.assertEqual(out, "0123")

    def test_while_loop_no_body(self):
        code = """
        main: function void() = {
            i: integer = 0;
            while (i < 3) i = i + 1;
            print i;
        }
        """
        _, out = self.get_ir(code)
        self.assertEqual(out, "3")

    def test_while_loop_local_scope(self):
        code = """
        main: function void() = {
            i: integer = 0;

            while (i < 3) {
                x: integer = i;

                print x;
                i = i + 1;
            }
        }
        """
        _, out = self.get_ir(code)
        self.assertEqual(out, "012")
