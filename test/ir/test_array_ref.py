import unittest
from parser.model import *

from ir import IRGenerator, run_llvm_clang_ir
from utils import clear_errors, errors_detected


class TestArrayRef(unittest.TestCase):
    def setUp(self):
        clear_errors()

    def get_ir_and_output(self, code):
        """Helper para generar IR y ejecutar."""
        ir_generator = IRGenerator()
        generated_ir = ir_generator.generate_from_code(code)

        self.assertFalse(
            errors_detected(),
            "Errores semánticos detectados durante la generación de IR",
        )

        output = ""
        try:
            output = run_llvm_clang_ir(str(generated_ir), add_runtime=True)
            output = output.strip()
        except Exception as e:
            print(f"Error al ejecutar LLVM/Clang IR: {e}")
            print("--- LLVM IR Generado ---")
            print(str(generated_ir))
            print("------------------------")
            self.fail(f"La ejecución del IR falló: {e}")

        return generated_ir, output

    def test_basic_decref(self):
        code = """
        arr: array[1] integer;
        """
        expected_output = ""
        gen, output = self.get_ir_and_output(code)
        self.assertEqual(output, expected_output)

        gen = str(gen)
        decref = gen.count('call void @"_bminor_array_decref"')
        self.assertEqual(decref, 1)

    def test_basic_incref(self):
        code = """
        arr1: array[1] integer;
        arr2: array[1] integer;
        arr2 = arr1;
        """
        expected_output = ""
        gen, output = self.get_ir_and_output(code)
        self.assertEqual(output, expected_output)

        # 2 copy (1 en declaración y 1 en asignación)
        # 4 decref (2 en declaración y 1 en asignación, 1 asignación previa a arr2)
        gen = str(gen)
        incref = gen.count('call void @"_bminor_array_incref"')
        self.assertEqual(incref, 1)

        decref = gen.count('call void @"_bminor_array_decref"')
        self.assertEqual(decref, 4)

    def test_inc_dec_func_arg(self):
        code = """
        foo: function void(a: array[1] integer) = {
        }

        arr: array[1] integer;
        foo(arr);
        """
        expected_output = ""
        gen, output = self.get_ir_and_output(code)
        self.assertEqual(output, expected_output)

        gen = str(gen)
        incref = gen.count('call void @"_bminor_array_incref"')
        self.assertEqual(incref, 1)  # como arg de función

        decref = gen.count('call void @"_bminor_array_decref"')
        self.assertEqual(decref, 2)  # 1 en llamada y 1 al final del main

    def test_inc_dec_return(self):
        code = """
        foo: function array[1] integer() = {
            r: array[1] integer;
            return r;
        }

        arr: array[1] integer;
        arr = foo();
        """
        expected_output = ""
        gen, output = self.get_ir_and_output(code)
        self.assertEqual(output, expected_output)

        gen = str(gen)
        incref = gen.count('call void @"_bminor_array_incref"')
        self.assertEqual(incref, 1)  # en el return

        decref = gen.count('call void @"_bminor_array_decref"')
        # 4 decref (1 en el return, 1 en la asignación y 2 al final del main -> declaración arr y llamada de foo)
        self.assertEqual(decref, 4)

    def test_array_automatic_free(self):
        code = """
        foo: function array[1] integer() = {
            r: array[1] integer;
            return r;
        }

        val: auto = foo();
        """
        expected_output = ""
        gen, output = self.get_ir_and_output(code)
        self.assertEqual(output, expected_output)

        gen = str(gen)
        decref = gen.count('call void @"_bminor_array_decref"')
        # 1 al salir de foo, 1 en la declaración y 1 al final del main
        self.assertEqual(decref, 3)

    def test_multiple_inc_dec(self):
        code = """
        foo: function array[1] integer(a: array[1] integer) = {
            return a;
        }

        set_first: function void(a: array[1] integer) = {
            a[0] = 42;
        }

        arr: array[1] integer;
        set_first(arr);

        arr2: auto = arr;
        arr2[0] = 1;

        arr = arr2;

        arr3: auto = foo(arr);

        print arr3[0];
        """
        expected_output = "1"
        gen, output = self.get_ir_and_output(code)
        self.assertEqual(output, expected_output)

        gen = str(gen)
        incref = gen.count('call void @"_bminor_array_incref"')
        self.assertEqual(incref, 5)

        decref = gen.count('call void @"_bminor_array_decref"')
        # 1 return
        # 1 set_first arg
        # 1 asignación arr2
        # 1 asignación arr
        # 1 foo arg
        # 1 arr3 decl
        # 1 al final del main (arr)
        # 1 al final del main (arr2)
        # 1 al final del main (arr3)
        self.assertEqual(decref, 9)

    def test_inc_dec_literal(self):
        code = """
        make_floats: function array [2] float () = {
            f: array [2] float = {1.1, 2.2};
            return f;
        }

        sum_floats: function float (arr: array [2] float) = {
            return arr[0] + arr[1];
        }

        main: function void () = {
            res: float = sum_floats(make_floats());
        }
        """
        expected_output = ""
        gen, output = self.get_ir_and_output(code)
        self.assertEqual(output, expected_output)

        gen = str(gen)
        incref = gen.count('call void @"_bminor_array_incref"')
        self.assertEqual(incref, 2)  # return, arg

        decref = gen.count('call void @"_bminor_array_decref"')
        self.assertEqual(decref, 3)  # return, arg, arr literal
