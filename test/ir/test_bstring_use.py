import unittest
from parser.model import *

from ir import IRGenerator, run_llvm_clang_ir
from utils import clear_errors, errors_detected


class TestStringUse(unittest.TestCase):
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
            # Nota: add_runtime=True es crucial para las funciones de string
            output = run_llvm_clang_ir(str(generated_ir), add_runtime=True)
            output = output.strip()  # Limpiar espacios en blanco al inicio/final
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
        """
        code = """
        main: function void () = {
            print "hello" + " world";
        }
        """
        _, output = self.get_ir_and_output(code)
        self.assertEqual(output, "hello world")

    # --- Test 2: Retornos de Función (Literal y Concatenación) ---
    def test_return_literal_and_concat(self):
        """
        Prueba que las funciones puedan retornar strings literales y
        el resultado de concatenaciones.
        """
        code = """
        get_literal: function string () = {
            return "Alpha";
        }

        get_concat: function string () = {
            return "Be" + "ta";
        }

        main: function void () = {
            s1: string = get_literal();
            s2: string = get_concat();
            print s1, " ", s2;
        }
        """
        _, output = self.get_ir_and_output(code)
        self.assertEqual(output, "Alpha Beta")

    # --- Test 3: Mutación de Parámetros y Temporales (Pass-by-Reference) ---
    def test_param_mutation_and_temporaries(self):
        """
        Prueba CRÍTICA: Verifica que:
        1. Modificar un parámetro tipo variable afecta al caller (paso por referencia).
        2. Modificar temporales (literales, binops, funcalls) no rompe el programa.
        """
        code = """
        modify: function void (s: string) = {
            s = "MODIFIED";
        }

        get_val: function string () = {
            return "returned";
        }

        main: function void () = {
            // Caso 1: Variable (Debe cambiar)
            v: string = "original";
            modify(v);
            print "Var: ", v, "\\n";

            // Caso 2: Literal (Se crea temp, se modifica, se descarta)
            modify("literal");
            print "Lit OK", "\\n";

            // Caso 3: BinOp (Temp de concatenación)
            modify("part1" + "part2");
            print "BinOp OK", "\\n";

            // Caso 4: FuncCall (Temp de retorno)
            modify(get_val());
            print "FuncCall OK", "\\n";
        }
        """
        # Nota: strip() elimina el último \n, pero los internos se mantienen
        expected_output = "Var: MODIFIED\nLit OK\nBinOp OK\nFuncCall OK"

        _, output = self.get_ir_and_output(code)
        # Normalizamos saltos de línea por si acaso (Windows/Unix)
        self.assertEqual(output.replace("\r\n", "\n"), expected_output)

    # --- Test 4: Retorno de Parámetro Modificado (Copia vs Ref) ---
    def test_return_modified_param(self):
        """
        Verifica la independencia entre la variable original modificada y
        el valor de retorno (debe ser una copia nueva).
        """
        code = """
        update_and_return: function string (target: string) = {
            // 1. Modifica la variable externa
            target = "Inside";

            // 2. Retorna el nuevo valor (debe hacer copy)
            return target;
        }

        main: function void () = {
            outer: string = "Outside";

            // Al llamar, 'outer' cambiará a "Inside", y 'res' recibirá una COPIA
            res: string = update_and_return(outer);

            // Cambiamos 'res' para asegurar que es memoria distinta a 'outer'
            res = res + "!";

            print "Outer: ", outer, "\\n";
            print "Res: ", res, "\\n";
        }
        """
        expected_output = "Outer: Inside\nRes: Inside!"

        _, output = self.get_ir_and_output(code)
        self.assertEqual(output.replace("\r\n", "\n"), expected_output)

    # --- Test 5: Llamadas Anidadas (Gestión de Memoria) ---
    def test_nested_calls(self):
        """
        Verifica que pasar el resultado de una función como parámetro a otra
        funcione correctamente (gestión de punteros temporales).
        """
        code = """
        surround: function string (s: string) = {
            return "[" + s + "]";
        }

        main: function void () = {
            // surround retorna un temporal que se pasa a la segunda llamada
            result: string = surround(surround("Core"));
            print result;
        }
        """
        _, output = self.get_ir_and_output(code)
        self.assertEqual(output, "[[Core]]")

    # --- Test 6: Variables Globales vs Locales (Shadowing y Ref) ---
    def test_global_vs_local_param(self):
        """
        Verifica:
        1. Shadowing: Parámetro con mismo nombre que global no afecta global.
        2. Pass Global: Pasar global como parámetro permite modificarla.
        """
        code = """
        g_str: string = "GLOBAL";

        change_local: function void (g_str: string) = {
            // Este 'g_str' es local (argumento), oculta a la global
            // Pero al ser string, modificamos el puntero local, no la global original
            // Espera... en BMinor string es Ref.
            // Si pasamos la global g_str aqui: change_local(g_str)
            // modificaria la global.

            // Pero aqui la prueba es pasar 'g_str' (la global) a un parametro llamado 'g_str'.
            g_str = "LOCAL_MOD";
            print "Inside: ", g_str, "\\n";
        }

        change_global_indirect: function void (ref: string) = {
            // Modificamos lo que nos pasen
            ref = "CHANGED";
        }

        main: function void () = {
            // 1. Shadowing / Argument passing
            // Pasamos g_str. La función recibe la referencia a g_str.
            // La función modifica esa referencia.
            change_local(g_str);
            print "Outside 1: ", g_str, "\\n";

            // 2. Pass global by ref explicito
            change_global_indirect(g_str);
            print "Outside 2: ", g_str, "\\n";
        }
        """

        # NOTA IMPORTANTE SOBRE ESTE TEST:
        # Dado que implementaste 'string' como paso por referencia siempre (i8**):
        # Cuando hacemos change_local(g_str), estamos pasando la dirección de g_str.
        # Dentro de change_local, asignamos "LOCAL_MOD". Esto modificará la variable original.
        #
        # Si tu intención era que 'change_local' tuviera una variable local INDEPENDIENTE
        # solo por llamarse igual, eso solo aplica si declaras 'var g_str: string' dentro.
        # Pero aqui es un argumento.
        #
        # Basado en tu lógica actual:
        # 1. change_local(g_str) -> modifica g_str a "LOCAL_MOD".
        # 2. change_global_indirect(g_str) -> modifica g_str a "CHANGED".

        expected_output = "Inside: LOCAL_MOD\nOutside 1: LOCAL_MOD\nOutside 2: CHANGED"

        _, output = self.get_ir_and_output(code)
        self.assertEqual(output.replace("\r\n", "\n"), expected_output)

    def test_reassignment_and_self_reference(self):
        """
        Prueba crítica para asegurar que no ocurra Use-After-Free.
        El valor antiguo debe ser liberado SOLO DESPUÉS de calcular el nuevo.
        """
        code = """
            main: function void () = {
                s: string = "Start";

                // 1. Reasignación simple (debe liberar "Start")
                s = "Middle";

                // 2. Auto-referencia (s = s + ...)
                // Si liberamos 's' antes de concatenar, esto imprime basura o crashea.
                s = s + "End";

                print s;
            }
            """
        _, output = self.get_ir_and_output(code)
        self.assertEqual(output, "MiddleEnd")

    def test_strings_in_loops(self):
        """
        Verifica la gestión de memoria dentro de estructuras de control.
        La variable 'inner' debe crearse y liberarse 3 veces.
        La variable 'acum' debe crecer correctamente.
        """
        code = """
            main: function void () = {
                i: integer;
                acum: string = "";

                for(i=0; i<3; i++) {
                    // Esta variable se crea y destruye en cada vuelta
                    inner: string = ".";

                    // Acumulador crece
                    acum = acum + inner;
                }
                print "Res:", acum;
            }
            """
        expected_output = "Res:..."
        _, output = self.get_ir_and_output(code)
        self.assertEqual(output, expected_output)

    def test_empty_and_escape_sequences(self):
        """
        Prueba casos borde: strings vacíos y caracteres especiales.
        """
        code = """
            main: function void () = {
                empty: string = "";

                // Concatenar con vacío no debe cambiar nada
                s: string = empty + "Line1";

                // Probar saltos de linea y tabuladores
                print s, "\\n", "\\tLine2";
            }
            """
        # Nota: Python interpreta \\n como \n real en el string esperado
        expected_output = "Line1\n\tLine2"
        _, output = self.get_ir_and_output(code)

        # Normalizamos saltos de línea
        output = output.replace("\r\n", "\n")
        self.assertEqual(output, expected_output)

    def test_strings_in_conditionals(self):
        """
        Verifica que el scope del IF limpie sus propias variables strings.
        """
        code = """
            main: function void () = {
                flag: boolean = true;
                outer: string = "Out";

                if (flag) {
                    inner: string = "In";
                    print outer, inner;
                } else {
                    inner_else: string = "Else";
                    print inner_else;
                }
                // 'inner' ya no existe aquí, el IR debe haber insertado el free
                print "Done";
            }
            """
        expected_output = "OutInDone"
        _, output = self.get_ir_and_output(code)
        self.assertEqual(output, expected_output)

    def test_String_nested_bin(self):
        code = """
            f: function string();

            say_hi: function string(name: string) = {
                return "Hola " + name;
            }

            main: function integer() = {
                print say_hi((f() + f()) + (f() + "!"));

                return 0;
            }

            f: function string() = {
                return " Bminor";
            }
            """
        expected_output = "Hola  Bminor Bminor Bminor!"
        _, output = self.get_ir_and_output(code)
        self.assertEqual(output, expected_output)
