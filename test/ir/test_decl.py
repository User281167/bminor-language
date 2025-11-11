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
        self.assertIn('@"x" = dso_local global i32 0, align 4', code)
        self.assertIn('@"y" = dso_local global float', code)
        self.assertIn('@"z" = dso_local global i8 0, align 1', code)
        self.assertIn('@"b" = dso_local global i1 0, align 1', code)

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

        self.assertIn('@"x" = dso_local global i32 1, align 4', code)
        self.assertIn('@"y" = dso_local global float', code)
        self.assertIn('@"z" = dso_local global i8 97, align 1', code)
        self.assertIn('@"w" = dso_local global i8 10, align 1', code)
        self.assertIn('@"b" = dso_local global i1 1, align 1', code)

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
        self.assertIn('@"x" = dso_local global i32 1, align 4', code)
        self.assertIn('@"y" = dso_local global float', code)
        self.assertIn('@"z" = dso_local global i8 97, align 1', code)
        self.assertIn('@"w" = dso_local global i8 10, align 1', code)
        self.assertIn('@"b" = dso_local global i1 0, align 1', code)

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

        self.assertIn('@"x" = dso_local global i32 1, align 4', code)
        self.assertIn('@"y" = dso_local global float', code)
        self.assertIn('@"z" = dso_local global i8 97, align 1', code)
        self.assertIn('@"w" = dso_local global i8 10, align 1', code)
        self.assertIn('@"b" = dso_local global i1 0, align 1', code)

    def test_global_literal_expr(self):
        gen, _ = self.get_ir(
            """
            x: integer = 1 + 2 / 30 * 10; // 1
            y: constant = -1.0 + 2.0;
            b: boolean = true && false;
            """
        )

        code = str(gen)

        self.assertIn('@"x" = dso_local global i32 1, align 4', code)
        self.assertIn('@"y" = dso_local global float', code)
        self.assertIn('@"b" = dso_local global i1 0, align 1', code)
