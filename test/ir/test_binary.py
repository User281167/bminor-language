import unittest
from parser.model import *  # Asumo que SimpleTypes y otros modelos están aquí

from ir import IRGenerator, run_llvm_clang_ir
from utils import clear_errors, errors_detected


class TestBinOper(unittest.TestCase):
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

    # --- Tests para Operaciones Aritméticas (Integer) ---

    def test_int_add_literals(self):
        code = """
        main: function void () = {
            print 1 + 2;
        }
        """
        _, out = self.get_ir(code)
        self.assertEqual(out, "3")

    def test_int_add_variable_literal(self):
        code = """
        a: integer = 10;
        main: function void () = {
            print a + 5;
        }
        """
        _, out = self.get_ir(code)
        self.assertEqual(out, "15")

    def test_int_sub_literals(self):
        code = """
        main: function void () = {
            print 10 - 3;
        }
        """
        _, out = self.get_ir(code)
        self.assertEqual(out, "7")

    def test_int_sub_variable_literal(self):
        code = """
        a: integer = 10;
        main: function void () = {
            print 5 - a;
        }
        """
        _, out = self.get_ir(code)
        self.assertEqual(out, "-5")

    def test_int_mul_literals(self):
        code = """
        main: function void () = {
            print 7 * 6;
        }
        """
        _, out = self.get_ir(code)
        self.assertEqual(out, "42")

    def test_int_div_literals(self):
        code = """
        main: function void () = {
            print 20 / 4;
        }
        """
        _, out = self.get_ir(code)
        self.assertEqual(out, "5")

    def test_int_div_literal_variable(self):
        code = """
        b: integer = 5;
        main: function void () = {
            print 20 / b;
        }
        """
        _, out = self.get_ir(code)
        self.assertEqual(out, "4")

    def test_int_rem_literals(self):
        code = """
        main: function void () = {
            print 10 % 3;
        }
        """
        _, out = self.get_ir(code)
        self.assertEqual(out, "1")

    def test_int_pow_literals(self):
        # Asumiendo que tienes una función math_runtime.pow_int()
        code = """
        main: function void () = {
            print 2 ^ 3;
        }
        """
        _, out = self.get_ir(code)
        self.assertEqual(out, "8")

    def test_int_pow_variable_literal(self):
        code = """
        base: integer = 3;
        main: function void () = {
            print base ^ 4;
        }
        """
        _, out = self.get_ir(code)
        self.assertEqual(out, "81")

    # --- Tests para Operaciones Aritméticas (Float) ---

    def test_float_add_literals(self):
        code = """
        main: function void () = {
            print 1.5 + 2.3;
        }
        """
        gen, out = self.get_ir(code)
        # Usamos assertAlmostEqual para floats debido a posibles imprecisiones
        self.assertAlmostEqual(float(out), 3.8)

    def test_float_add_variable_literal(self):
        code = """
        x: float = 1.0;
        main: function void () = {
            print x + 2.5;
        }
        """
        _, out = self.get_ir(code)
        self.assertAlmostEqual(float(out), 3.5)

    def test_float_sub_literals(self):
        code = """
        main: function void () = {
            print 5.5 - 2.1;
        }
        """
        _, out = self.get_ir(code)
        self.assertAlmostEqual(float(out), 3.4)

    def test_float_mul_literals(self):
        code = """
        main: function void () = {
            print 2.5 * 4.0;
        }
        """
        _, out = self.get_ir(code)
        self.assertAlmostEqual(float(out), 10.0)

    def test_float_div_literals(self):
        code = """
        main: function void () = {
            print 10.0 / 4.0;
        }
        """
        _, out = self.get_ir(code)
        self.assertAlmostEqual(float(out), 2.5)

    def test_float_rem_literals(self):
        code = """
        main: function void () = {
            print 10.5 % 3.0;
        }
        """
        _, out = self.get_ir(code)
        # El módulo de floats puede ser un poco menos predecible que el de enteros
        self.assertAlmostEqual(float(out), 1.5)

    # --- Tests para Operaciones de Comparación (Integer) ---

    def test_int_lt_literals(self):
        code = """
        main: function void () = {
            print 5 < 10;
        }
        """
        _, out = self.get_ir(code)
        self.assertEqual(out, "true")

    def test_int_lt_equal_literals(self):
        code = """
        main: function void () = {
            print 10 <= 10;
        }
        """
        _, out = self.get_ir(code)
        self.assertEqual(out, "true")

    def test_int_gt_literals(self):
        code = """
        main: function void () = {
            print 15 > 10;
        }
        """
        _, out = self.get_ir(code)
        self.assertEqual(out, "true")

    def test_int_gt_equal_literals(self):
        code = """
        main: function void () = {
            print 10 >= 10;
        }
        """
        _, out = self.get_ir(code)
        self.assertEqual(out, "true")

    def test_int_eq_literals(self):
        code = """
        main: function void () = {
            print 7 == 7;
        }
        """
        _, out = self.get_ir(code)
        self.assertEqual(out, "true")

    def test_int_neq_literals(self):
        code = """
        main: function void () = {
            print 7 != 8;
        }
        """
        _, out = self.get_ir(code)
        self.assertEqual(out, "true")

    # --- Tests para Operaciones de Comparación (Float) ---
    # Nota: Usamos `fcmp_ordered` en tu código, lo cual es bueno.
    # Las comparaciones de floats pueden ser complicadas con NaN.
    # Estos tests asumen valores "normales".

    def test_float_lt_literals(self):
        code = """
        main: function void () = {
            print 5.5 < 10.1;
        }
        """
        _, out = self.get_ir(code)
        self.assertEqual(out, "true")

    def test_float_lt_equal_literals(self):
        code = """
        main: function void () = {
            print 10.1 <= 10.1;
        }
        """
        _, out = self.get_ir(code)
        self.assertEqual(out, "true")

    def test_float_gt_literals(self):
        code = """
        main: function void () = {
            print 15.5 > 10.1;
        }
        """
        _, out = self.get_ir(code)
        self.assertEqual(out, "true")

    def test_float_gt_equal_literals(self):
        code = """
        main: function void () = {
            print 10.1 >= 10.1;
        }
        """
        _, out = self.get_ir(code)
        self.assertEqual(out, "true")

    def test_float_eq_literals(self):
        code = """
        main: function void () = {
            print 7.7 == 7.7;
        }
        """
        _, out = self.get_ir(code)
        self.assertEqual(out, "true")

    def test_float_neq_literals(self):
        code = """
        main: function void () = {
            print 7.7 != 8.8;
        }
        """
        _, out = self.get_ir(code)
        self.assertEqual(out, "true")

    # --- Tests para Operaciones Lógicas (Boolean) ---

    def test_bool_and_literals(self):
        code = """
        main: function void () = {
            print true && true;
        }
        """
        gen, out = self.get_ir(code)
        self.assertEqual(out, "true")

    def test_bool_and_mixed(self):
        code = """
        a: boolean = true;
        main: function void () = {
            print a && false;
        }
        """
        _, out = self.get_ir(code)
        self.assertEqual(out, "false")

    def test_bool_or_literals(self):
        code = """
        main: function void () = {
            print false || true;
        }
        """
        _, out = self.get_ir(code)
        self.assertEqual(out, "true")

    def test_bool_or_mixed(self):
        code = """
        a: boolean = false;
        main: function void () = {
            print a || false;
        }
        """
        _, out = self.get_ir(code)
        self.assertEqual(out, "false")

    # --- Tests con combinaciones de tipos ---
    # Dependiendo de tu lenguaje, esto podría ser un error de tipo
    # o una coerción automática. Si es un error de tipo, no necesitas estos tests
    # o deberías añadir tests de error de tipo. Si hay coerción, pruébala.

    # Ejemplo: Si tu lenguaje permite comparar int con float y los coerces
    # def test_int_float_compare(self):
    #     code = """
    #     a: integer = 5;
    #     b: float = 5.0;
    #     main: function void () = {
    #         print a == b; # Asumiendo coerción de int a float
    #     }
    #     """
    #     _, out = self.get_ir(code)
    #     self.assertEqual(out, "true")

    # --- Test de complejidad combinando operaciones ---
    def test_complex_expression_int(self):
        code = """
        a: integer = 2;
        b: integer = 3;
        main: function void () = {
            print (a + b) * 2; // Esperado: (2 + 3) * 2 = 10
        }
        """
        _, out = self.get_ir(code)
        self.assertEqual(out, "10")

    def test_complex_expression_float(self):
        code = """
        x: float = 1.5;
        y: float = 2.0;
        main: function void () = {
            print (x * y) + 1.0; // Esperado: (1.5 * 2.0) + 1.0 = 3.0 + 1.0 = 4.0
        }
        """
        _, out = self.get_ir(code)
        self.assertAlmostEqual(float(out), 4.0)

    def test_complex_expression_bool(self):
        code = """
        p: boolean = true;
        q: boolean = false;
        r: boolean = true;
        main: function void () = {
            print (p && q) || r; // Esperado: (true && false) || true = false || true = true
        }
        """
        _, out = self.get_ir(code)
        self.assertEqual(out, "true")
        self.assertEqual(out, "true")

    # --- Tests para Operaciones de Comparación (Char) ---

    def test_char_lt_literals(self):
        code = """
        main: function void () = {
            print 'a' < 'b';
        }
        """
        _, out = self.get_ir(code)
        # 'a' tiene un valor ASCII menor que 'b'
        self.assertEqual(out, "true")

    def test_char_lt_equal_literals(self):
        code = """
        main: function void () = {
            print 'z' <= 'z';
        }
        """
        _, out = self.get_ir(code)
        # Son iguales
        self.assertEqual(out, "true")

    def test_char_gt_literals(self):
        code = """
        main: function void () = {
            print 'c' > 'a';
        }
        """
        _, out = self.get_ir(code)
        # 'c' tiene un valor ASCII mayor que 'a'
        self.assertEqual(out, "true")

    def test_char_gt_equal_literals(self):
        code = """
        main: function void () = {
            print 'x' >= 'y';
        }
        """
        _, out = self.get_ir(code)
        # 'x' es menor que 'y', así que esto debe ser falso
        self.assertEqual(out, "false")

    def test_char_eq_literals(self):
        code = """
        main: function void () = {
            print 'M' == 'M';
        }
        """
        _, out = self.get_ir(code)
        self.assertEqual(out, "true")

    def test_char_neq_literals(self):
        code = """
        main: function void () = {
            print 'A' != 'B';
        }
        """
        _, out = self.get_ir(code)
        self.assertEqual(out, "true")

    # --- Tests combinando chars con variables y literales ---

    def test_char_lt_variable_literal(self):
        code = """
        char_var: char = 'p';
        main: function void () = {
            print char_var < 'q';
        }
        """
        _, out = self.get_ir(code)
        self.assertEqual(out, "true")

    def test_char_eq_variable_literal(self):
        code = """
        char_var: char = 'X';
        main: function void () = {
            print char_var == 'Y';
        }
        """
        _, out = self.get_ir(code)
        self.assertEqual(out, "false")

    def test_char_neq_variable_literal(self):
        code = """
        char_var: char = 'm';
        main: function void () = {
            print char_var != 'm';
        }
        """
        _, out = self.get_ir(code)
        self.assertEqual(out, "false")
