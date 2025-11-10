import unittest
from parser.model import *

from ir import IRGenerator, run_llvm_ir
from utils import clear_errors, errors_detected


class TestBasicDecl(unittest.TestCase):
    def setUp(self):
        clear_errors()

    def get_ir(self, code, run=False):
        gen = IRGenerator().generate_from_code(code)
        out = ""
        self.assertFalse(errors_detected())

        if run:
            out = run_llvm_ir(str(gen))

        return gen, out

    def test_global_basic(self):
        gen, _ = self.get_ir("x: integer; y: float; z: char; b: boolean;")

        # Verifica que las variables están en el entorno
        code = str(gen)

        # Verifica que las variables están alocadas en run()
        self.assertIn('%"x" = alloca i32, align 4', code)
        self.assertIn('store i32 0, i32* %"x"', code)
        self.assertIn('%"y" = alloca float, align 4', code)
        self.assertIn("store float", code)
        self.assertIn('0x0, float* %"y"', code)
        self.assertIn('%"z" = alloca i8, align 1', code)
        self.assertIn('store i8 0, i8* %"z"', code)
        self.assertIn('%"b" = alloca i1, align 1', code)
        self.assertIn('store i1 0, i1* %"b"', code)

    def test_global_basic_value(self):
        gen, _ = self.get_ir(
            """
            x: integer = 1;
            y: float = 1.0;
            z: char = 'a';
            w: char = '\\n';
            b: boolean = true;
            """
        )

        code = str(gen)

        self.assertIn('%"x" = alloca i32, align 4', code)
        self.assertIn('store i32 1, i32* %"x"', code)

        self.assertIn('%"y" = alloca float, align 4', code)
        self.assertIn('store float 0x3ff0000000000000, float* %"y"', code)

        self.assertIn('%"z" = alloca i8, align 1', code)
        self.assertIn('store i8 97, i8* %"z"', code)

        self.assertIn('%"w" = alloca i8, align 1', code)
        self.assertIn('store i8 10, i8* %"w"', code)

        self.assertIn('%"b" = alloca i1, align 1', code)
        self.assertIn('store i1 true, i1* %"b"', code)

    def test_global_basic_auto(self):
        gen, _ = self.get_ir(
            """
            x: auto = 1;
            y: auto = 1.0;
            z: auto = 'a';
            w: auto = '\\n';
            b: auto = false;
            """
        )

        code = str(gen)

        self.assertIn('%"x" = alloca i32, align 4', code)
        self.assertIn('store i32 1, i32* %"x"', code)

        self.assertIn('%"y" = alloca float, align 4', code)
        self.assertIn('store float 0x3ff0000000000000, float* %"y"', code)

        self.assertIn('%"z" = alloca i8, align 1', code)
        self.assertIn('store i8 97, i8* %"z"', code)

        self.assertIn('%"w" = alloca i8, align 1', code)
        self.assertIn('store i8 10, i8* %"w"', code)

        self.assertIn('%"b" = alloca i1, align 1', code)
        self.assertIn('store i1 false, i1* %"b"', code)

    def test_global_constant(self):
        gen, _ = self.get_ir(
            """
            x: constant = 1;
            y: constant = 1.0;
            z: constant = 'a';
            w: constant = '\\n';
            b: constant = false;
            """
        )

        code = str(gen)

        self.assertIn('%"x" = alloca i32, align 4', code)
        self.assertIn('store i32 1, i32* %"x"', code)

        self.assertIn('%"y" = alloca float, align 4', code)
        self.assertIn('store float 0x3ff0000000000000, float* %"y"', code)

        self.assertIn('%"z" = alloca i8, align 1', code)
        self.assertIn('store i8 97, i8* %"z"', code)

        self.assertIn('%"w" = alloca i8, align 1', code)
        self.assertIn('store i8 10, i8* %"w"', code)

        self.assertIn('%"b" = alloca i1, align 1', code)
        self.assertIn('store i1 false, i1* %"b"', code)

    def test_global_literal_expr(self):
        gen, _ = self.get_ir(
            """
            x: integer = 1 + 2 / 30 * 10; // 1
            y: constant = -1.0 + 2.0;
            b: boolean = true && false;
            """
        )

        code = str(gen)

        self.assertIn('%"x" = alloca i32, align 4', code)
        self.assertIn('store i32 1, i32* %"x"', code)

        self.assertIn('%"y" = alloca float, align 4', code)
        self.assertIn('store float 0x3ff0000000000000, float* %"y"', code)

        self.assertIn('%"b" = alloca i1, align 1', code)
        self.assertIn('store i1 false, i1* %"b"', code)

    def test_copy_auto(self):
        gen, _ = self.get_ir("x: auto = 'a'; y: auto = x;")

        code = str(gen)

        self.assertIn('%"x" = alloca i8, align 1', code)
        self.assertIn('store i8 97, i8* %"x"', code)
        self.assertIn('%"y" = alloca i8, align 1', code)

        import re

        match = re.search(r'store i8 %"(.*?)\.1", i8\* %"y"', code)
        self.assertIsNotNone(match)
