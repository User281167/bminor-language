import unittest
from parser import Parser
from parser.model import *

from interprete import Context, Interpreter
from scanner import Lexer
from utils import clear_errors, errors_detected


class TestInterpreterStringReference(unittest.TestCase):
    def setUp(self):
        clear_errors()

    def get_output(self, code):
        """Ejecuta el código en el intérprete y retorna la salida."""
        parser = Parser()
        tokens = Lexer().tokenize(code)
        ast = parser.parse(tokens)

        # Interpreter ejecutando en contexto global
        interpreter = Interpreter(Context(code), get_output=True)
        interpreter.interpret(ast)

        if errors_detected():
            self.fail(f"Errores en el intérprete:\n{code}")

        return interpreter.output

    # =========================================================================
    # TESTS DE STRINGS POR REFERENCIA
    # =========================================================================

    def test_string_param_mutation_variable(self):
        """
        Prueba el caso base solicitado:
        Pasar una variable string a una función y modificarla dentro.
        El cambio debe reflejarse fuera.
        """
        code = """
        set_s: function string(var: string) = {
            var = "new";
            return var;
        }

        s: string = "old";

        // Llamada pasando variable
        set_s(s);

        print s;
        """
        # Esperado: "new" porque 'var' es una referencia a 's'
        expected = "new"
        self.assertEqual(self.get_output(code), expected)

    def test_string_param_mutation_literal(self):
        """
        Prueba pasando un literal.
        La función modifica su parámetro local, pero como no hay variable externa,
        no hay efecto visible fuera (solo no debe crashear).
        """
        code = """
        set_s: function string(var: string) = {
            var = "changed";
            return var;
        }

        // Llamada pasando literal
        // El intérprete crea un temp, lo modifica a "changed", retorna "changed", y descarta el temp.
        res: string = set_s("original");

        print res;
        """
        expected = "changed"
        self.assertEqual(self.get_output(code), expected)

    def test_concat_and_mutation(self):
        """
        Verifica que la concatenación funcione junto con la mutación.
        """
        code = """
        append_exclam: function void(s: string) = {
            s = s + "!";
        }

        msg: string = "Hola";

        append_exclam(msg); // msg se convierte en "Hola!"
        append_exclam(msg); // msg se convierte en "Hola!!"

        print msg;
        """
        expected = "Hola!!"
        self.assertEqual(self.get_output(code), expected)

    def test_return_modified_param_semantics(self):
        """
        Verifica la diferencia entre la variable original (modificada)
        y el valor de retorno (copia del valor en ese momento).
        """
        code = """
        update: function string(target: string) = {
            target = "Inside";
            return target; // Retorna "Inside"
        }

        outer: string = "Outside";

        // 'outer' cambia a "Inside" por referencia.
        // 'res' toma el valor "Inside" retornado.
        res: string = update(outer);

        // Ahora modificamos 'res'. NO debe afectar a 'outer'
        // (el retorno es valor, no referencia a la referencia).
        res = "Distinct";

        print outer, "-", res;
        """
        expected = "Inside-Distinct"
        self.assertEqual(self.get_output(code), expected)

    def test_global_vs_local_shadowing_ref(self):
        """
        Prueba compleja de Scope + Referencia.
        """
        code = """
        g_str: string = "GLOBAL";

        modify_arg: function void(arg: string) = {
            // Modifica lo que le pasen
            arg = "MODIFIED_ARG";
        }

        // Caso 1: Pasamos la global explícitamente
        modify_arg(g_str);
        print g_str, " ";

        // Caso 2: Variable local con mismo nombre que global (Shadowing)
        // Probamos que modifique la local y NO la global
        main_logic: function void() = {
             g_str: string = "LOCAL";

             modify_arg(g_str); // Modifica la local
             print g_str;
        }

        main_logic();

        // La global debe seguir siendo "MODIFIED_ARG" (del paso 1),
        // no "MODIFIED_ARG" (del paso 2, ese fue a la local).
        print " ", g_str;
        """
        # 1. modify_arg(global) -> Global es "MODIFIED_ARG"
        # 2. main_logic -> local es "LOCAL" -> modify_arg(local) -> local es "MODIFIED_ARG"
        # 3. Global sigue siendo "MODIFIED_ARG"
        expected = "MODIFIED_ARG MODIFIED_ARG MODIFIED_ARG"
        self.assertEqual(self.get_output(code), expected)

    def test_nested_call_ref(self):
        """
        Prueba encadenamiento.
        A -> llama B(A) -> B llama C(A).
        Todos modifican la misma variable original.
        """
        code = """
        step2: function void(s2: string) = {
            s2 = s2 + "2";
        }

        step1: function void(s1: string) = {
            s1 = s1 + "1";
            step2(s1); // Pasa la referencia hacia abajo
        }

        val: string = "0";
        step1(val);

        print val;
        """
        expected = "012"
        self.assertEqual(self.get_output(code), expected)

    def test_nested_expressions_safety(self):
        """
        Prueba de la expresión compleja que pusiste:
        say_hi((f() + f()) + (f() + "!"));
        Esto genera temporales. Verificar que funcione sin crashear.
        """
        code = """
        f: function string() = { return " Bminor"; }

        say_hi: function string(name: string) = {
            return "Hola " + name;
        }

        // ( " Bminor" + " Bminor" ) + ( " Bminor" + "!" )
        // " Bminor Bminor" + " Bminor!"
        // " Bminor Bminor Bminor!"
        print say_hi((f() + f()) + (f() + "!"));
        """
        expected = "Hola  Bminor Bminor Bminor!"
        self.assertEqual(self.get_output(code), expected)
