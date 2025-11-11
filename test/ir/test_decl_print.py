import unittest
from parser.model import *

from ir import IRGenerator, run_llvm_clang_ir
from utils import clear_errors, errors_detected


class TestDecl(unittest.TestCase):
    def setUp(self):
        clear_errors()

    def get_ir(self, code):
        gen = IRGenerator().generate_from_code(code)
        out = ""
        self.assertFalse(errors_detected())

        try:
            out = run_llvm_clang_ir(str(gen), add_runtime=True)
        except Exception as e:
            print(e)

        return gen, out

    def test_basic_val(self):
        code = """
            main: function void () = {
                print 1, .10, 'A', true, false;
            }
        """

        gen, out = self.get_ir(code)

        self.assertIn("1", out)
        self.assertIn("0.1", out)
        self.assertIn("A", out)
        self.assertIn("true", out)
        self.assertIn("false", out)

    def test_basic_decl(self):
        code = """
            x1: integer;
            x2: integer = 1 + 110;
            y1: float;
            y2: float = 1.1;
            z1: char;
            z2: char = 'A';
            b1: boolean;
            b2: boolean = true;

            main: function void () = {
                print x1, x2, y1, y2, z1, z2, b1, b2;
            }
            """

        gen, out = self.get_ir(code)

        self.assertIn("0", out)
        self.assertIn("110", out)
        self.assertIn("0.000000", out)
        self.assertIn("1.100000", out)
        self.assertIn("A", out)
        self.assertIn("A", out)
        self.assertIn("false", out)
        self.assertIn("true", out)
