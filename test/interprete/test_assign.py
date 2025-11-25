import unittest
from parser import Parser

# from parser.model import * # (Opcional si no necesitas clases directas aquí)
from interprete import Context, Interpreter
from scanner import Lexer
from utils import clear_errors, errors_detected


class TestAssignment(unittest.TestCase):
    def setUp(self):
        clear_errors()

    def get_output(self, code):
        """Ejecuta código válido y retorna la salida."""
        parser = Parser()
        tokens = Lexer().tokenize(code)
        ast = parser.parse(tokens)

        interpreter = Interpreter(Context(code), get_output=True)
        interpreter.interpret(ast)
        return interpreter.output

    def get_interpreter_error(self, code):
        """Ejecuta código esperando un error (semántico o runtime)."""
        parser = Parser()
        tokens = Lexer().tokenize(code)
        ast = parser.parse(tokens)

        interpreter = Interpreter(Context(code), get_output=True)
        try:
            interpreter.interpret(ast)
        except Exception:
            pass

        self.assertTrue(errors_detected(), f"Se esperaba un error en: {code}")

    # =========================================================================
    # CASOS DE ÉXITO (HAPPY PATH)
    # =========================================================================

    def test_simple_assignment(self):
        """Prueba básica: declarar y actualizar."""
        code = """
        x: integer = 10;
        x = 20;
        print x;
        """
        expected = "20"
        self.assertEqual(self.get_output(code), expected)

    def test_assignment_with_expression(self):
        """La asignación debe resolver la expresión a la derecha primero."""
        code = """
        val: integer = 5;
        val = 5 * 2 + 1;
        print val;
        """
        expected = "11"
        self.assertEqual(self.get_output(code), expected)

    def test_self_assignment(self):
        """Prueba usar la misma variable en la expresión (x = x + 1)."""
        code = """
        counter: integer = 1;
        counter = counter + 1;
        print counter;
        """
        expected = "2"
        self.assertEqual(self.get_output(code), expected)

    def test_chained_assignment(self):
        """
        Prueba a = b = 10.
        Para que esto funcione, visit_Assign debe retornar el valor asignado.
        """
        code = """
        a: integer = 0;
        b: integer = 0;
        c: integer = 0;
        a = b = c = 50;
        print a, b, c;
        """
        expected = "505050"
        self.assertEqual(self.get_output(code), expected)

    def test_auto_reassignment(self):
        """
        Si se usó 'auto', el tipo se fijó en la declaración.
        Aquí probamos que se pueda reasignar el MISMO tipo.
        """
        code = """
        x: auto = 100;
        x = 200; 
        print x;
        """
        expected = "200"
        self.assertEqual(self.get_output(code), expected)

    # =========================================================================
    # CASOS DE ERROR (STRICT TYPING & SCOPE)
    # =========================================================================

    def test_error_assign_undeclared(self):
        """No se puede asignar a una variable que no existe."""
        code = "z = 10;"
        self.get_interpreter_error(code)

    def test_error_type_mismatch_int(self):
        """Declarada int, intento asignar float."""
        code = """
        i: integer = 10;
        i = 10.5;
        """
        self.get_interpreter_error(code)

    def test_error_type_mismatch_bool(self):
        """Declarada bool, intento asignar int."""
        code = """
        flag: boolean = true;
        flag = 0;
        """
        self.get_interpreter_error(code)

    def test_error_auto_type_mismatch(self):
        """
        'auto' infiere string. Intentar asignar bool después es error.
        """
        code = """
        s: auto = "Hola";
        s = true;
        """
        self.get_interpreter_error(code)

    def test_error_assign_to_constant(self):
        """No se puede reasignar una constante."""
        code = """
        PI: constant = 3.14;
        PI = 3.1415;
        """
        self.get_interpreter_error(code)
