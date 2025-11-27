import unittest
from parser import Parser
from parser.model import *

from interprete import Context, Interpreter
from scanner import Lexer
from utils import clear_errors, errors_detected


class TestInterpreterFunctions(unittest.TestCase):
    def setUp(self):
        clear_errors()

    def get_output(self, code):
        """Ejecuta el código y devuelve la salida."""
        parser = Parser()
        tokens = Lexer().tokenize(code)
        ast = parser.parse(tokens)

        interpreter = Interpreter(Context(code), get_output=True)
        interpreter.interpret(ast)

        if errors_detected():
            self.fail(f"Errores detectados en el intérprete:\n{code}")

        return interpreter.output

    def get_interpreter_error(self, code):
        """Espera un error de ejecución (ej: argumentos incorrectos)."""
        parser = Parser()
        tokens = Lexer().tokenize(code)
        ast = parser.parse(tokens)

        interpreter = Interpreter(Context(code), get_output=True)
        try:
            interpreter.interpret(ast)
        except Exception:
            return
        self.assertTrue(errors_detected(), f"Se esperaba error en:\n{code}")

    # =========================================================================
    # 1. LLAMADAS BÁSICAS Y PARÁMETROS
    # =========================================================================

    def test_void_function_no_args(self):
        """Llamada simple a función void."""
        code = """
        greet: function void() = {
            print "Hello World";
        }
        
        print "Start ";
        greet();
        print " End";
        """
        expected = "Start Hello World End"
        self.assertEqual(self.get_output(code), expected)

    def test_function_multiple_params_mixed_types(self):
        """Paso de parámetros de distintos tipos."""
        code = """
        show_info: function void(age: integer, active: boolean, name: string) = {
            print name, " is ", age, " active: ", active;
        }

        show_info(25, true, "Alice");
        """
        # Ajusta el formato de bool según tu implementación
        expected = "Alice is 25 active: true"
        self.assertEqual(self.get_output(code), expected)

    # =========================================================================
    # 2. VALORES DE RETORNO Y EXPRESIONES
    # =========================================================================

    def test_return_value_usage(self):
        """Usar el valor de retorno en una expresión matemática."""
        code = """
        square: function integer(x: integer) = {
            return x * x;
        }

        // 5 + (4 * 4) = 21
        res: integer = 5 + square(4);
        print res;
        """
        expected = "21"
        self.assertEqual(self.get_output(code), expected)

    def test_nested_function_calls(self):
        """Llamada a función dentro de argumento de otra (f(g(x)))."""
        code = """
        add: function integer(a: integer, b: integer) = {
            return a + b;
        }
        
        // add(10, add(5, 5)) -> add(10, 10) -> 20
        print add(10, add(5, 5));
        """
        expected = "20"
        self.assertEqual(self.get_output(code), expected)

    # =========================================================================
    # 3. SCOPE Y SHADOWING (CRÍTICO PARA INTÉRPRETES)
    # =========================================================================

    def test_scope_shadowing_param(self):
        """
        Prueba que el parámetro 'x' oculte a la variable global 'x'.
        Y que la global no se vea afectada.
        """
        code = """
        x: integer = 100; // Global

        print_local: function void(x: integer) = {
            print x; // Debe imprimir el argumento (50), no la global
            x = 0;   // Modifica la local
        }

        print_local(50);
        print x; // La global debe seguir siendo 100
        """
        expected = "50100"
        self.assertEqual(self.get_output(code), expected)

    def test_scope_shadowing_local_var(self):
        """
        Prueba variable local declarada dentro de la función vs global.
        """
        code = """
        val: string = "Global";

        change: function void() = {
            val: string = "Local"; // Nueva variable, oculta la global
            print val;
        }

        change();
        print val; // Debe imprimir "Global"
        """
        expected = "LocalGlobal"
        self.assertEqual(self.get_output(code), expected)

    def test_scope_access_global(self):
        """
        Prueba que la función PUEDE leer globales si no hay shadowing.
        """
        code = """
        global_factor: integer = 2;

        multiply: function integer(n: integer) = {
            return n * global_factor;
        }

        print multiply(10);
        """
        expected = "20"
        self.assertEqual(self.get_output(code), expected)

    # =========================================================================
    # 4. CONTROL DE FLUJO AVANZADO (EARLY RETURN)
    # =========================================================================

    def test_early_return_logic(self):
        """
        Prueba CRÍTICA para Interpretes (Visitor):
        El 'return' debe detener la ejecución de la función inmediatamente,
        incluso si hay más código debajo.
        """
        code = """
        check: function integer(val: integer) = {
            if (val > 10) {
                return 1;
            }

            // Si el return no detiene la ejecución, esto se imprimirá (ERROR)
            print "No deberia verse";
            return 0;
        }

        print check(20);
        print check(5);
        """
        # Esperado: 1 (del primer call) y 0 (del segundo call sin print extra)
        expected = "1No deberia verse0"
        self.assertEqual(self.get_output(code), expected)

    def test_return_inside_loop(self):
        """Return rompiendo un bucle."""
        code = """
        find: function integer() = {
            i: integer;
            for(i=0; i<10; i++) {
                if (i == 3) {
                    return i; // Debe salir de la función y del loop
                }
            }
            return -1;
        }
        print find();
        """
        expected = "3"
        self.assertEqual(self.get_output(code), expected)

    # =========================================================================
    # 5. RECURSIVIDAD
    # =========================================================================

    def test_recursion_factorial(self):
        """Recursividad simple."""
        code = """
        fact: function integer(n: integer) = {
            if (n <= 1) return 1;
            return n * fact(n - 1);
        }
        print fact(5);
        """
        expected = "120"
        self.assertEqual(self.get_output(code), expected)

    def test_mutual_recursion(self):
        """
        Recursividad mutua (Paridad).
        Requiere que el intérprete pueda resolver nombres que se definen después
        (o usar forward declaration si tu lenguaje lo pide).
        """
        code = """
        is_odd: function boolean(n: integer);

        is_even: function boolean(n: integer) = {
            if (n == 0) return true;
            return is_odd(n - 1);
        }

        is_odd: function boolean(n: integer) = {
            if (n == 0) return false;
            return is_even(n - 1);
        }

        print is_even(4);
        print is_odd(4);
        """
        expected = "truefalse"  # o "TrueFalse"
        self.assertEqual(self.get_output(code), expected)

    # =========================================================================
    # 6. ERRORES DE TIEMPO DE EJECUCIÓN (RUNTIME)
    # =========================================================================

    def test_arg_count_mismatch(self):
        """Llamar a función con menos argumentos de los necesarios."""
        code = """
        add: function integer(a: integer, b: integer) = { return a + b; }
        add(1); 
        """
        self.get_interpreter_error(code)

    def test_void_func_returning_value(self):
        """
        Intentar asignar el resultado de una función void.
        (Semántico/Runtime).
        """
        code = """
        no_ret: function void() = { print "Hi"; }
        x: integer = no_ret(); 
        """
        self.get_interpreter_error(code)
