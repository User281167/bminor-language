import unittest
from parser.model import *

from ir import IRGenerator, run_llvm_ir
from utils import clear_errors


class TestBasicDecl(unittest.TestCase):
    def setUp(self):
        clear_errors()

    def get_ir(self, code, run=False):
        gen = IRGenerator().generate_from_code(code)
        out = ""

        if run:
            out = run_llvm_ir(str(gen))

        return gen, out

    def test_global_basic(self):
        gen, _ = self.get_ir("x: integer; y: float; z: char;")

        x = gen.get_global("x")
        self.assertEqual(x.name, "x")

        y = gen.get_global("y")
        self.assertEqual(y.name, "y")

        z = gen.get_global("z")
        self.assertEqual(z.name, "z")

        code = str(gen)
        self.assertIn('@"x" = dso_local global i32 0, align 4', code)

        self.assertIn('@"y" = dso_local global float', code)
        self.assertIn("0x0, align 4", code)

        self.assertIn('@"z" = dso_local global i8 0, align 1', code)

    def test_global_basic_value(self):
        gen, _ = self.get_ir(
            """
            x: integer = 1;
            y: float = 1.0;
            z: char = 'a';
            w: char = '\\n';
            """
        )

        x = gen.get_global("x")
        self.assertEqual(x.name, "x")

        y = gen.get_global("y")
        self.assertEqual(y.name, "y")

        z = gen.get_global("z")
        self.assertEqual(z.name, "z")

        code = str(gen)
        self.assertIn('@"x" = dso_local global i32 1, align 4', code)

        self.assertIn('@"y" = dso_local global float 0x3ff0000000000000, align 4', code)

        self.assertIn('@"z" = dso_local global i8 97, align 1', code)
        self.assertIn('@"w" = dso_local global i8 10, align 1', code)
