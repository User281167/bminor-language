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

    def test_global_int(self):
        gen, _ = self.get_ir("x: integer;")

        x = gen.get_global("x")
        self.assertEqual(x.name, "x")

        code = str(gen)
        self.assertIn('@"x" = dso_local global i32 0, align 4', code)

    def test_global_float(self):
        gen, _ = self.get_ir("x: float;")

        x = gen.get_global("x")
        self.assertEqual(x.name, "x")

        code = str(gen)
        self.assertIn('@"x" = dso_local global float', code)
        self.assertIn("0x0, align 4", code)

    def test_global_char(self):
        gen, _ = self.get_ir("x: char;")

        x = gen.get_global("x")
        self.assertEqual(x.name, "x")

        code = str(gen)
        self.assertIn('@"x" = dso_local global i8 0, align 1', code)
