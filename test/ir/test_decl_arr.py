import unittest
from parser.model import *

from ir import IRGenerator, run_llvm_ir
from utils import clear_errors, errors_detected


class TestArrayDecl(unittest.TestCase):
    def setUp(self):
        clear_errors()

    def get_ir(self, code, run=False):
        gen = IRGenerator().generate_from_code(code)
        out = ""
        self.assertFalse(errors_detected())

        if run:
            out = run_llvm_ir(str(gen))

        return gen, out

    def test_array_int(self):
        codes = [
            "x: array [1] integer;",
            "x: array [1] float;",
            "x: array [1] char;",
            "x: array [1] boolean;",
        ]

        types = ["i32", "float", "i8", "i1"]

        for c, t in zip(codes, types):
            gen, _ = self.get_ir(c)

            # Verifica que las variables están en el entorno
            code = str(gen)
            arr_t = "{i32, " + t + "*}"

            # Verifica que las variables están alocadas en run()
            self.assertIn(f'%"x.data" = alloca [1 x {t}]', code)
            self.assertIn(f'%"x" = alloca {arr_t}', code)

            self.assertIn(
                f'%"x.size_ptr" = getelementptr {arr_t}, {arr_t}* %"x", i32 0, i32 0',
                code,
            )
            self.assertIn(f'store i32 1, i32* %"x.size_ptr"', code)
            self.assertIn(
                f'%"x.data_ptr" = getelementptr {arr_t}, {arr_t}* %"x", i32 0, i32 1',
                code,
            )

            import re

            # self.assertIn(f'%".5" = bitcast [1 x {t}]* %"x.data" to {t}*', code)
            # match = re.search(
            #     f'%"(.*)" = bitcast [1 x {t}]\\* %"x.data" to {t}\\*', code
            # )
            # self.assertIsNotNone(match)
            # self.assertIn(f'store {t}* %".5", {t}** %"x.data_ptr"', code)

    def test_array_init(self):
        gen, _ = self.get_ir(
            """
            x: array [2] integer = {100, 200};
            """
        )

        # Verifica que las variables están en el entorno
        code = str(gen)

        # Verifica que las variables están alocadas en run()
        self.assertIn('store [2 x i32] [i32 100, i32 200], [2 x i32]* %"x.data"', code)

    def test_array_var(self):
        gen, _ = self.get_ir(
            """
            n: integer;
            x: array [n] integer = {100, 200};
            """
        )

        # Verifica que las variables están en el entorno
        code = str(gen)

        import re

        # llvm puede usar cualquier puntero temporal para cargar n
        found = False

        for line in code.split("\n"):
            if "store i32 %" in line and "x.size_ptr" in line:
                found = True
                break

        self.assertTrue(found)

        # Verifica que las variables está alocadas en run()
        self.assertIn('store [2 x i32] [i32 100, i32 200], [2 x i32]* %"x.data"', code)
