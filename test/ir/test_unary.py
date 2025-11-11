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

    def test_int(self):
        code = """
            x: integer = 1;
            x2: integer = -x;
            x3: integer = +x;
            x4: integer = -+x;

            main: function void () = {
                print x, x2, x3, x4;
            }
            """

        gen, out = self.get_ir(code)
        self.assertIn("1-11-1", out)

    def test_float(self):
        code = """
            y1: float = 1.0;
            y2: float = -y1;
            y3: float = +y1;
            y4: float = +-y1;

            main: function void () = {
                print y1, y2, y3, y4;
            }
            """

        gen, out = self.get_ir(code)
        self.assertIn("1.000000-1.0000001.000000-1.000000", out)

    def test_bool(self):
        code = """
            x1: boolean = true;
            x2: boolean = !x1;
            x3: boolean = !!x1;

            main: function void () = {
                print x1, x2, x3;
            }
            """

        gen, out = self.get_ir(code)
        self.assertIn("truefalsetrue", out)
