import unittest
from parser.model import *

from ir import IRGenerator, run_llvm_clang_ir
from utils import clear_errors, errors_detected


class TestFunctions(unittest.TestCase):
    def setUp(self):
        clear_errors()

    def get_ir(self, code):
        gen = IRGenerator().generate_from_code(code)
        out = ""
        self.assertFalse(
            errors_detected(), "Errores detectados durante la generación de IR"
        )

        try:
            out = run_llvm_clang_ir(str(gen), add_runtime=True)
            out = out.strip()
        except Exception as e:
            print(f"Error al ejecutar LLVM/Clang IR: {e}")
            print("--- LLVM IR ---")
            print(str(gen))
            print("---------------")
            self.fail(f"La ejecución del IR falló: {e}")

        return gen, out

    def test_function_call_basic(self):
        code = """
        f: function void() = {
            print 42;
        }

        main: function void() = {
            f();
        }
        """
        _, out = self.get_ir(code)
        self.assertEqual(out, "42")

    def test_function_call_with_argument(self):
        code = """
        f: function void(x: integer) = {
            print x;
        }

        main: function void() = {
            f(100);
        }
        """
        _, out = self.get_ir(code)
        self.assertEqual(out, "100")

    def test_function_call_with_return(self):
        code = """
        f: function integer(x: integer) = {
            return x + 1;
        }

        main: function void() = {
            print f(100);
        }
        """
        _, out = self.get_ir(code)
        self.assertEqual(out, "101")

    # def test_function_nested(self):
    #     code = """
    #     f: function void() = {
    #         f: function void() = {
    #             print 42;
    #         }

    #         f();

    #         print 100;
    #     }

    #     main: function void() = {
    #         f();
    #     }
    #     """
    #     _, out = self.get_ir(code)
    #     self.assertEqual(out, "42100")

    def test_function_recursive(self):
        code = """
        f: function integer(x: integer) = {
            if (x == 0) {
                return 0;
            } else {
                return x + f(x - 1);
            }
        }

        main: function void() = {
            print f(5);
        }
        """
        _, out = self.get_ir(code)
        self.assertEqual(out, "15")

    def test_function_with_if(self):
        code = """
        f: function void(x: integer) = {
            if (x > 0) {
                print x;
            }
        }

        main: function void() = {
            f(10);
        }
        """
        _, out = self.get_ir(code)
        self.assertEqual(out, "10")

    def test_function_with_loop(self):
        code = """
        f: function void() = {
            i: integer;
            for (i = 0; i < 5; i++) {
                print i;
            }
        }

        main: function void() = {
            f();
        }
        """
        _, out = self.get_ir(code)
        self.assertEqual(out, "01234")

    def test_function_call_multiple_arguments(self):
        code = """
        f: function void(x: integer, y: integer, z: integer) = {
            print x;
            print y;
            print z;
        }

        main: function void() = {
            f(1, 2, 3);
        }
        """
        _, out = self.get_ir(code)
        self.assertEqual(out, "123")

    def test_function_mutual_recursion(self):
        code = """
        g: function integer(x: integer);

        f: function integer(x: integer) = {
            if (x == 0) {
                return 0;
            } else {
                return x + g(x - 1);
            }
        }

        g: function integer(x: integer) = {
            if (x == 0) {
                return 0;
            } else {
                return x + f(x - 1);
            }
        }

        main: function void() = {
            print f(3);
        }
        """
        _, out = self.get_ir(code)
        self.assertEqual(out, "6")

    def test_function_local_variable(self):
        code = """
        f: function integer(x: integer) = {
            y: integer = 10;
            return x + y;
        }
        main: function void() = {
            print f(5);
        }
        """
        _, out = self.get_ir(code)
        self.assertEqual(out, "15")

    def test_function_call_no_parameters(self):
        code = """
            f: function void() = {
                print 42;
            }

            main: function void() = {
                f();
            }
            """
        _, out = self.get_ir(code)
        self.assertEqual(out, "42")

    def test_function_call_integer_parameter(self):
        code = """
        f: function void(x: integer) = {
            print x;
        }

        main: function void() = {
            f(100);
        }
        """
        _, out = self.get_ir(code)
        self.assertEqual(out, "100")

    def test_function_call_float_parameter(self):
        code = """
        f: function void(x: float) = {
            print x;
        }

        main: function void() = {
            f(3.14);
        }
        """
        _, out = self.get_ir(code)
        self.assertAlmostEqual(float(out), 3.14, places=5)

    def test_function_call_char_parameter(self):
        code = """
        f: function void(x: char) = {
            print x;
        }

        main: function void() = {
            f('A');
        }
        """
        _, out = self.get_ir(code)
        self.assertEqual(out, "A")

    def test_function_call_boolean_parameter(self):
        code = """
        f: function void(x: boolean) = {
            print x;
        }

        main: function void() = {
            f(true);
        }
        """
        _, out = self.get_ir(code)
        self.assertEqual(out, "true")

    def test_function_call_multiple_parameters(self):
        code = """
        f: function void(x: integer, y: float, z: char) = {
            print x;
            print '\\n';
            print y;
            print '\\n';
            print z;
        }

        main: function void() = {
            f(10, 2.71, 'B');
        }
        """
        _, out = self.get_ir(code)

        lines = out.split("\n")
        self.assertEqual(lines[0], "10")
        self.assertAlmostEqual(float(lines[1]), 2.71, places=5)
        self.assertEqual(lines[2], "B")

    def test_function_call_return_integer(self):
        code = """
        f: function integer(x: integer) = {
            return x + 1;
        }

        main: function void() = {
            print f(100);
        }
        """
        _, out = self.get_ir(code)
        self.assertEqual(out, "101")

    def test_function_call_return_float(self):
        code = """
        f: function float(x: float) = {
            return x * 2.0;
        }

        main: function void() = {
            print f(2.5);
        }
        """
        _, out = self.get_ir(code)
        val = float(out)
        self.assertAlmostEqual(val, 5.0, places=5)

    def test_function_call_return_char(self):
        code = """
        f: function char(x: char) = {
            return x;
        }

        main: function void() = {
            print f('Z');
        }
        """
        _, out = self.get_ir(code)
        self.assertEqual(out, "Z")

    def test_function_call_return_boolean(self):
        code = """
        f: function boolean(x: boolean) = {
            return x;
        }

        main: function void() = {
            print f(false);
        }
        """
        _, out = self.get_ir(code)
        self.assertEqual(out, "false")

    # def test_function_nested(self):
    #     code = """
    #     f: function void() = {
    #         f: function void() = {
    #             print 42;
    #         }

    #         f();

    #         print 100;
    #     }

    #     main: function void() = {
    #         f();
    #     }
    #     """
    #     _, out = self.get_ir(code)
    #     self.assertEqual(out, "42100")

    # def test_function_nested_if(self):
    #     code = """
    #     f: function void() = {
    #         f: function void() = {
    #             if (true) {
    #                 f: function void() = {
    #                     print 84;
    #                 }

    #                 f();
    #             }

    #             print 42;
    #         }

    #         f();

    #         print 100;
    #     }

    #     main: function void() = {
    #         f();
    #     }
    #     """
    #     _, out = self.get_ir(code)
    #     self.assertEqual(out, "8442100")

    # def test_function_nested_if_else(self):
    #     code = """
    #     f: function void() = {
    #         f: function void() = {
    #             if (false) {
    #                 f: function void() = {
    #                     print 84;
    #                 }

    #                 f();
    #             } else {
    #                 f: function void() = {
    #                     print 21;
    #                 }

    #                 f();
    #             }

    #             print 42;
    #         }

    #         f();

    #         print 100;
    #     }

    #     main: function void() = {
    #         f();
    #     }
    #     """
    #     _, out = self.get_ir(code)
    #     self.assertEqual(out, "2142100")

    # def test_function_nested_for(self):
    #     code = """
    #     f: function void() = {
    #         i: integer;

    #         for (i = 0; i < 3; i++) {
    #             f: function void() = {
    #                 print '-';
    #             }

    #             f();
    #         }

    #         print 100;
    #     }

    #     main: function void() = {
    #         f();
    #     }
    #     """
    #     _, out = self.get_ir(code)
    #     self.assertEqual(out, "---100")

    # def test_function_nested_while(self):
    #     code = """
    #     f: function void() = {
    #         i: integer = 0;

    #         while (i < 3) {
    #             f: function void() = {
    #                 print '-';
    #             }

    #             f();
    #             i = i + 1;
    #         }

    #         print 100;
    #     }

    #     main: function void() = {
    #         f();
    #     }
    #     """
    #     _, out = self.get_ir(code)
    #     self.assertEqual(out, "---100")

    # def test_function_nested_do_while(self):
    #     code = """
    #     f: function void() = {
    #         i: integer = 0;

    #         do {
    #             f: function void() = {
    #                 print '-';
    #             }

    #             f();
    #             i = i + 1;
    #         } while (i < 3);

    #         print 100;
    #     }

    #     main: function void() = {
    #         f();
    #     }
    #     """
    #     _, out = self.get_ir(code)
    #     self.assertEqual(out, "---100")

    def test_function_recursive(self):
        code = """
        f: function integer(x: integer) = {
            if (x == 0) {
                return 0;
            } else {
                return x + f(x - 1);
            }
        }

        main: function void() = {
            print f(5);
        }
        """
        _, out = self.get_ir(code)
        self.assertEqual(out, "15")

    def test_function_with_if(self):
        code = """
        f: function void(x: integer) = {
            if (x > 0) {
                print x;
            }
        }

        main: function void() = {
            f(10);
        }
        """
        _, out = self.get_ir(code)
        self.assertEqual(out, "10")

    def test_function_with_loop(self):
        code = """
        f: function void() = {
            i: integer;
            for (i = 0; i < 5; i++) {
                print i;
            }
        }

        main: function void() = {
            f();
        }
        """
        _, out = self.get_ir(code)
        self.assertEqual(out, "01234")

    def test_function_mutual_recursion(self):
        code = """
        g: function integer(x: integer);

        f: function integer(x: integer) = {
            if (x == 0) {
                return 0;
            } else {
                return x + g(x - 1);
            }
        }

        g: function integer(x: integer) = {
            if (x == 0) {
                return 0;
            } else {
                return x + f(x - 1);
            }
        }

        main: function void() = {
            print f(3);
        }
        """
        _, out = self.get_ir(code)
        self.assertEqual(out, "6")

    def test_function_local_variable(self):
        code = """
        f: function integer(x: integer) = {
            y: integer = 10;
            return x + y;
        }
        main: function void() = {
            print f(5);
        }
        """
        _, out = self.get_ir(code)
        self.assertEqual(out, "15")
