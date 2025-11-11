import unittest
from parser.model import *

from ir import IRGenerator, run_llvm_clang_ir
from utils import clear_errors, errors_detected


class TestIncDecInteger(unittest.TestCase):  # Renombrado para mayor claridad
    def setUp(self):
        clear_errors()

    def get_ir(self, code):
        gen = IRGenerator().generate_from_code(code)
        out = ""
        self.assertFalse(
            errors_detected(), "Errores detectados durante la generación de IR"
        )

        try:
            # Asegúrate de que run_llvm_clang_ir maneje correctamente los prints sin newline
            out = run_llvm_clang_ir(str(gen), add_runtime=True)
            out = out.strip()
        except Exception as e:
            print(f"Error al ejecutar LLVM/Clang IR: {e}")
            print("--- LLVM IR ---")
            print(str(gen))
            print("---------------")
            self.fail(f"La ejecución del IR falló: {e}")

        return gen, out

    def test_inc_post_variable(self):
        code = """
        x: integer = 1;
        y: integer;
        main: function void () = {
            y = x++; // y toma el valor de x (1), luego x se incrementa a 2
            print y; // Imprime 1
            print x; // Imprime 2
        }
        """
        _, out = self.get_ir(code)
        self.assertEqual(out, "12")  # Sin saltos de línea

    def test_inc_pre_variable(self):
        code = """
        z: integer = 1;
        main: function void () = {
            z = ++z; // z se incrementa a 2, luego z toma el nuevo valor de z (2). Resultado: z = 2
            print z; // Imprime 2
        }
        """
        _, out = self.get_ir(code)
        self.assertEqual(out, "2")

    def test_inc_pre_expr(self):
        code = """
        x: integer = 1;
        w: integer;
        main: function void () = {
            // En este punto, el análisis semántico habría validado que x es una lvalue.
            // La expresión `1 - x` NO es una lvalue modificable.
            // Si tu lenguaje permite `++` sobre la *evaluación* de una expresión NO lvalue,
            // y esa evaluación se hace temporalmente, y el `++` se aplica al temporal,
            // entonces la semántica debe ser clara.
            // La interpretación más común y segura es que `++(expr)` donde expr no es lvalue es un error.
            // Si quieres probar la generación de IR para esto, ASUME una semántica
            // donde el compilador crea un temporal, incrementa el temporal, y asigna ese temporal.
            // En este caso: 1-x = 0. Temporal = 0. Temporal++ -> Temporal = 1. w = Temporal (1). x sigue siendo 1.
            w = ++(1 - x);
            print w; // Debería imprimir 1 según esta semántica.
            print x; // x no se modifica -> imprime 1.
        }
        """
        _, out = self.get_ir(code)
        self.assertEqual(out, "11")  # w = 1, x = 1

    def test_dec_post_variable(self):
        code = """
        x: integer = 5;
        y: integer;
        main: function void () = {
            y = x--; // y toma el valor de x (5), luego x se decrementa a 4
            print y; // Imprime 5
            print x; // Imprime 4
        }
        """
        _, out = self.get_ir(code)
        self.assertEqual(out, "54")

    def test_dec_pre_variable(self):
        code = """
        z: integer = 5;
        main: function void () = {
            z = --z; // z se decrementa a 4, luego z toma el nuevo valor de z (4). Resultado: z = 4
            print z; // Imprime 4
        }
        """
        _, out = self.get_ir(code)
        self.assertEqual(out, "4")

    def test_dec_pre_expr(self):
        code = """
        x: integer = 5;
        w: integer;
        main: function void () = {
            // Similar a inc_pre_expr, asumiendo que la expr no modificable
            // (x-1) crea un temporal. --temporal evalúa a 3. w = 3. x sigue 5.
            w = --(x - 1);
            print w; // Imprime 3
            print x; // Imprime 5
        }
        """
        _, out = self.get_ir(code)
        self.assertEqual(out, "35")

    # --- Test de Secuencia de Operaciones Inc/Dec ---

    def test_sequence_inc_dec_post_pre(self):
        code = """
        a: integer = 1;
        b: integer = 2;
        res_ab: integer;
        res_ba: integer;
        main: function void () = {
            // a = 1, b = 2
            // res_ab = a++ + b--; // a++ dev 1, b-- dev 2. Luego a=2, b=1. res_ab = 1 + 2 = 3.
            res_ab = a++ + b--;
            print res_ab; // 3
            print a; // 2
            print b; // 1

            // res_ba = ++a + --b; // a=2, b=1. ++a -> a=3. --b -> b=0. res_ba = 3 (a) + 0 (b) = 3.
            res_ba = ++a + --b;
            print res_ba; // 3
            print a; // 3
            print b; // 0
        }
        """
        _, out = self.get_ir(code)
        self.assertEqual(out, "321330")

    def test_sequence_complex_expr_inc_dec(self):
        code = """
        val: integer = 10;
        res: integer;
        main: function void () = {
            // val = 10
            // res = val++ * 2 + --val;
            // Pasos:
            // 1. val++: Devuelve 10. val ahora es 11.
            // 2. --val: val es 11. --val se aplica a val, val ahora es 10. Devuelve 10.
            // 3. Operación: res = 10 (de val++) * 2 + 10 (de --val)
            //             res = 20 + 10 = 30.
            // Estado final: res=30, val=10.
            res = val++ * 2 + --val;
            print res; // 30
            print val; // 10
        }
        """
        _, out = self.get_ir(code)
        self.assertEqual(out, "3010")
        self.assertEqual(out, "3010")

    # --- Test de Inc/Dec con Literales y Expresiones (Solo Integer Válidos) ---

    def test_literal(self):
        code = """
        main: function void () = {
            print 5++; // Imprime 5
            print ++5; // Imprime 6
            print 5--; // Imprime 5
            print --5; // Imprime 4
        }
        """
        _, out = self.get_ir(code)
        self.assertEqual(out, "5654")
