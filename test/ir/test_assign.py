import unittest
from parser.model import *

from ir import IRGenerator, run_llvm_clang_ir
from utils import clear_errors, errors_detected


class TestAssignments(unittest.TestCase):
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

    # --- Tests para Asignación de Integer ---

    def test_assign_int_literal(self):
        code = """
        x: integer;
        main: function void () = {
            x = 123;
            print x;
        }
        """
        _, out = self.get_ir(code)
        self.assertEqual(out, "123")

    def test_assign_int_variable(self):
        code = """
        a: integer = 10;
        x: integer;
        main: function void () = {
            x = a;
            print x;
        }
        """
        _, out = self.get_ir(code)
        self.assertEqual(out, "10")

    def test_assign_int_unary_neg(self):
        code = """
        x: integer;
        main: function void () = {
            x = -(5 + 2); // x = -7
            print x;
        }
        """
        _, out = self.get_ir(code)
        self.assertEqual(out, "-7")

    def test_assign_int_binary_expr(self):
        code = """
        a: integer = 5;
        b: integer = 3;
        x: integer;
        main: function void () = {
            x = a * (b + 2); // x = 5 * (3 + 2) = 5 * 5 = 25
            print x;
        }
        """
        _, out = self.get_ir(code)
        self.assertEqual(out, "25")

    # --- Tests para Asignación de Float ---

    def test_assign_float_literal(self):
        code = """
        y: float;
        main: function void () = {
            y = 3.14159;
            print y;
        }
        """
        _, out = self.get_ir(code)
        self.assertAlmostEqual(float(out), 3.14159)

    def test_assign_float_variable(self):
        code = """
        a: float = 2.718;
        y: float;
        main: function void () = {
            y = a;
            print y;
        }
        """
        _, out = self.get_ir(code)
        self.assertAlmostEqual(float(out), 2.718)

    def test_assign_float_unary_neg(self):
        code = """
        y: float;
        main: function void () = {
            y = -(1.5 * 2.0); // y = -3.0
            print y;
        }
        """
        _, out = self.get_ir(code)
        self.assertAlmostEqual(float(out), -3.0)

    def test_assign_float_binary_expr(self):
        code = """
        a: float = 10.0;
        b: float = 2.0;
        y: float;
        main: function void () = {
            y = (a / b) + 0.5; // y = (10.0 / 2.0) + 0.5 = 5.0 + 0.5 = 5.5
            print y;
        }
        """
        _, out = self.get_ir(code)
        self.assertAlmostEqual(float(out), 5.5)

    # --- Tests para Asignación de Boolean ---

    def test_assign_bool_literal_true(self):
        code = """
        x: boolean;
        main: function void () = {
            x = true;
            print x;
        }
        """
        _, out = self.get_ir(code)
        self.assertEqual(out, "true")

    def test_assign_bool_literal_false(self):
        code = """
        x: boolean;
        main: function void () = {
            x = false;
            print x;
        }
        """
        _, out = self.get_ir(code)
        self.assertEqual(out, "false")

    def test_assign_bool_variable(self):
        code = """
        a: boolean = true;
        x: boolean;
        main: function void () = {
            x = a;
            print x;
        }
        """
        _, out = self.get_ir(code)
        self.assertEqual(out, "true")

    def test_assign_bool_unary_not(self):
        code = """
        x: boolean;
        main: function void () = {
            x = !true; // x = false
            print x;
        }
        """
        _, out = self.get_ir(code)
        self.assertEqual(out, "false")

    def test_assign_bool_binary_expr(self):
        code = """
        a: boolean = true;
        b: boolean = false;
        x: boolean;
        main: function void () = {
            x = a && (b || true); // x = true && (false || true) = true && true = true
            print x;
        }
        """
        _, out = self.get_ir(code)
        self.assertEqual(out, "true")

    # --- Tests para Asignación de Char ---

    def test_assign_char_literal(self):
        code = """
        c: char;
        main: function void () = {
            c = 'R';
            print c;
        }
        """
        _, out = self.get_ir(code)
        self.assertEqual(out, "R")

    def test_assign_char_variable(self):
        code = """
        a: char = 'X';
        c: char;
        main: function void () = {
            c = a;
            print c;
        }
        """
        _, out = self.get_ir(code)
        self.assertEqual(out, "X")

    # def test_assign_char_from_int_literal_expr(self):
    #     # Si tu lenguaje permite esto (conversión implícita de int a char)
    #     # Esto puede ser un error de tipo si no.
    #     # Ejemplo: Asignar el valor numérico de 'A' (65) a un char.
    #     code = """
    #     c: char;
    #     main: function void () = {
    #         c = 65; // Valor ASCII de 'A'
    #         print c;
    #     }
    #     """
    #     _, out = self.get_ir(code)
    #     self.assertEqual(out, "A")

    # def test_assign_char_from_related_char_expr(self):
    #     code = """
    #     c: char;
    #     main: function void () = {
    #         c = 'a' + 1; // Si el lenguaje permite sumar a un char (interpreta como int y convierte de vuelta)
    #                      // Esto usualmente resultaría en 'b'
    #         print c;
    #     }
    #     """
    #     _, out = self.get_ir(code)
    #     # Asumiendo que 'a' + 1 resulta en 'b' (valor ASCII 97 + 1 = 98)
    #     self.assertEqual(
    #         out, "b"
    #     )  # Asumiendo que 'a' + 1 resulta en 'b' (valor ASCII 97 + 1 = 98)
    #     self.assertEqual(out, "b")
