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

    def test_array_basic(self):
        gen, _ = self.get_ir(
            """
            x: array [1] integer;
            y: array [2] float;
            z: array [3] char;
            b: array [4] boolean;
            """
        )

        # Verifica que las variables están en el entorno
        code = str(gen)

        # Verifica que las variables están alocadas en run()
        self.assertIn('%"x" = alloca [1 x i32]', code)
        self.assertIn('%"y" = alloca [2 x float]', code)
        self.assertIn('%"z" = alloca [3 x i8]', code)
        self.assertIn('%"b" = alloca [4 x i1]', code)

    def test_array_basic_val(self):
        gen, _ = self.get_ir(
            """
            x: array [1] integer = {1};
            y: array [2] float = {1.0, 2.0};
            z: array [3] char = {'a', 'b', 'c'};
            b: array [4] boolean = {true, false, true, false};
            """
        )

        # Verifica que las variables están en el entorno
        code = str(gen)

        # Verifica que las variables están alocadas en run()
        self.assertIn('%"x" = alloca [1 x i32]', code)
        self.assertIn('%"y" = alloca [2 x float]', code)
        self.assertIn('%"z" = alloca [3 x i8]', code)
        self.assertIn('%"b" = alloca [4 x i1]', code)

        self.assertIn('store [1 x i32] [i32 1], [1 x i32]* %"x"', code)
        self.assertIn(
            'store [2 x float] [float 0x3ff0000000000000, float 0x4000000000000000], [2 x float]* %"y"',
            code,
        )
        self.assertIn('store [3 x i8] [i8 97, i8 98, i8 99], [3 x i8]* %"z"', code)
        self.assertIn(
            'store [4 x i1] [i1 true, i1 false, i1 true, i1 false], [4 x i1]* %"b"',
            code,
        )
