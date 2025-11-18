import unittest
from parser.model import *

from ir import IRGenerator, run_llvm_clang_ir
from utils import clear_errors, errors_detected


class TestStringConcatenation(unittest.TestCase):
    def setUp(self):
        """Se ejecuta antes de cada test."""
        clear_errors()

    def get_ir_and_output(self, code):
        """
        Función de ayuda para generar el IR, ejecutarlo y obtener la salida.
        Maneja las aserciones de errores comunes.
        """
        # Generar el IR a partir del código fuente
        ir_generator = IRGenerator()
        generated_ir = ir_generator.generate_from_code(code)

        # Verificar que no hubo errores durante la generación
        self.assertFalse(
            errors_detected(),
            "Errores semánticos detectados durante la generación de IR",
        )

        output = ""
        try:
            # Ejecutar el IR con el runtime de C y capturar la salida
            output = run_llvm_clang_ir(str(generated_ir), add_runtime=True)
            output = output.strip()  # Limpiar espacios en blanco
        except Exception as e:
            print(f"Error al ejecutar LLVM/Clang IR: {e}")
            print("--- LLVM IR Generado ---")
            print(str(generated_ir))
            print("------------------------")
            self.fail(f"La ejecución del IR falló: {e}")

        return generated_ir, output

    # --- Test 1: Concatenación Simple ---
    def test_concat_two_literals(self):
        """
        Prueba la concatenación básica de dos strings literales.
        Verifica que el resultado impreso es correcto.
        """
        code = """
        main: function void () = {
            print "hello" + " world";
        }
        """
        _, output = self.get_ir_and_output(code)
        self.assertEqual(output, "hello world")

    # --- Test 2: Concatenación Múltiple ---
    def test_concat_three_literals(self):
        """
        Prueba la concatenación de tres strings literales.
        Esto verifica que el resultado intermedio de la primera concatenación
        se maneja correctamente como entrada para la segunda.
        """
        code = """
        main: function void () = {
            print "one" + " two " + "three";
        }
        """
        # El AST se agrupará como ("one" + " two ") + "three"
        _, output = self.get_ir_and_output(code)
        self.assertEqual(output, "one two three")

    # --- Test 3: Concatenación con String Vacío ---
    def test_concat_with_empty_string(self):
        """
        Prueba que la concatenación con un string vacío funciona
        correctamente, tanto a la izquierda como a la derecha.
        """
        # Caso 1: Vacío a la derecha
        code_right = """
        main: function void () = {
            print "start" + "";
        }
        """
        _, output_right = self.get_ir_and_output(code_right)
        self.assertEqual(output_right, "start")

        # Caso 2: Vacío a la izquierda
        code_left = """
        main: function void () = {
            print "" + "end";
        }
        """
        _, output_left = self.get_ir_and_output(code_left)
        self.assertEqual(output_left, "end")
