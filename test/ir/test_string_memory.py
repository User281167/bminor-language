import unittest
from parser.model import *

from ir import IRGenerator, run_llvm_clang_ir
from utils import clear_errors, errors_detected


class TestStringMemory(unittest.TestCase):
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
            # print(str(generated_ir))
            print("------------------------")
            self.fail(f"La ejecución del IR falló: {e}")

        return generated_ir, output

    def test_literal(self):
        """
        No crea copia del string
        No llama a runtime copy o free
        """
        code = """
        print "Hello, World!";
        """
        expected_output = "Hello, World!"
        gen, output = self.get_ir_and_output(code)
        self.assertEqual(output, expected_output)

        gen = str(gen)
        copies = gen.count('call i8* @"_bminor_string_copy"')
        frees = gen.count('call void @"_bminor_string_free"')

        self.assertEqual(
            copies,
            0,
            "No se esperaba copias de strings en el IR generado.",
        )
        self.assertEqual(
            frees,
            0,
            "No se esperaba frees de strings en el IR generado.",
        )

    def test_string_copy_and_free(self):
        """
        Crea copia del string
        Llama a runtime copy y free
        """
        code = """
        s: string = "Hello, World!";
        print s;
        """
        expected_output = "Hello, World!"
        gen, output = self.get_ir_and_output(code)
        self.assertEqual(output, expected_output)

        gen = str(gen)
        copies = gen.count('call i8* @"_bminor_string_copy"')
        frees = gen.count('call void @"_bminor_string_free"')

        self.assertEqual(
            copies,
            1,
            "Se esperaba una copia de string en el IR generado.",
        )
        self.assertEqual(
            frees,
            1,
            "Se esperaba un free de string en el IR generado.",
        )

    def test_copy_literal_in_fun_call(self):
        """
        Pasa literal a función
        Crea copia del string
        Llama a runtime copy y free
        """
        code = """
        print_string: function void(s: string) = {
            print s;
        }

        print_string("Hello, World!");
        """
        expected_output = "Hello, World!"
        gen, output = self.get_ir_and_output(code)
        self.assertEqual(output, expected_output)

        gen = str(gen)
        copies = gen.count('call i8* @"_bminor_string_copy"')
        frees = gen.count('call void @"_bminor_string_free"')

        self.assertEqual(
            copies,
            1,
            "Se esperaba una copia de string en el IR generado.",
        )
        self.assertEqual(
            frees,
            1,
            "Se esperaba un free de string en el IR generado.",
        )

    def test_assignment_null(self):
        """
        Asigna string a variable
        Crea copia del string
        Llama a runtime copy y free
        """
        code = """
        s1: string;
        s2: string;
        """
        gen, _ = self.get_ir_and_output(code)

        # 2 copy y 2 free
        # 2 copy de null \0
        gen = str(gen)
        copies = gen.count('call i8* @"_bminor_string_copy"')
        frees = gen.count('call void @"_bminor_string_free"')
        self.assertEqual(
            copies,
            2,
            f"Se esperaban 2 llamadas a _bminor_string_copy, se encontraron {copies}.",
        )
        self.assertEqual(
            frees,
            2,
            f"Se esperaban 2 llamadas a _bminor_string_free, se encontraron {frees}.",
        )

    def test_assignment(self):
        """
        Asigna string a variable
        Crea copia del string
        Llama a runtime copy y free
        """
        code = """
        s1: string = "Hello, ";
        s2: string = "World!";
        print s1, s2;
        """
        expected_output = "Hello, World!"
        gen, output = self.get_ir_and_output(code)
        self.assertEqual(output, expected_output)

        # 2 copy y 2 free
        gen = str(gen)
        copies = gen.count('call i8* @"_bminor_string_copy"')
        frees = gen.count('call void @"_bminor_string_free"')
        self.assertEqual(
            copies,
            2,
            f"Se esperaban 2 llamadas a _bminor_string_copy, se encontraron {copies}.",
        )
        self.assertEqual(
            frees,
            2,
            f"Se esperaban 2 llamadas a _bminor_string_free, se encontraron {frees}.",
        )

    def test_concat(self):
        """
        Concatena strings
        Crea copias de los strings
        Llama a runtime copy y free
        """
        code = """
        s1: string = "Hello, ";
        s2: string = "World!";
        s3: string;
        s3 = s1 + s2;
        print s3;
        """
        expected_output = "Hello, World!"
        gen, output = self.get_ir_and_output(code)
        self.assertEqual(output, expected_output)

        # 3 copy y 4 free incluye old s3
        gen = str(gen)
        copies = gen.count('call i8* @"_bminor_string_copy"')
        frees = gen.count('call void @"_bminor_string_free"')
        self.assertEqual(
            copies,
            3,
            f"Se esperaban 3 llamadas a _bminor_string_copy, se encontraron {copies}.",
        )
        self.assertEqual(
            frees,
            4,
            f"Se esperaban 4 llamadas a _bminor_string_free, se encontraron {frees}.",
        )

    def test_string_var_param(self):
        """
        Pasa variable string a función
        No Crea copia del string
        """
        code = """
        print_string: function void(s: string) = {
            print s;
        }

        s: string = "Hello, World!";
        print_string(s);
        """
        expected_output = "Hello, World!"
        gen, output = self.get_ir_and_output(code)
        self.assertEqual(output, expected_output)

        gen = str(gen)
        copies = gen.count('call i8* @"_bminor_string_copy"')
        self.assertEqual(
            copies,
            1,
            f"Se esperaban 1 llamada a _bminor_string_copy, se encontraron {copies}.",
        )
        frees = gen.count('call void @"_bminor_string_free"')
        self.assertEqual(
            frees,
            1,
            f"Se esperaban 1 llamada a _bminor_string_free, se encontraron {frees}.",
        )

    def test_string_return(self):
        """
        Retorna variable string de función
        No Crea copia del string

        Return crea una copia para el valor de retorno
        La función limpiar los string dentro del scope
        """
        code = """
        get_greeting: function string() = {
            s: string = "Hello, World!";
            return s;
        }

        print get_greeting();
        """
        expected_output = "Hello, World!"
        gen, output = self.get_ir_and_output(code)
        self.assertEqual(output, expected_output)

        gen = str(gen)
        copies = gen.count('call i8* @"_bminor_string_copy"')
        self.assertEqual(
            copies,
            2,
            f"Se esperaban 2 llamada a _bminor_string_copy, se encontraron {copies}.",
        )
        frees = gen.count('call void @"_bminor_string_free"')
        self.assertEqual(
            frees,
            2,
            f"Se esperaban 2 llamada a _bminor_string_free, se encontraron {frees}.",
        )

    def test_assign_from_function(self):
        """
        Asigna valor retornado por función a variable string
        La función retorna un literal
        Crea copia del string
        Llama a runtime copy y free
        """
        code = """
        get_greeting: function string() = {
            return "Hello, World!";
        }
        s: string = get_greeting();
        print s;
        """
        expected_output = "Hello, World!"
        gen, output = self.get_ir_and_output(code)
        self.assertEqual(output, expected_output)

        # 1 copy del return 1 free
        gen = str(gen)
        copies = gen.count('call i8* @"_bminor_string_copy"')
        frees = gen.count('call void @"_bminor_string_free"')
        self.assertEqual(
            copies,
            1,
            f"Se esperaban 1 llamada a _bminor_string_copy, se encontraron {copies}.",
        )
        self.assertEqual(
            frees,
            1,
            f"Se esperaban 1 llamada a _bminor_string_free, se encontraron {frees}.",
        )

    def test_string_array(self):
        """
        Crea array de strings
        Crea copias de los strings
        Copy y free dependen de la gestión del array
        """
        code = """
        arr: array[3] string;
        arr[0] = "Hello, ";
        arr[1] = "World";
        arr[2] = "!";
        print arr[0], arr[1], arr[2];
        """
        expected_output = "Hello, World!"
        gen, output = self.get_ir_and_output(code)
        self.assertEqual(output, expected_output)

        # 3 copy y 3 free
        gen = str(gen)
        copies = gen.count('call i8* @"_bminor_string_copy"')
        frees = gen.count('call void @"_bminor_string_free"')
        self.assertEqual(
            copies,
            0,
            f"Se esperaban 0 llamadas a _bminor_string_copy, se encontraron {copies}.",
        )
        self.assertEqual(
            frees,
            0,
            f"Se esperaban 0 llamadas a _bminor_string_free, se encontraron {frees}.",
        )

    def test_string_from_array(self):
        """
        Obtiene string de array
        Crea copia del string
        Llama a runtime copy y free
        """
        code = """
        arr: array[3] string;
        arr[0] = "Hello, ";
        arr[1] = "World";
        arr[2] = "!";
        s: string = arr[1];
        print s;
        """
        expected_output = "World"
        gen, output = self.get_ir_and_output(code)
        self.assertEqual(output, expected_output)

        # 1 copy y 1 free
        gen = str(gen)
        copies = gen.count('call i8* @"_bminor_string_copy"')
        frees = gen.count('call void @"_bminor_string_free"')
        self.assertEqual(
            copies,
            1,
            f"Se esperaban 1 llamada a _bminor_string_copy, se encontraron {copies}.",
        )
        self.assertEqual(
            frees,
            1,
            f"Se esperaban 1 llamada a _bminor_string_free, se encontraron {frees}.",
        )

    def test_string_array_loc_param(self):
        """
        Pasar un item del array de strings a función
        Crea copia del string
        """
        code = """
        print_string: function void(s: string) = {
            print s;
        }

        arr: array[2] string;
        arr[0] = "Hello,";
        arr[1] = "World!";
        print_string(arr[0]);
        """
        expected_output = "Hello,"
        gen, output = self.get_ir_and_output(code)
        self.assertEqual(output, expected_output)

        gen = str(gen)
        copies = gen.count('call i8* @"_bminor_string_copy"')
        self.assertEqual(
            copies,
            1,
            f"Se esperaban 0 llamadas a _bminor_string_copy, se encontraron {copies}.",
        )
        frees = gen.count('call void @"_bminor_string_free"')
        self.assertEqual(
            frees,
            1,
            f"Se esperaban 0 llamadas a _bminor_string_free, se encontraron {frees}.",
        )

    def test_add_array_string(self):
        """
        Pasar un string literal como item del array
        """
        code = """
        arr: array[1] string = { "Hello, World!" };
        """

        gen, _ = self.get_ir_and_output(code)
        # 0 copy y 0 free
        # runtime se encarga de la copia en arrays de tipo string
        gen = str(gen)
        copies = gen.count('call i8* @"_bminor_string_copy"')
        frees = gen.count('call void @"_bminor_string_free"')
        self.assertEqual(
            copies,
            0,
            f"Se esperaban 0 llamadas a _bminor_string_copy, se encontraron {copies}.",
        )
        self.assertEqual(
            frees,
            0,
            f"Se esperaban 0 llamadas a _bminor_string_free, se encontraron {frees}.",
        )

    def test_add_array_strings(self):
        """
        Pasar un strings como item del array
        """
        code = """
        get_string: function string() = {
            return "Hello from function!";
        }

        var: string = "hola";
        arr: array[3] string = { "Hello, World!", var, get_string() };
        """

        gen, _ = self.get_ir_and_output(code)
        # 0 copy y 0 free
        # runtime se encarga de la copia en arrays de tipo string
        gen = str(gen)
        copies = gen.count('call i8* @"_bminor_string_copy"')
        frees = gen.count('call void @"_bminor_string_free"')
        self.assertEqual(
            copies,
            2,  # la copia de get_string(), var
            f"Se esperaban 2 llamadas a _bminor_string_copy, se encontraron {copies}.",
        )
        self.assertEqual(
            frees,
            2,  # la copia de get_string(), var
            f"Se esperaban 2 llamadas a _bminor_string_free, se encontraron {frees}.",
        )
