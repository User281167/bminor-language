import unittest
from parser import Parser

# Asegúrate de que parser.model tenga las definiciones necesarias (Program, Print, etc.)
from parser.model import *

from interprete import Context, Interpreter
from scanner import Lexer
from utils import clear_errors


class TestPrint(unittest.TestCase):
    def setUp(self):
        clear_errors()

    def get_output(self, code):
        """Ayuda para ejecutar el código y capturar la salida."""
        parser = Parser()
        tokens = Lexer().tokenize(code)
        ast = parser.parse(tokens)

        # Asumimos que tu Interpreter tiene un flag 'get_output' que
        # redirige los prints a una variable interna self.output
        interpreter = Interpreter(Context(code), get_output=True)
        interpreter.interpret(ast)

        return interpreter.output

    def test_basic_print(self):
        """Prueba básica de enteros concatenados."""
        code = "print 1, 2;"
        expected_output = "12"
        output = self.get_output(code)
        self.assertEqual(output, expected_output)

    def test_newline_separator(self):
        """
        Prueba el caso específico solicitado: print 1, '\n', 1;
        Verifica que el caracter de escape se interprete correctamente.
        """
        code = """print 1, '\\n', 1;"""
        # Nota: En el string de Python usamos '\\n' para enviar
        # los caracteres literales \ y n al Lexer, o '\n' si el Lexer lo soporta directo.
        # Si tu lexer soporta '\n' dentro de chars:

        expected_output = "1\n1"
        output = self.get_output(code)
        self.assertEqual(output, expected_output)

    def test_floating_point(self):
        """Prueba de números flotantes."""
        code = "print 3.14, 0.005;"
        expected_output = "3.140.005"
        output = self.get_output(code)
        self.assertEqual(output, expected_output)

    def test_booleans(self):
        """
        Prueba de booleanos.
        Requerimiento: bool -> true, false (en minúsculas).
        """
        code = "print true, false;"

        # Dependiendo de tu implementación, Python convierte True a "True".
        # Asegúrate de que tu intérprete convierta bools a strings en minúscula
        # si eso es lo que requiere tu lenguaje.
        expected_output = "truefalse"
        output = self.get_output(code)
        self.assertEqual(output, expected_output)

    def test_chars_and_strings(self):
        """Prueba de char y string."""
        # Asumiendo comillas simples para char y dobles para string
        code = """
        print 'A', "Hola Mundo";
        """
        expected_output = "AHola Mundo"
        output = self.get_output(code)
        self.assertEqual(output, expected_output)

    def test_mixed_types(self):
        """
        Prueba integradora con todos los tipos:
        char, string, integer, float, bool
        """
        code = """
        print 'C', ": ", "Valor ", 10, " - ", 5.5, " es ", true;
        """
        expected_output = "C: Valor 10 - 5.5 es true"
        output = self.get_output(code)
        self.assertEqual(output, expected_output)
