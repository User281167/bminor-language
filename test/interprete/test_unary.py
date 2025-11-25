import unittest
from parser import Parser
from parser.model import *  # Asegúrate de importar tus nodos

from interprete import Context, Interpreter
from scanner import Lexer
from utils import clear_errors, errors_detected


# Asumo que tienes una excepción específica para errores en tiempo de ejecución.
# Si usas Exception genérico, cámbialo aquí.
class RuntimeException(Exception):
    pass


class TestUnary(unittest.TestCase):
    def setUp(self):
        clear_errors()

    def get_output(self, code):
        """Helper para ejecutar y obtener string."""
        parser = Parser()
        tokens = Lexer().tokenize(code)
        ast = parser.parse(tokens)

        # El intérprete debe estar configurado para capturar salida
        interpreter = Interpreter(Context(code), get_output=True)
        interpreter.interpret(ast)
        return interpreter.output

    def get_interpreter_error(self, code):
        """Helper para ejecutar y esperar una excepción."""
        parser = Parser()
        tokens = Lexer().tokenize(code)
        ast = parser.parse(tokens)
        interpreter = Interpreter(Context(code), get_output=True)
        interpreter.interpret(ast)

        self.assertTrue(errors_detected())

    # -------------------------------------------------------------------------
    # TEST UNARIOS: INTEGER (- y +)
    # -------------------------------------------------------------------------
    def test_unary_integer(self):
        # Prueba negativo (-) y positivo (+)
        code = "print -5, +5;"
        expected = "-55"
        self.assertEqual(self.get_output(code), expected)

    def test_unary_integer_chained(self):
        # Prueba doble negativo (menos por menos da más)
        # Nota: Esto requiere que tu parser soporte recursión en unarios (ej: - -5)
        code = "print - -5;"
        expected = "5"
        self.assertEqual(self.get_output(code), expected)

    # -------------------------------------------------------------------------
    # TEST UNARIOS: FLOAT (- y +)
    # -------------------------------------------------------------------------
    def test_unary_float(self):
        code = "print -3.14, +2.5;"
        expected = "-3.142.5"
        self.assertEqual(self.get_output(code), expected)

    # -------------------------------------------------------------------------
    # TEST UNARIOS: BOOL (!)
    # -------------------------------------------------------------------------
    def test_unary_bool_not(self):
        # !true -> false, !false -> true
        code = "print !true, !false;"
        expected = "falsetrue"
        self.assertEqual(self.get_output(code), expected)

    def test_unary_bool_double_not(self):
        # !!true -> true
        code = "print !!true;"
        expected = "true"
        self.assertEqual(self.get_output(code), expected)

    # -------------------------------------------------------------------------
    # VALIDACIÓN DE TIPOS (ERRORES)
    # -------------------------------------------------------------------------
    # Como pediste: "-", "+" SOLO para números, "!" SOLO para bool.
    # Estos tests aseguran que tu intérprete lance error si se violan las reglas.

    def test_error_minus_on_bool(self):
        # No se puede hacer -true
        code = "print -true;"
        # Cambia Exception por tu clase de error específica (ej: TypeError, RuntimeError)
        self.get_interpreter_error(code)

    def test_error_not_on_integer(self):
        # No se puede hacer !1
        code = "print !1;"
        self.get_interpreter_error(code)

    def test_error_not_on_string(self):
        # No se puede hacer !"hola"
        code = "print !'hola';"
        self.get_interpreter_error(code)
