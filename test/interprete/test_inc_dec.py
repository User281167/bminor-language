import unittest
from parser import Parser
from parser.model import *

from interprete import Context, Interpreter
from scanner import Lexer
from utils import clear_errors, errors_detected


class TestIncDecInteger(unittest.TestCase):
    def setUp(self):
        clear_errors()

    def get_output(self, code):
        """Ejecuta código y devuelve output acumulado."""
        parser = Parser()
        tokens = Lexer().tokenize(code)
        ast = parser.parse(tokens)

        interpreter = Interpreter(Context(code), get_output=True)
        interpreter.interpret(ast)
        return interpreter.output

    def get_interpreter_error(self, code):
        """Espera un error de tipos (ej: float++)."""
        parser = Parser()
        tokens = Lexer().tokenize(code)
        ast = parser.parse(tokens)

        interpreter = Interpreter(Context(code), get_output=True)
        try:
            interpreter.interpret(ast)
        except Exception:
            pass
        self.assertTrue(errors_detected(), f"Se esperaba error en: {code}")

    # =========================================================================
    # 1. VARIABLES (L-VALUES) - MODIFICACIÓN DE MEMORIA
    # =========================================================================

    def test_inc_post_variable(self):
        """
        x++:
        1. Devuelve valor original.
        2. Incrementa variable en memoria.
        """
        code = """
        x: integer = 1;
        y: integer = 0;
        y = x++; 
        print y, x;
        """
        # y recibe 1 (valor viejo), x queda en 2
        expected = "12"
        self.assertEqual(self.get_output(code), expected)

    def test_inc_pre_variable(self):
        """
        ++x:
        1. Incrementa variable en memoria.
        2. Devuelve nuevo valor.
        """
        code = """
        z: integer = 1;
        z = ++z; 
        print z;
        """
        # z se incrementa a 2, devuelve 2, se asigna 2 a z.
        expected = "2"
        self.assertEqual(self.get_output(code), expected)

    def test_dec_post_variable(self):
        """
        x--: Devuelve viejo, decrementa variable.
        """
        code = """
        x: integer = 5;
        y: integer = 0;
        y = x--;
        print y, x;
        """
        # y recibe 5, x queda en 4
        expected = "54"
        self.assertEqual(self.get_output(code), expected)

    def test_dec_pre_variable(self):
        """
        --z: Decrementa variable, devuelve nuevo.
        """
        code = """
        z: integer = 5;
        z = --z;
        print z;
        """
        expected = "4"
        self.assertEqual(self.get_output(code), expected)

    # =========================================================================
    # 2. EXPRESIONES TEMPORALES (R-VALUES)
    # =========================================================================
    # Según tus tests de IR, permites ++ sobre expresiones que no son variables.
    # El interprete debe calcular, incrementar el valor temporal y retornarlo,
    # sin intentar guardar en memoria si no es una variable.

    def test_inc_pre_expr(self):
        """
        w = ++(1 - x);
        1. (1-x) -> 0
        2. ++0 -> 1 (se retorna 1)
        3. x no cambia
        """
        code = """
        x: integer = 1;
        w: integer = 0;
        w = ++(1 - x);
        print w, x;
        """
        expected = "11"
        self.assertEqual(self.get_output(code), expected)

    def test_dec_pre_expr(self):
        """
        w = --(x - 1);
        1. (x-1) -> 4
        2. --4 -> 3
        """
        code = """
        x: integer = 5;
        w: integer = 0;
        w = --(x - 1);
        print w, x;
        """
        expected = "35"
        self.assertEqual(self.get_output(code), expected)

    def test_literals(self):
        """
        Prueba con literales directos según tu especificación.
        5++ -> devuelve 5 (incrementa el temporal al aire)
        ++5 -> devuelve 6
        """
        code = "print 5++, ++5, 5--, --5;"
        expected = "5654"
        self.assertEqual(self.get_output(code), expected)

    # =========================================================================
    # 3. SECUENCIAS COMPLEJAS
    # =========================================================================

    def test_sequence_inc_dec_post_pre(self):
        code = """
        a: integer = 1;
        b: integer = 2;

        // a++ (dev 1, a=2) + b-- (dev 2, b=1) = 3
        res_ab: integer = a++ + b--;
        print res_ab, a, b;

        // a=2, b=1 actual.
        // ++a (a=3, dev 3) + --b (b=0, dev 0) = 3
        res_ba: integer = ++a + --b;
        print res_ba, a, b;
        """
        expected = "321330"
        self.assertEqual(self.get_output(code), expected)

    def test_sequence_complex_expr_inc_dec(self):
        """
        Evaluar orden de precedencia y efectos laterales.
        """
        code = """
        val: integer = 10;
        // val++ (dev 10, val=11) * 2 = 20
        // --val (val=10, dev 10)
        // 20 + 10 = 30
        res: integer = val++ * 2 + --val;
        print res, val;
        """
        expected = "3010"
        self.assertEqual(self.get_output(code), expected)

    # =========================================================================
    # 4. VALIDACIÓN DE TIPOS (ERRORES)
    # =========================================================================

    def test_error_float_inc(self):
        """Solo integers permitidos."""
        code = """
        f: float = 1.5;
        f++;
        """
        self.get_interpreter_error(code)

    def test_error_float_dec(self):
        """Solo integers permitidos."""
        code = "print --2.5;"
        self.get_interpreter_error(code)

    def test_error_bool_inc(self):
        """Bool no tiene aritmética."""
        code = """
        b: boolean = true;
        b++;
        """
        self.get_interpreter_error(code)

    def test_error_string_dec(self):
        code = 'print "hola"--;'
        self.get_interpreter_error(code)
