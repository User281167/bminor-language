import unittest
from parser import Parser
from parser.model import *

from interprete import Context, Interpreter
from scanner import Lexer
from utils import clear_errors, errors_detected


class TestBinary(unittest.TestCase):
    def setUp(self):
        clear_errors()

    def get_output(self, code):
        """Ejecuta código y devuelve el output acumulado."""
        parser = Parser()
        tokens = Lexer().tokenize(code)
        ast = parser.parse(tokens)

        interpreter = Interpreter(Context(code), get_output=True)
        interpreter.interpret(ast)
        return interpreter.output

    def get_interpreter_error(self, code):
        """
        Ejecuta código esperando que se detecten errores
        (usando tu helper errors_detected).
        """
        parser = Parser()
        tokens = Lexer().tokenize(code)
        ast = parser.parse(tokens)

        interpreter = Interpreter(Context(code), get_output=True)
        # Aquí capturamos excepciones si el intérprete lanza 'raise'
        # o verificamos el flag de errores si el intérprete solo loguea.
        try:
            interpreter.interpret(ast)
        except Exception:
            pass  # Si lanza excepción, asumimos que fue capturada o validamos abajo

        # Verificamos si el sistema de logs registró el error
        self.assertTrue(
            errors_detected(), f"Se esperaba un error para el código: {code}"
        )

    # =========================================================================
    # 1. ARITMÉTICA DE ENTEROS (Integer Operations)
    # =========================================================================
    def test_int_arithmetic_basic(self):
        # +, -, *
        code = "print 10 + 20, 10 - 2, 5 * 4;"
        expected = "30820"
        self.assertEqual(self.get_output(code), expected)

    def test_int_division_strict(self):
        """
        Según tu código:
        if isinstance(left, int) and isinstance(right, int): return left // right
        Esto significa división ENTERA para integers.
        """
        # 10 / 3 debería ser 3, no 3.3333
        code = "print 10 / 3;"
        expected = "3"
        self.assertEqual(self.get_output(code), expected)

    def test_int_modulo(self):
        code = "print 10 % 3;"  # Sobra 1
        expected = "1"
        self.assertEqual(self.get_output(code), expected)

    def test_int_precedence(self):
        # Validar precedencia estándar (multiplicación antes que suma)
        # Esto depende de tu Parser, pero es bueno probarlo aquí.
        code = "print 2 + 3 * 4;"  # 2 + 12 = 14
        expected = "14"
        self.assertEqual(self.get_output(code), expected)

    # =========================================================================
    # 2. ARITMÉTICA DE FLOTANTES (Float Operations)
    # =========================================================================
    def test_float_arithmetic(self):
        code = "print 2.5 + 2.5, 5.0 - 1.5, 2.0 * 1.5;"
        expected = "5.03.53.0"
        self.assertEqual(self.get_output(code), expected)

    def test_float_division(self):
        # Float sí debe devolver decimales
        code = "print 5.0 / 2.0;"
        expected = "2.5"
        self.assertEqual(self.get_output(code), expected)

    # =========================================================================
    # 3. COMPARACIONES (Integer, Float, Char)
    # =========================================================================
    def test_comparisons_numeric(self):
        # <, <=, >, >=
        code = "print 1 < 2, 2 <= 2, 5 > 10, 5 >= 5;"
        expected = "truetruefalsetrue"
        self.assertEqual(self.get_output(code), expected)

    def test_equality(self):
        # ==, !=
        code = "print 10 == 10, 10 != 5;"
        expected = "truetrue"
        self.assertEqual(self.get_output(code), expected)

    def test_char_comparison(self):
        # 'a' < 'b' es verdadero por código ASCII
        code = "print 'a' < 'b', 'b' == 'b';"
        expected = "truetrue"
        self.assertEqual(self.get_output(code), expected)

    # =========================================================================
    # 4. LÓGICA BOOLEANA (Short-circuit)
    # =========================================================================
    def test_logical_ops(self):
        # LAND, LOR
        # true LAND true -> true
        # true LOR false -> true
        code = "print true && true, false || true, true && false;"
        expected = "truetruefalse"
        self.assertEqual(self.get_output(code), expected)

    def test_logical_equality(self):
        # boolean == boolean
        code = "print true == true, false != true;"
        expected = "truetrue"
        self.assertEqual(self.get_output(code), expected)

    # =========================================================================
    # 5. STRING CONCATENATION
    # =========================================================================
    def test_string_concat(self):
        # Solo operador + está definido para string
        code = 'print "Hola" + " " + "Mundo";'
        expected = "Hola Mundo"
        self.assertEqual(self.get_output(code), expected)

    # =========================================================================
    # 6. ERRORES DE TIPOS (Validación estricta de _bin_ops)
    # =========================================================================

    def test_error_mixed_types_int_float(self):
        """
        Tu tabla _bin_ops NO define ('integer', '+', 'float').
        Esto debe dar error, no conversión implícita.
        """
        code = "print 1 + 2.5;"
        self.get_interpreter_error(code)

    def test_error_mixed_types_string_int(self):
        """
        Tu tabla NO define ('string', '+', 'integer').
        """
        code = 'print "Numero: " + 1;'
        self.get_interpreter_error(code)

    def test_error_char_arithmetic(self):
        """
        Tu tabla NO define ('char', '+', 'char').
        Solo permite comparaciones para chars.
        """
        code = "print 'a' + 'b';"
        self.get_interpreter_error(code)

    def test_error_bool_arithmetic(self):
        """
        No se puede sumar booleanos.
        """
        code = "print true + false;"
        self.get_interpreter_error(code)
