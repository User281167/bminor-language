import unittest
from parser import Parser
from parser.model import *

from interprete import Context, Interpreter
from scanner import Lexer
from utils import clear_errors, errors_detected


class TestDeclarations(unittest.TestCase):
    def setUp(self):
        clear_errors()

    def get_output(self, code):
        """Ejecuta código y devuelve la salida."""
        parser = Parser()
        tokens = Lexer().tokenize(code)
        ast = parser.parse(tokens)

        interpreter = Interpreter(Context(code), get_output=True)
        interpreter.interpret(ast)
        return interpreter.output

    def get_interpreter_error(self, code):
        """Ejecuta código esperando que ocurra un error semántico/runtime."""
        parser = Parser()
        tokens = Lexer().tokenize(code)
        ast = parser.parse(tokens)

        interpreter = Interpreter(Context(code), get_output=True)
        try:
            interpreter.interpret(ast)
        except Exception:
            pass  # Asumimos captura interna o excepción directa

        self.assertTrue(errors_detected(), f"Se esperaba error en: {code}")

    # =========================================================================
    # 1. DECLARACIONES EXPLÍCITAS (Happy Path)
    # =========================================================================
    def test_explicit_declarations(self):
        """Prueba declaración de todos los tipos básicos."""
        code = """
        i: integer = 10;
        f: float = 3.14;
        b: boolean = true;
        c: char = 'X';
        s: string = "Test";
        print i, f, b, c, s;
        """
        expected = "103.14trueXTest"
        self.assertEqual(self.get_output(code), expected)

    # =========================================================================
    # 2. AUTO INFERENCIA (Happy Path)
    # =========================================================================
    def test_auto_declaration(self):
        """
        'auto' debe inferir el tipo del valor asignado.
        """
        code = """
        x: auto = 100;
        y: auto = "AutoString";
        print x, y;
        """
        expected = "100AutoString"
        self.assertEqual(self.get_output(code), expected)

    # =========================================================================
    # 3. CONSTANTES (Happy Path)
    # =========================================================================
    def test_constant_declaration(self):
        """Declaración de constantes."""
        code = """
        PI: constant = 3.14159;
        MAX: constant = 10;
        print PI, MAX;
        """
        expected = "3.1415910"
        self.assertEqual(self.get_output(code), expected)

    # =========================================================================
    # 4. ASIGNACIONES (Happy Path)
    # =========================================================================
    def test_assignment_update(self):
        """Actualizar el valor de una variable existente."""
        code = """
        x: integer = 1;
        x = 5;
        print x;
        """
        expected = "5"
        self.assertEqual(self.get_output(code), expected)

    def test_chained_assignment(self):
        """
        Prueba a = b = 10;
        La asignación debe devolver el valor asignado para permitir encadenamiento.
        """
        code = """
        a: integer = 0;
        b: integer = 1;
        a = b = 10;
        print a, b;
        """
        expected = "1010"
        self.assertEqual(self.get_output(code), expected)

    # =========================================================================
    # 5. VALIDACIÓN DE TIPOS ESTRICTA (Error Path)
    # =========================================================================

    def test_error_type_mismatch_explicit(self):
        """Error al declarar explícitamente con tipo incorrecto."""
        # integer no puede recibir float
        code = "i: integer = 2.5;"
        self.get_interpreter_error(code)

    def test_error_assignment_mismatch(self):
        """Error al asignar un tipo diferente a una variable ya declarada."""
        code = """
        i: integer = 10;
        i = true;
        """
        self.get_interpreter_error(code)

    # =========================================================================
    # 6. AUTO: INMUTABILIDAD DE TIPO (Error Path)
    # =========================================================================
    def test_error_auto_type_change(self):
        """
        'auto' infiere el tipo al inicio (ej: int).
        No debe permitir cambiar a float después.
        """
        code = """
        a: auto = 10; 
        a = 10.5;
        """
        self.get_interpreter_error(code)

    def test_error_auto_string_to_int(self):
        """
        'auto' infiere string, intentar asignar int debe fallar.
        """
        code = """
        s: auto = "Hola";
        s = 1;
        """
        self.get_interpreter_error(code)

    # =========================================================================
    # 7. CONSTANT: INMUTABILIDAD DE VALOR (Error Path)
    # =========================================================================
    def test_error_modify_constant(self):
        """Error al intentar asignar un nuevo valor a una constante."""
        code = """
        K: constant = 100;
        K = 200;
        """
        self.get_interpreter_error(code)

    def test_error_modify_constant_chained(self):
        """Error incluso en asignaciones encadenadas."""
        code = """
        K: constant = 5;
        var: integer = 0;
        var = K = 10;
        """
        self.get_interpreter_error(code)
