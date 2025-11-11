import unittest
from parser.model import *

from ir import IRGenerator, run_llvm_clang_ir
from utils import clear_errors, errors_detected


class TestIfElse(unittest.TestCase):
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

    # --- Test básico de IF ---
    def test_if_true_branch(self):
        code = """
        main: function void () = {
            if (true) {
                print 1;
            }
        }
        """
        _, out = self.get_ir(code)
        self.assertEqual(out, "1")

    def test_if_false_branch_no_else(self):
        code = """
        main: function void () = {
            if (false) {
                print 1; // Esta línea no se ejecuta
            }
            print 2; // Esto sí se ejecuta
        }
        """
        _, out = self.get_ir(code)
        self.assertEqual(out, "2")  # Solo imprime el 2

    # --- Test básico de IF-ELSE ---
    def test_if_else_true(self):
        code = """
        main: function void () = {
            if (true) {
                print 1;
            } else {
                print 2; // Esta línea no se ejecuta
            }
            print 3; // Esto sí se ejecuta
        }
        """
        _, out = self.get_ir(code)
        self.assertEqual(out, "13")

    def test_if_else_false(self):
        code = """
        main: function void () = {
            if (false) {
                print 1; // Esta línea no se ejecuta
            } else {
                print 2;
            }
            print 3; // Esto sí se ejecuta
        }
        """
        _, out = self.get_ir(code)
        self.assertEqual(out, "23")

    # --- Test de IF con variables y expresiones ---
    def test_if_variable_condition_true(self):
        code = """
        a: boolean = true;
        main: function void () = {
            if (a) {
                print 10;
            }
            print 20;
        }
        """
        _, out = self.get_ir(code)
        self.assertEqual(out, "1020")

    def test_if_variable_condition_false(self):
        code = """
        a: boolean = false;
        main: function void () = {
            if (a) {
                print 10; // No se ejecuta
            }
            print 20;
        }
        """
        _, out = self.get_ir(code)
        self.assertEqual(out, "20")

    def test_if_expression_condition(self):
        code = """
        x: integer = 5;
        main: function void () = {
            if (x > 3) { // 5 > 3 es true
                print 1;
            } else {
                print 2;
            }
            print 3;
        }
        """
        _, out = self.get_ir(code)
        self.assertEqual(out, "13")

    # --- Test de IF-ELSE IF-ELSE (simulado con anidamiento) ---
    def test_if_else_if_else_structure(self):
        code = """
        val: integer = 0; // Prueba con val = 0, 1, 2
        main: function void () = {
            if (val == 0) {
                print 1; // Condición 1: val == 0 -> True
            } else if (val == 1) { // Else branch del primer if
                print 2; // Condición 2: val == 1 -> False (si val era 0)
            } else { // Else branch del segundo if (el que se ejecuta si val == 0)
                print 3; // Condición 3: Else -> True
            }
            print 4; // Siempre se ejecuta
        }
        """
        # Para probar este test, necesitarías ejecutarlo 3 veces, cambiando `val`
        # o tener una forma de pasar parámetros. Aquí probamos un caso.
        # Caso: val = 0
        # Salida esperada: 14

        # Para probarlo programáticamente con diferentes valores:
        # Puedes redefinir `code` dentro del test para cada caso, o pasar valores.

        # Probando con val = 0
        code_val0 = """
        val: integer = 0;
        main: function void () = {
            if (val == 0) {
                print 1;
            } else if (val == 1) {
                print 2;
            } else {
                print 3;
            }
            print 4;
        }
        """
        _, out_val0 = self.get_ir(code_val0)
        self.assertEqual(out_val0, "14")

        # Probando con val = 1
        code_val1 = """
        val: integer = 1;
        main: function void () = {
            if (val == 0) {
                print 1;
            } else if (val == 1) {
                print 2;
            } else {
                print 3;
            }
            print 4;
        }
        """
        _, out_val1 = self.get_ir(code_val1)
        self.assertEqual(out_val1, "24")

        # Probando con val = 2 (o cualquier otro valor que no sea 0 o 1)
        code_val2 = """
        val: integer = 2;
        main: function void () = {
            if (val == 0) {
                print 1;
            } else if (val == 1) {
                print 2;
            } else {
                print 3;
            }
            print 4;
        }
        """
        _, out_val2 = self.get_ir(code_val2)
        self.assertEqual(out_val2, "34")

    # --- Test de Anidamiento de IFs ---
    def test_nested_ifs(self):
        code = """
        a: integer = 1;
        b: integer = 2;
        main: function void () = {
            if (a == 1) { // True
                print 1;
                if (b == 2) { // True
                    print 2;
                } else {
                    print 3; // No se ejecuta
                }
                print 4; // Se ejecuta
            } else {
                print 5; // No se ejecuta
            }
            print 6; // Se ejecuta
        }
        """
        _, out = self.get_ir(code)
        self.assertEqual(out, "1246")

    def test_nested_ifs_outer_false(self):
        code = """
        a: integer = 0;
        b: integer = 2;
        main: function void () = {
            if (a == 1) { // False
                print 1; // No se ejecuta
                if (b == 2) { // No se evalúa esta rama interna
                    print 2;
                } else {
                    print 3;
                }
                print 4; // No se ejecuta
            } else { // Else de 'if (a == 1)'
                print 5;
            }
            print 6; // Se ejecuta
        }
        """
        _, out = self.get_ir(code)
        self.assertEqual(out, "56")

    def test_nested_ifs_inner_false(self):
        code = """
        a: integer = 1;
        b: integer = 0;
        main: function void () = {
            if (a == 1) { // True
                print 1;
                if (b == 2) { // False
                    print 2; // No se ejecuta
                } else {
                    print 3;
                }
                print 4; // Se ejecuta
            } else {
                print 5; // No se ejecuta
            }
            print 6; // Se ejecuta
        }
        """
        _, out = self.get_ir(code)
        self.assertEqual(out, "1346")
