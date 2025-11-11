import unittest
from parser.model import *

from ir import IRGenerator, run_llvm_clang_ir
from utils import clear_errors, errors_detected


class TestAutoAssignments(unittest.TestCase):
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

    # --- Tests para Inferencia de Tipo con 'auto' ---

    def test_auto_infer_int(self):
        code = """
        x: auto = 10;
        main: function void () = {
            print x;
        }
        """
        _, out = self.get_ir(code)
        self.assertEqual(out, "10")

    def test_auto_infer_float(self):
        code = """
        y: auto = 3.14;
        main: function void () = {
            print y;
        }
        """
        _, out = self.get_ir(code)
        self.assertAlmostEqual(float(out), 3.14)

    def test_auto_infer_bool(self):
        code = """
        z: auto = true;
        main: function void () = {
            print z;
        }
        """
        _, out = self.get_ir(code)
        self.assertEqual(out, "true")

    def test_auto_infer_char(self):
        code = """
        c: auto = 'A';
        main: function void () = {
            print c;
        }
        """
        _, out = self.get_ir(code)
        self.assertEqual(out, "A")

    # --- Tests para Reasignación con 'auto' ---
    # El tipo se fija en la declaración, pero el valor puede cambiar.

    def test_auto_reassign_int(self):
        code = """
        x: auto = 10; // x se infiere como integer
        main: function void () = {
            x = 20; // Reasignación válida
            print x;
            x = -5; // Otra reasignación válida
            print x;
        }
        """
        _, out = self.get_ir(code)
        self.assertEqual(out, "20-5")

    def test_auto_reassign_float(self):
        code = """
        y: auto = 1.5; // y se infiere como float
        main: function void () = {
            y = 2.7; // Reasignación válida
            print y;
            y = -(3.0 / 2.0); // y = -1.5
            print y;
        }
        """
        _, out = self.get_ir(code)
        # self.assertAlmostEqual(float(out), 2.7)
        # Para la segunda impresión, necesitas tener una forma de capturar múltiples prints
        # Si print siempre añade newline, la salida sería "2.700000\n-1.500000"
        # Asumiendo que podemos verificar la segunda salida:
        self.assertAlmostEqual(float("-" + out.split("-")[1]), -1.5)

    def test_auto_reassign_bool(self):
        code = """
        z: auto = true; // z se infiere como boolean
        main: function void () = {
            z = false; // Reasignación válida
            print z;
            z = !false; // z = true
            print z;
        }
        """
        _, out = self.get_ir(code)
        self.assertEqual(out, "falsetrue")

    def test_auto_reassign_char(self):
        code = """
        c: auto = 'a'; // c se infiere como char
        main: function void () = {
            c = 'b'; // Reasignación válida
            print c;
            c = 'Z'; // Otra reasignación válida
            print c;
        }
        """
        _, out = self.get_ir(code)
        self.assertEqual(out, "bZ")

    # --- Test de Errores de Tipo con Reasignación ---
    # 'auto' fija el tipo. Intentar asignar un tipo diferente debe ser un error.

    # def test_auto_reassign_type_error_int_to_float(self):
    #     code = """
    #     x: auto = 10; // x es integer
    #     main: function void () = {
    #         x = 5.5; // ERROR: Intentando asignar float a un integer
    #         print x;
    #     }
    #     """
    #     # Para este test, esperamos que errors_detected() sea True
    #     # y que la ejecución de run_llvm_clang_ir falle o no imprima nada
    #     gen = IRGenerator().generate_from_code(code)
    #     self.assertTrue(
    #         errors_detected(),
    #         "Se esperaba un error de tipo para asignación incorrecta a 'auto'",
    #     )
    # Opcional: verificar que run_llvm_clang_ir no produce una salida válida o falla
    # try:
    #     run_llvm_clang_ir(str(gen), add_runtime=True)
    #     self.fail("Se esperaba un fallo debido a error de tipo, pero se ejecutó.")
    # except:
    #     pass # Se espera que falle o no produzca salida imprimible

    # def test_auto_reassign_type_error_char_to_int(self):
    #     code = """
    #     c: auto = 'a'; // c es char
    #     main: function void () = {
    #         c = 97; // ERROR: Intentando asignar int a char (si no hay conversión explícita permitida)
    #         print c;
    #     }
    #     """
    #     gen = IRGenerator().generate_from_code(code)
    #     self.assertTrue(
    #         errors_detected(),
    #         "Se esperaba un error de tipo para asignación incorrecta a 'auto' char",
    #     )

    # --- Test con Asignación desde Expresiones ---

    def test_auto_assign_from_expr(self):
        code = """
        result: auto = (5 + 3) * 2; // Se infiere como integer
        main: function void () = {
            print result;
        }
        """
        _, out = self.get_ir(code)
        self.assertEqual(out, "16")
        self.assertEqual(out, "16")
