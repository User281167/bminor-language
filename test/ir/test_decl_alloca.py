import unittest
from parser.model import *

from ir import IRGenerator, run_llvm_ir
from utils import clear_errors, errors_detected


class TestDecl(unittest.TestCase):
    def setUp(self):
        clear_errors()

    def get_ir(self, code, run=False):
        gen = IRGenerator().generate_from_code(code)
        out = ""
        self.assertFalse(errors_detected())

        if run:
            out = run_llvm_ir(str(gen))

        return gen, out

    def test_copy(self):
        gen, _ = self.get_ir("x: integer; y: integer = x;")

        x = gen.get_global("x")
        self.assertEqual(x.name, "x")

        y = gen.get_global("y")
        self.assertEqual(y.name, "y")

        code = str(gen)
        self.assertIn('@"x" = dso_local global i32 0, align 4', code)
        self.assertIn('@"y" = dso_local global i32 0, align 4', code)

        self.assertIn('%"x" = load i32, i32* @"x"', code)

    def test_copy_auto(self):
        gen, _ = self.get_ir("x: auto = 'a'; y: auto = x;")

        x = gen.get_global("x")
        self.assertEqual(x.name, "x")

        y = gen.get_global("y")
        self.assertEqual(y.name, "y")

        code = str(gen)
        self.assertIn('@"x" = dso_local global i8 97, align 1', code)
        self.assertIn('@"y" = dso_local global i8 0, align 1', code)

        self.assertIn('%"x" = load i8, i8* @"x"', code)
        self.assertIn('store i8 %"x", i8* @"y"', code)
