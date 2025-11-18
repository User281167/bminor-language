import unittest

from ir import IRGenerator, run_llvm_clang_ir
from utils import clear_errors, errors_detected


class TestStringVariables(unittest.TestCase):
    def setUp(self):
        """Se ejecuta antes de cada test."""
        clear_errors()

    def get_ir_and_output(self, code):
        """
        Función de ayuda para generar el IR, ejecutarlo y obtener la salida.
        """
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

    # --- Tests para Variables Locales ---

    def test_local_string_declaration_uninitialized(self):
        """
        Prueba que una variable string local sin valor inicial
        se crea correctamente como un string vacío.
        """
        code = """
        main: function void () = {
            s: string;
            print s;
        }
        """
        _, output = self.get_ir_and_output(code)
        self.assertEqual(output, "")

    def test_local_string_declaration_initialized(self):
        """
        Prueba que una variable string local se inicializa
        correctamente con un valor literal.
        """
        code = """
        main: function void () = {
            s: string = "hello from local";
            print s;
        }
        """
        _, output = self.get_ir_and_output(code)
        self.assertEqual(output, "hello from local")

    def test_local_string_assignment_from_variable(self):
        """
        Prueba la asignación de una variable a otra, verificando
        que la semántica de copia funciona.
        """
        code = """
        main: function void () = {
            s1: string = "source value";
            s2: string;
            s2 = s1;
            print s2;
        }
        """
        _, output = self.get_ir_and_output(code)
        self.assertEqual(output, "source value")

    def test_local_string_reassignment(self):
        """
        Prueba la reasignación de una variable string. Esto es crucial
        para verificar que la memoria del valor antiguo se libera
        correctamente antes de asignar el nuevo.
        """
        code = """
        main: function void () = {
            s: string = "first value";
            s = "second value";
            print s;
        }
        """
        _, output = self.get_ir_and_output(code)
        self.assertEqual(output, "second value")

    # --- Tests para Variables Globales ---

    def test_global_string_variables(self):
        """
        Prueba la declaración y asignación de variables string globales.
        """
        code = """
        g_uninit: string;
        g_init: string = "initial global";

        main: function void () = {
            print g_uninit;
            print "---";
            print g_init;
        }
        """
        # Se espera que g_uninit sea "" y g_init tenga su valor.
        # La salida de print separa con un espacio por defecto
        # (Ajusta el 'expected' si tu print no añade espacios).
        expected_output = "---initial global"
        _, output = self.get_ir_and_output(code)
        self.assertEqual(output, expected_output)

    def test_global_string_assignment_in_main(self):
        """
        Prueba que una variable global puede ser modificada
        correctamente dentro de una función.
        """
        code = """
        s: string = "original";

        main: function void () = {
            s = "modified in main";
            print s;
        }
        """
        _, output = self.get_ir_and_output(code)
        self.assertEqual(output, "modified in main")

    def test_full_string_lifecycle(self):
        """
        Un test completo que combina globales, locales, asignación
        y reasignación para asegurar que todo el sistema funciona en conjunto.
        """
        code = """
        g_str: string = "global";

        main: function void () = {
            l_str: string;
            l_str = g_str + " and local"; // Asignación con concatenación
            print l_str; // "global and local"

            g_str = "new global"; // Reasignación de global

            print "---";
            print g_str; // "new global"
            print "---";
            print l_str; // Aún debe ser "global and local", probando la copia
        }
        """
        expected_output = "global and local---new global---global and local"
        _, output = self.get_ir_and_output(code)
        self.assertEqual(output, expected_output)

    def test_concat_variables(self):
        code = """
        main: function void () = {
            a: string = "a";
            b: string = "b";
            c: string = a + b;
            print c;
        }
        """
        _, output = self.get_ir_and_output(code)
        self.assertEqual(output, "ab")
