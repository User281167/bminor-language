"""
Este archivo contiene la parte de generación de código intermedio con LLVMite.
El objetivo es tomar el AST generado por el parser y transformarlo en
código intermedio que pueda ser ejecutado por la maquina virtual de
LLVMite.
"""

import codecs
import uuid
from parser import Parser
from parser.model import *

from llvmlite import ir

from scanner import Lexer
from semantic import Check, Symtab
from utils import warning

from .array_runtime import ArrayRuntime
from .ir_type import IrTypes
from .math_runtime import MathRuntime
from .print_runtime import PrintRuntime
from .string_runtime import StringRuntime


class IRGenerator(Visitor):
    @classmethod
    def generate_from_code(cls, code: str) -> ir.Module:

        lexer = Lexer().tokenize(code)
        ast = Parser().parse(lexer)
        env, ast = Check.checker(ast, return_ast=True)

        return cls.Generate(ast, env, None)

    @classmethod
    def Generate(
        cls, n: Program, semantic_env: Symtab, module_name: str | None
    ) -> ir.Module:
        """
        Genera un módulo de IR a partir del AST y la tabla de símbolos.
        Visita todas las declaraciones y llama a accept() para cada una.
        Si hay un error en alguna de las declaraciones, imprime el error y sigue adelante.
        Devuelve el módulo de IR generado.

        args:
            n (Program): AST del programa, el ast generado por el analizador semántico ya que este inyecta los tipos en cada nodo
            semantic_env (Symtab): Tabla de símbolos
            module_name (str | None): Nombre del módulo de IR
        """

        gen = cls()

        if module_name is None:
            module_name = "main"

        module = ir.Module(name=module_name)

        # Crear función run, bloques y builder
        func_type = ir.FunctionType(IrTypes.i32, [])
        run_func = ir.Function(module, func_type, name="main")

        alloca_block = run_func.append_basic_block(name="alloca_entry")
        entry_block = run_func.append_basic_block(name="entry")

        alloca_builder = ir.IRBuilder(alloca_block)
        run_builder = ir.IRBuilder(entry_block)

        # Asignar atributos al generador
        setattr(gen, "module", module)
        setattr(gen, "global_scope", True)
        setattr(gen, "run_func", run_func)
        setattr(gen, "run_builder", run_builder)
        setattr(gen, "alloca_builder", alloca_builder)
        setattr(gen, "entry_block", entry_block)
        setattr(gen, "semantic_env", semantic_env)
        setattr(gen, "print_runtime", PrintRuntime(module))
        setattr(gen, "math_runtime", MathRuntime(module))
        setattr(gen, "string_runtime", StringRuntime(module))
        setattr(gen, "array_runtime", ArrayRuntime(module))
        setattr(gen, "_string_cache", {})

        # Entorno de símbolos contexto global
        env = Symtab("global")

        # renombrar función main del usuario, main_uid para evitar conflicto con nuestro main de entrada
        user_main = semantic_env.get("main", recursive=False)

        if user_main:
            user_main.name = f"main_{uuid.uuid4().hex}"

        # PRIMERA PASADA: Declarar todas las funciones
        for decl in n.body:
            try:
                if isinstance(decl, FuncDecl):
                    gen.declare_function(decl, env, run_builder.module)
            except Exception as e:
                print(f"Error al declarar la función {decl.name}: {repr(e)}")

        # Visitar todas las declaraciones
        # liberar string antes de salir
        free_strings = gen._run_block(
            n.body,
            env,
            run_builder,
            alloca_builder,
            run_func,
            is_global=True,
        )

        # SEGUNDA PASADA: Definir todas las funciones
        for decl in n.body:
            try:
                if isinstance(decl, FuncDecl):
                    gen.define_function(decl, env)
            except Exception as e:
                print(f"Error al definir la función {decl.name}: {repr(e)}")

        # salto explícito al bloque principal
        # Posicionar run_builder al final del bloque antes de emitir ret
        alloca_builder.branch(entry_block)
        run_builder.position_at_end(entry_block)

        user_main = semantic_env.get("main", recursive=False)

        if user_main:
            # si existe una función main, llamarla y retornar su valor si no return 0
            main_func = module.get_global(user_main.name)

            if main_func and isinstance(main_func, ir.Function):
                result = run_builder.call(main_func, [])
                gen._free_strings(run_builder, env, free_strings)

                if user_main.type == SimpleTypes.INTEGER.value:
                    # Llamar a main y retornar su resultado
                    run_builder.ret(result)
                else:
                    warning("Main function no return integer type")
                    run_builder.ret(IrTypes.i32_zero)
        else:
            # No hay main, retornar 0
            gen._free_strings(run_builder, env, free_strings)
            run_builder.ret(IrTypes.i32_zero)

        return module

    def _free_strings(self, builder: ir.IRBuilder, env: Symtab, strings_in_block: list):
        free_fn = self.string_runtime.free()
        null_ptr = ir.Constant(IrTypes.generic_pointer_t, None)

        for string in strings_in_block:
            loc = env.get(string.name, recursive=False)
            str_ptr = builder.load(loc, name=f"{string.name}_to_free")
            builder.call(free_fn, [str_ptr])
            builder.store(null_ptr, loc)

        strings_in_block.clear()

    def _run_block(
        self,
        n,
        env,
        builder,
        alloca,
        func,
        merge=None,
        is_global=False,
    ) -> list:
        """
        Ejecuta un bloque de sentencias, manejando el scope y liberando strings.

        Si en global_scope, declara las funciones primero.
        return:
            Si es global_scope, devuelve la lista strings en el bloque. ya que si se liberan en el bloque, se perderán las referencias globales.
            Si no es global_scope, devuelve una lista vacía.
        """
        strings_in_block = []

        for stmt in n or []:
            self.global_scope = is_global

            if isinstance(stmt, VarDecl) and stmt.type == SimpleTypes.STRING.value:
                strings_in_block.append(stmt)
            elif isinstance(stmt, (BreakStmt, ContinueStmt)):
                self._free_strings(builder, env, strings_in_block)

            ptr = stmt.accept(self, env, builder, alloca, func)

            # free string flotantes
            if (
                isinstance(stmt, (UnaryOper, BinOper, FuncCall))
                and stmt.type == SimpleTypes.STRING.value
            ):
                free = self.string_runtime.free()
                builder.call(free, [ptr])
            # liberar después de calcular return para evitar free prematuro
            elif isinstance(stmt, ReturnStmt):
                self._free_strings(builder, env, strings_in_block)

                if ptr:
                    builder.ret(ptr)

            if builder.block.is_terminated:
                break

        self.global_scope = is_global

        if is_global:
            return strings_in_block
        else:
            self._free_strings(builder, env, strings_in_block)

        if merge and not builder.block.is_terminated:
            builder.branch(merge)

        return []

    def comment(self, builder: ir.IRBuilder, msg: str):
        builder.comment("-" * len(msg))

        for line in msg.split("\n"):
            builder.comment(line)

        builder.comment("-" * len(msg))

    def _inject_fun_builtins(
        self,
        env: Symtab,
        builder: ir.IRBuilder,
        alloca: ir.IRBuilder,
        func: ir.Function,
    ):
        pass

    def _check_fun_call_builtins(
        self, n: FuncCall, builder: ir.IRBuilder, alloca: ir.IRBuilder
    ) -> bool:
        pass

    def _error(self, msg: str, lineno: int):
        pass

    def visit(
        self,
        n: BlockStmt,
        env: Symtab,
        builder: ir.IRBuilder,
        alloca: ir.IRBuilder,
        func: ir.Function,
    ):
        env_local = Symtab(f"block_{n.lineno}", parent=env)
        self._run_block(n.body, env_local, builder, alloca, func)

    # --- Statements

    def _set_array_location(
        self,
        n: Assignment,
        env: Symtab,
        builder: ir.IRBuilder,
        alloca: ir.IRBuilder,
        func: ir.Function,
    ):
        val = n.value.accept(self, env, builder, alloca, func)

        # Obtener puntero al array y el índice
        array_name = n.location.array.name
        array_var = env.get(array_name)

        if array_var.type == IrTypes.generic_pointer_t:
            array_ptr = array_var
        else:
            array_ptr = builder.load(array_var, name=f"{array_name}_ptr")

        index = n.location.index.accept(self, env, builder, alloca, func)

        if n.location.type == SimpleTypes.STRING.value:
            # Si es string, el valor YA ES un puntero (i8*)
            value_ptr = val
        else:
            # Si es básico (int/bool), necesitamos un puntero a él.
            # Crear espacio temporal en el stack
            temp_val = alloca.alloca(val.type, name="temp_assign_val")
            builder.store(val, temp_val)

            # Obtener el puntero genérico (i8*)
            value_ptr = builder.bitcast(temp_val, IrTypes.generic_pointer_t)

        # El runtime decide si hace free, strdup o memcpy.
        set_fn = self.array_runtime.set()
        builder.call(set_fn, [array_ptr, index, value_ptr])

        # retornar valor
        return val

    def visit(
        self,
        n: Assignment,
        env: Symtab,
        builder: ir.IRBuilder,
        alloca: ir.IRBuilder,
        func: ir.Function,
    ):
        if isinstance(n.location, VarLoc):
            loc = env.get(n.location.name)
        elif isinstance(n.location, ArrayLoc):
            return self._set_array_location(n, env, builder, alloca, func)

        if not n.location.type == SimpleTypes.STRING.value:
            new_value_ir = n.value.accept(self, env, builder, alloca, func)
            builder.store(new_value_ir, loc)
            return new_value_ir

        # Liberar el valor antiguo.
        old_str = builder.load(loc, "old_str_to_free")
        new_value_ir = n.value.accept(self, env, builder, alloca, func)

        # evitar copiar un puntero suelto, en vez de hacer free o copy, usar el result
        if isinstance(n.value, (BinOper, FuncCall)):
            new_ptr = new_value_ir
        else:
            copy_fn = self.string_runtime.copy()
            new_ptr = builder.call(copy_fn, [new_value_ir], "new_from_copy")

        builder.call(self.string_runtime.free(), [old_str])
        builder.store(new_ptr, loc)
        return new_ptr

    def visit(
        self,
        n: PrintStmt,
        env: Symtab,
        builder: ir.IRBuilder,
        alloca: ir.IRBuilder,
        func: ir.Function,
    ):
        fun_call = {
            str(SimpleTypes.INTEGER.value): self.print_runtime.print_int(),
            str(SimpleTypes.CHAR.value): self.print_runtime.print_char(),
            str(SimpleTypes.FLOAT.value): self.print_runtime.print_float(),
            str(SimpleTypes.BOOLEAN.value): self.print_runtime.print_bool(),
            str(SimpleTypes.STRING.value): self.print_runtime.print_string(),
        }

        for expr in n.expr or []:
            val = expr.accept(self, env, builder, alloca, func)

            fn = fun_call[str(expr.type)]
            builder.call(fn, [val])

            # liberar string temporal si aplica
            if expr.type == SimpleTypes.STRING.value and isinstance(
                expr, (BinOper, FuncCall)
            ):
                free = self.string_runtime.free()
                builder.call(free, [val])

    def visit(
        self,
        n: IfStmt,
        env: Symtab,
        builder: ir.IRBuilder,
        alloca: ir.IRBuilder,
        func: ir.Function,
    ):
        """
        Genera LLVM IR para una sentencia 'if' o 'if-else'.
        """
        self.comment(builder, "If statement")

        # Crear los bloques básicos necesarios
        then_block = func.append_basic_block(name="then")
        then_env = Symtab(f"if_{n.lineno}", parent=env)

        else_block = None
        else_env = None

        if n.else_branch:
            else_block = func.append_basic_block(name="else")
            else_env = Symtab(f"else_{n.lineno}", parent=env)

        # Block donde el control se une después del if/else
        merge_block = func.append_basic_block(name="merge")

        # Generar la rama condicional (cbranch)
        condition_value = n.condition.accept(self, env, builder, alloca, func)
        builder.cbranch(
            condition_value, then_block, else_block if else_block else merge_block
        )

        # Al final del bloque 'then', siempre debe haber una rama incondicional al 'merge_block'
        # Verificar que continue, break o return no hayan terminado el bloque
        builder.position_at_end(then_block)
        self._run_block(n.then_branch, then_env, builder, alloca, func, merge_block)

        if n.else_branch:
            builder.position_at_end(else_block)
            self._run_block(n.else_branch, else_env, builder, alloca, func, merge_block)

        # Volver al bloque de merge
        builder.position_at_end(merge_block)
        self.comment(builder, "End if statement")

    def add_loop_flags(self, env: Symtab, condition_block, merge_block, continue_block):
        env.add("loop_condition", condition_block)
        env.add("loop_merge", merge_block)
        env.add("loop_continue", continue_block)

    def get_loop_condition(self, env: Symtab):
        return env.get("loop_condition")

    def get_loop_merge(self, env: Symtab):
        return env.get("loop_merge")

    def get_loop_continue(self, env: Symtab):
        return env.get("loop_continue")

    def visit(
        self,
        n: ForStmt,
        env: Symtab,
        builder: ir.IRBuilder,
        alloca: ir.IRBuilder,
        func: ir.Function,
    ):
        self.comment(builder, "For loop")

        if n.init:
            n.init.accept(self, env, builder, alloca, func)

        # Crear los bloques básicos necesarios
        condition_block = func.append_basic_block(name="for_cond")
        loop_block = func.append_basic_block(name="for_body")
        update_block = func.append_basic_block(name="for_update")
        merge_block = func.append_basic_block(name="for_merge")

        # Verificar la condición
        builder.branch(condition_block)
        builder.position_at_end(condition_block)

        if n.condition:
            condition_value = n.condition.accept(self, env, builder, alloca, func)
            builder.cbranch(condition_value, loop_block, merge_block)
        else:  # Si no hay condición, el bucle se ejecuta siempre
            builder.branch(loop_block)

        # Contenido del bucle
        builder.position_at_end(loop_block)
        local_env = Symtab(f"for_{n.lineno}", parent=env)
        self.add_loop_flags(local_env, condition_block, merge_block, update_block)

        self._run_block(n.body, local_env, builder, alloca, func, update_block)
        builder.position_at_end(update_block)

        if n.update:
            n.update.accept(self, env, builder, alloca, func)

        builder.branch(condition_block)  # Volver a la condición

        builder.position_at_end(merge_block)
        self.comment(builder, "End for loop")

    def visit(
        self,
        n: WhileStmt,
        env: Symtab,
        builder: ir.IRBuilder,
        alloca: ir.IRBuilder,
        func: ir.Function,
    ):
        self.comment(builder, "While loop")

        # Crear los bloques básicos necesarios
        condition_block = func.append_basic_block(name="while_cond")
        loop_block = func.append_basic_block(name="while_body")
        merge_block = func.append_basic_block(name="while_end")

        # Verificar la condición
        builder.branch(condition_block)
        builder.position_at_end(condition_block)

        if n.condition:
            condition_value = n.condition.accept(self, env, builder, alloca, func)
            builder.cbranch(condition_value, loop_block, merge_block)
        else:  # Si no hay condición, el bucle se ejecuta siempre
            builder.branch(loop_block)

        # Contenido del bucle
        builder.position_at_end(loop_block)

        local_env = Symtab(f"while_{n.lineno}", parent=env)
        self.add_loop_flags(local_env, condition_block, merge_block, condition_block)
        self._run_block(n.body, local_env, builder, alloca, func, condition_block)

        builder.position_at_end(merge_block)
        self.comment(builder, "End while loop")

    def visit(
        self,
        n: DoWhileStmt,
        env: Symtab,
        builder: ir.IRBuilder,
        alloca: ir.IRBuilder,
        func: ir.Function,
    ):
        self.comment(builder, "Do while loop")

        # Crear los bloques básicos necesarios
        loop_block = func.append_basic_block(name="do_while")
        condition_block = func.append_basic_block(name="do_while_cond")
        merge_block = func.append_basic_block(name="do_while_end")

        # Ejecutar al menos una vez
        builder.branch(loop_block)
        builder.position_at_end(condition_block)

        if n.condition:
            condition_value = n.condition.accept(self, env, builder, alloca, func)
            builder.cbranch(condition_value, loop_block, merge_block)
        else:  # Si no hay condición, el bucle se ejecuta siempre
            builder.branch(loop_block)

        # Contenido del bucle
        builder.position_at_end(loop_block)

        local_env = Symtab(f"do_while_{n.lineno}", parent=env)
        self.add_loop_flags(local_env, condition_block, merge_block, condition_block)
        self._run_block(n.body, local_env, builder, alloca, func, condition_block)

        builder.position_at_end(merge_block)
        self.comment(builder, "End do while loop")

    def visit(
        self,
        n: ContinueStmt,
        env: Symtab,
        builder: ir.IRBuilder,
        alloca: ir.IRBuilder,
        func: ir.Function,
    ):
        self.comment(builder, "Continue")
        continue_block = self.get_loop_continue(env)
        builder.branch(continue_block)

    def visit(
        self,
        n: BreakStmt,
        env: Symtab,
        builder: ir.IRBuilder,
        alloca: ir.IRBuilder,
        func: ir.Function,
    ):
        self.comment(builder, "Break")
        block = self.get_loop_merge(env)
        builder.branch(block)

    def visit(
        self,
        n: ReturnStmt,
        env: Symtab,
        builder: ir.IRBuilder,
        alloca: ir.IRBuilder,
        func: ir.Function,
    ):
        self.comment(builder, "Return")

        if n.expr is None:
            self.default_return(builder, func.type)
            return None

        if not builder.block.is_terminated:
            val = n.expr.accept(self, env, builder, alloca, func)

            if isinstance(n.expr, VarLoc) and isinstance(n.expr.type, ArrayType):
                # Verificar si es un parámetro de la función actual
                loc_ptr = env.get(n.expr.name)

                if loc_ptr.type == IrTypes.generic_pointer_t:
                    array_ptr = loc_ptr  # ya es un puntero de referencia
                elif loc_ptr.type == IrTypes.generic_pointer_t.as_pointer():
                    array_ptr = builder.load(
                        loc_ptr, name=f"{n.expr.name}_ptr_for_call"
                    )

                return array_ptr
            elif n.expr.type == SimpleTypes.STRING.value and isinstance(
                n.expr, (VarLoc, Literal)
            ):
                copy = self.string_runtime.copy()
                val = builder.call(copy, [val], "return_string_copy")

            return val

    # --- Declaration

    def visit(
        self,
        n: Declaration,
        env: Symtab,
        builder: ir.IRBuilder,
        alloca: ir.IRBuilder,
        func: ir.Function,
    ):
        pass

    def __get_literal_value(self, n):
        if not isinstance(n, (Literal, UnaryOper, BinOper)):
            return

        if isinstance(n, Literal):
            return n.value
        elif isinstance(n, UnaryOper):
            val = self.__get_literal_value(n.expr)

            if val is None:
                return

            if n.oper == "+":
                return val
            elif n.oper == "-":
                return -val
            elif n.oper == "!":
                return not val
        elif isinstance(n, BinOper):
            left = self.__get_literal_value(n.left)

            if left is None:
                return

            right = self.__get_literal_value(n.right)

            if right is None:
                return

            if n.oper == "+":
                return left + right
            elif n.oper == "-":
                return left - right
            elif n.oper == "*":
                return left * right
            elif n.oper == "/":
                return left / right
            elif n.oper == "%":
                return left % right
            elif n.oper == "^":
                return left**right
            elif n.oper == "==":
                return left == right
            elif n.oper == "!=":
                return left != right
            elif n.oper == ">":
                return left > right
            elif n.oper == "<":
                return left < right
            elif n.oper == ">=":
                return left >= right
            elif n.oper == "<=":
                return left <= right
            elif n.oper == "LAND":
                return left and right
            elif n.oper == "||":
                return left or right

        return None

    def _get_literal_value(self, n):
        val = self.__get_literal_value(n)

        if val is None:
            return

        if n.type == SimpleTypes.INTEGER.value:
            return int(val)
        elif n.type == SimpleTypes.FLOAT.value:
            return float(val)
        elif n.type == SimpleTypes.CHAR.value:
            decoded = codecs.decode(val, "unicode_escape")  # '\\n' -> '\n'
            return ord(decoded)
        elif n.type == SimpleTypes.BOOLEAN.value:
            return bool(val)

        return val

    def _auto_array(self, n, env, builder, alloca, func):
        arr = ArrayDecl(
            n.name,
            n.type,
            n.value,
        )
        self.visit(arr, env, builder, alloca, func)

    def visit(
        self,
        n: VarDecl,
        env: Symtab,
        builder: ir.IRBuilder,
        alloca: ir.IRBuilder,
        func: ir.Function,
    ):
        if isinstance(n, AutoDecl) and isinstance(n.value, list):
            self._auto_array(n, env, builder, alloca, func)
            return

        llvm_type = IrTypes.get_type(n.type)
        val = self._get_literal_value(n.value)

        if self.global_scope:
            var = ir.GlobalVariable(self.module, llvm_type, n.name)

            if val is None:
                var.initializer = ir.Constant(llvm_type, 0)
            elif n.type == SimpleTypes.INTEGER.value:
                var.initializer = IrTypes.const_int(val)
            elif n.type == SimpleTypes.FLOAT.value:
                var.initializer = IrTypes.const_float(val)
            elif n.type == SimpleTypes.CHAR.value:
                var.initializer = IrTypes.const_char(val)
            elif n.type == SimpleTypes.BOOLEAN.value:
                var.initializer = IrTypes.const_bool(val)

            var.linkage = "dso_local"
        else:
            var = alloca.alloca(
                llvm_type, name=n.name
            )  # no agregar nombre ya que puede redefinir una var global

        var.align = IrTypes.get_align(n.type) or 0

        if n.type != SimpleTypes.STRING.value:
            # Asignar el valor si no no era un literal
            if not n.value:
                builder.store(ir.Constant(llvm_type, 0), var)
            elif not val is None:
                if not self.global_scope:
                    builder.store(ir.Constant(llvm_type, val), var)
            else:
                val = n.value.accept(self, env, builder, alloca, func)
                builder.store(val, var)
        else:
            var.align = 8
            var.initializer = ir.Constant(llvm_type, None)

            if n.value:
                initial_val_ptr = n.value.accept(self, env, builder, alloca, func)

                # evitar copiar un puntero suelto, en vez de hacer free o copy, usar el result
                if isinstance(n.value, (BinOper, FuncCall)):
                    string_ptr = initial_val_ptr
                else:
                    # si es literal o variable, copiar
                    copy_fn = self.string_runtime.copy()
                    string_ptr = builder.call(copy_fn, [initial_val_ptr])
            else:
                # cadena vacía por defecto
                initial_val_ptr = self._create_global_string("", builder)
                copy_fn = self.string_runtime.copy()
                string_ptr = builder.call(copy_fn, [initial_val_ptr])

            builder.store(string_ptr, var)

        env.add(n.name, var)

    def _set_arr_index(
        self,
        array_ptr,
        val_ast,
        index,
        env,
        builder,
        alloca,
        func,
        is_string=False,
        temp_alloca=None,
        free=False,
    ):
        index_llvm = IrTypes.const_int(index)
        value_llvm = val_ast.accept(self, env, builder, alloca, func)
        set_fn = self.array_runtime.set()  # El set unificado

        if is_string:
            # Tipo String: Pasamos el puntero directo a la cadena
            value_ptr = value_llvm
        else:
            # Tipo Básico: Reutilizamos el alloca y lo usamos para el store/bitcast

            if temp_alloca is None:
                # Esto NO DEBERÍA pasar si la lógica del llamador es correcta.
                # Si pasa, significa que se llamó a _set_arr_index para un tipo básico sin preparar el alloca.
                raise Exception(
                    "Internal Error: Missing reusable alloca for array initialization."
                )

            # Almacenar el valor en el alloca REUTILIZABLE
            builder.store(value_llvm, temp_alloca)

            # Bitcast a puntero genérico (i8*)
            value_ptr = builder.bitcast(
                temp_alloca, IrTypes.generic_pointer_t, name="value_ptr"
            )

        # Llamada unificada a _bminor_array_set
        builder.call(set_fn, [array_ptr, index_llvm, value_ptr])

        if free:
            free_fn = self.string_runtime.free()
            builder.call(free_fn, [value_ptr])

    def visit(
        self,
        n: ArrayDecl,
        env: Symtab,
        builder: ir.IRBuilder,
        alloca: ir.IRBuilder,
        func: ir.Function,
    ):
        # Loc para el Puntero (i8**)
        if self.global_scope:
            var = ir.GlobalVariable(self.module, IrTypes.generic_pointer_t, n.name)
            var.initializer = IrTypes.null_pointer
            var.linkage = "dso_local"
        else:
            var = alloca.alloca(IrTypes.generic_pointer_t, name=n.name)

        if isinstance(n.type.size, int):
            # Auto array posible size como entero de len(n.value)
            size = IrTypes.const_int(n.type.size)
        else:
            size = n.type.size.accept(self, env, builder, alloca, func)

        element_size = IrTypes.get_align(n.type.base)
        element_size = IrTypes.const_int(element_size)

        list_size = len(n.value) if n.value else 0
        list_size = IrTypes.const_int(list_size)

        is_string = n.type.base == SimpleTypes.STRING.value
        is_string = IrTypes.const_bool(is_string)

        env.add(n.name, var)

        # para inicializar en función
        load_var = env.get(n.name)

        new_fn = self.array_runtime.new()
        array_ptr = builder.call(new_fn, [size, list_size, element_size, is_string])
        builder.store(array_ptr, load_var)

        temp_alloca_reusable = None

        if n.value:
            # Si NO es string, preparamos un alloca único para la inicialización
            if n.type.base != SimpleTypes.STRING.value:
                # Asume que 'alloca' es el IRBuilder para el bloque alloca_entry
                element_llvm_type = IrTypes.get_type(n.type.base)
                temp_alloca_reusable = alloca.alloca(
                    element_llvm_type, name="temp_arr_init_val"
                )

            for i, val_ast in enumerate(n.value):
                free = is_string and isinstance(val_ast, (BinOper, FuncCall))

                self._set_arr_index(
                    array_ptr,
                    val_ast,
                    i,
                    env,
                    builder,
                    alloca,
                    func,
                    is_string=n.type.base == SimpleTypes.STRING.value,
                    temp_alloca=temp_alloca_reusable,  # <-- ¡PASAMOS EL ALLOCA REUTILIZABLE!
                    free=free,
                )

    # El visitor continúa desde aquí.
    def default_return(self, builder: ir.IRBuilder, ret_type: ir.Type | None):
        """
        Genera un return por defecto si no hay uno explícito.
        """
        if not builder.block.is_terminated:
            if ret_type == ir.VoidType() or ret_type is None:
                builder.ret_void()
            elif ret_type == IrTypes.i32:
                builder.ret(IrTypes.i32_zero)
            elif ret_type == IrTypes.f32:
                builder.ret(IrTypes.const_float(0.0))
            elif ret_type == IrTypes.i8:
                builder.ret(IrTypes.const_char("\0"))
            elif ret_type == IrTypes.i1:
                builder.ret(IrTypes.const_bool(False))

    def declare_function(self, n: FuncDecl, env: Symtab, module):
        # Obtener tipo de retorno y parámetros
        # Crear tipo de función LLVM
        # Crear la función LLVM (pero sin cuerpo)
        ret_type = IrTypes.get_type(n.return_type)
        param_types = []

        for p in n.params:
            llvm_type = IrTypes.get_type(p.type)

            # Si el parámetro es STRING, se pasa por REFERENCIA (i8**),
            # por lo que el tipo de argumento es puntero al puntero del string.
            if isinstance(p.type, ArrayType):
                param_types.append(llvm_type)
            elif p.type == SimpleTypes.STRING.value:
                param_types.append(llvm_type.as_pointer())  # Convierte i8* a i8**
            else:
                param_types.append(llvm_type)

        existing_entry = env.get(n.name, recursive=False)

        if existing_entry and isinstance(existing_entry, ir.Function):
            return

        func_type = ir.FunctionType(ret_type, param_types)
        func_body = ir.Function(module, func_type, name=n.name)

        env.add(n.name, func_body)

    def define_function(self, n: FuncDecl, env: Symtab):
        if n.body is None:
            return

        self.global_scope = False

        # Buscar la función en la tabla de símbolos
        # Obtener tipo de retorno y parámetros
        # Crear bloques y builder para el cuerpo
        func_body = env.get(n.name, recursive=False)
        ret_type = IrTypes.get_type(n.return_type)
        param_types = [IrTypes.get_type(p.type) for p in n.params]

        alloca_block = func_body.append_basic_block(name="alloca")
        entry_block = func_body.append_basic_block(name="entry")

        alloca_builder = ir.IRBuilder(alloca_block)
        body_builder = ir.IRBuilder(entry_block)

        # Entorno de la función
        local_env = Symtab(n.name, parent=env)

        # Asignar parámetros a variables locales
        for i, param in enumerate(n.params):
            llvm_arg = func_body.args[i]

            if param.type == SimpleTypes.STRING.value or isinstance(
                param.type, ArrayType
            ):
                # pasar por referencia
                local_env.add(param.name, llvm_arg)
            else:
                # pasar por valor
                llvm_type = llvm_arg.type
                ptr = alloca_builder.alloca(llvm_type, name=param.name)
                ptr.align = IrTypes.get_align(param.type)

                body_builder.store(llvm_arg, ptr)
                local_env.add(param.name, ptr)

        self._run_block(n.body, local_env, body_builder, alloca_builder, func_body)

        alloca_builder.branch(entry_block)
        self.default_return(body_builder, ret_type)  # asegurar return al final

    def visit(
        self,
        n: FuncDecl,
        env: Symtab,
        builder: ir.IRBuilder,
        alloca: ir.IRBuilder,
        func: ir.Function,
    ):
        pass

    def visit(self, n: Param, builder: ir.IRBuilder, alloca: ir.IRBuilder, env: Symtab):
        pass

    # --- Expressions

    def visit(
        self,
        n: Literal,
        env: Symtab,
        builder: ir.IRBuilder,
        alloca: ir.IRBuilder,
        func: ir.Function,
    ):
        """
        Devuelve Constant
        """

        if n.type == SimpleTypes.INTEGER.value:
            return IrTypes.const_int(n.value)
        elif n.type == SimpleTypes.FLOAT.value:
            return IrTypes.const_float(n.value)
        elif n.type == SimpleTypes.CHAR.value:
            return IrTypes.const_char(n.value)
        elif n.type == SimpleTypes.BOOLEAN.value:
            return IrTypes.const_bool(n.value)
        elif n.type == SimpleTypes.STRING.value:
            return self._create_global_string(n.value, builder)

    def _create_global_string(self, py_string: str, builder: ir.IRBuilder) -> ir.Value:
        """
        Crea (o recupera de la caché) una constante de string global
        y devuelve un puntero i8* a ella.

        Corregir escape sequences en el string y agregar null terminator.
        """
        interpreted_string = py_string.encode("utf-8").decode("unicode_escape")
        str_val = interpreted_string.encode("utf8") + b"\00"

        if str_val in self._string_cache:
            global_var = self._string_cache[str_val]
        else:
            # Crear una nueva variable global para el string
            str_type = ir.ArrayType(IrTypes.i8, len(str_val))
            name = f".str.{len(self._string_cache)}"

            global_var = ir.GlobalVariable(self.module, str_type, name=name)
            global_var.linkage = "internal"  # Solo visible dentro de este módulo
            global_var.global_constant = True
            global_var.initializer = ir.Constant(str_type, bytearray(str_val))

            self._string_cache[str_val] = global_var

        # Obtener un puntero al primer elemento (i8*)
        zero = IrTypes.i32_zero
        ptr = builder.gep(global_var, [zero, zero], name=f".str_ptr")

        return ptr

    def visit(
        self,
        n: SimpleType,
        env: Symtab,
        builder: ir.IRBuilder,
        alloca: ir.IRBuilder,
        func: ir.Function,
    ):
        pass

    def visit(
        self,
        n: ArrayType,
        env: Symtab,
        builder: ir.IRBuilder,
        alloca: ir.IRBuilder,
        func: ir.Function,
    ):
        pass

    def _visit_inc_dec_common(
        self,
        n: Increment | Decrement,
        env: Symtab,
        builder: ir.IRBuilder,
        alloca: ir.IRBuilder,
        func: ir.Function,
    ):
        if isinstance(n.location, VarLoc):
            ptr = env.get(n.location.name)
        else:
            ptr = n.location.accept(self, env, builder, alloca, func)

        if type(ptr) == type(IrTypes.i32_zero) or type(ptr) == ir.Instruction:
            val = ptr
        else:
            val = builder.load(ptr)

        if isinstance(n, Increment):
            incremented = builder.add(val, IrTypes.const_int(1))
        else:
            incremented = builder.sub(val, IrTypes.const_int(1))

        if isinstance(n.location, VarLoc):
            builder.store(incremented, ptr)

        if n.postfix:
            return val  # devuelve el valor original

        return incremented  # devuelve el valor incrementado

    def visit(
        self,
        n: Increment,
        env: Symtab,
        builder: ir.IRBuilder,
        alloca: ir.IRBuilder,
        func: ir.Function,
    ):
        return self._visit_inc_dec_common(n, env, builder, alloca, func)

    def visit(
        self,
        n: Decrement,
        env: Symtab,
        builder: ir.IRBuilder,
        alloca: ir.IRBuilder,
        func: ir.Function,
    ):
        return self._visit_inc_dec_common(n, env, builder, alloca, func)

    def _concatenate_string(
        self,
        n: BinOper,
        env: Symtab,
        builder: ir.IRBuilder,
        alloca: ir.IRBuilder,
        func: ir.Function,
    ) -> ir.Value:
        """
        Genera el IR para concatenar dos strings, que pueden ser literales (i8*)
        o el resultado de otra operación (BMinorString*).
        """
        left = n.left.accept(self, env, builder, alloca, func)
        right = n.right.accept(self, env, builder, alloca, func)

        # Obtenemos las funciones del runtime
        concat_fn = self.string_runtime.concat()
        free_fn = self.string_runtime.free()

        result = builder.call(concat_fn, [left, right], "concat_result")

        if isinstance(n.left, (BinOper, FuncCall)):
            builder.call(free_fn, [left])
        if isinstance(n.right, (BinOper, FuncCall)):
            builder.call(free_fn, [right])

        return result

    def visit(
        self,
        n: BinOper,
        env: Symtab,
        builder: ir.IRBuilder,
        alloca: ir.IRBuilder,
        func: ir.Function,
    ):
        is_int = not (n.left.type == SimpleTypes.FLOAT.value)

        if n.type == SimpleTypes.STRING.value and n.oper == "+":
            return self._concatenate_string(n, env, builder, alloca, func)

        left = n.left.accept(self, env, builder, alloca, func)
        right = n.right.accept(self, env, builder, alloca, func)

        if n.oper == "^":
            fn = self.math_runtime.pow_int()
            return builder.call(fn, [left, right])

        fn_math = {
            "+": builder.add if is_int else builder.fadd,
            "-": builder.sub if is_int else builder.fsub,
            "*": builder.mul if is_int else builder.fmul,
            "/": builder.sdiv if is_int else builder.fdiv,
            "%": builder.srem if is_int else builder.frem,
        }

        # ordered para evitar problemas con NaN
        fn_log = {
            "<=": (builder.icmp_signed if is_int else builder.fcmp_ordered),
            "<": (builder.icmp_signed if is_int else builder.fcmp_ordered),
            ">=": (builder.icmp_signed if is_int else builder.fcmp_ordered),
            ">": (builder.icmp_signed if is_int else builder.fcmp_ordered),
            "==": (builder.icmp_signed if is_int else builder.fcmp_ordered),
            "!=": (builder.icmp_signed if is_int else builder.fcmp_ordered),
        }

        fn_bool = {
            "LAND": builder.and_,
            "LOR": builder.or_,
        }

        if n.oper in fn_math:
            return fn_math[n.oper](left, right)
        elif n.oper in fn_log:
            return fn_log[n.oper](n.oper, left, right)
        elif n.oper in fn_bool:
            return fn_bool[n.oper](left, right)

    def visit(
        self,
        n: UnaryOper,
        env: Symtab,
        builder: ir.IRBuilder,
        alloca: ir.IRBuilder,
        func: ir.Function,
    ):
        val = n.expr.accept(self, env, builder, alloca, func)

        if n.oper == "+":
            return val
        elif n.oper == "-":
            if n.expr.type == SimpleTypes.INTEGER.value:
                return builder.neg(val)

            return builder.fsub(IrTypes.const_float(0), val)
        elif n.oper == "!":
            return builder.not_(val)

    def visit(
        self,
        n: FuncCall,
        env: Symtab,
        builder: ir.IRBuilder,
        alloca: ir.IRBuilder,
        func: ir.Function,
    ):
        fun_name = env.get(n.name)
        args = []
        free_ref_temps = (
            []
        )  # Para allocas temporales de strings pasados por referencia (i8**)

        for i, arg in enumerate(n.args):
            if arg.type == SimpleTypes.STRING.value:
                if isinstance(arg, VarLoc):
                    # Variable (Ej. set_str(var)) -> Pasa su alloca (i8**)
                    # El scope es el encargado de liberar.
                    loc = env.get(arg.name)
                    args.append(loc)
                else:
                    # Expresión (Ej. fun("hola")) pasada a referencia (i8**)

                    # Generar el valor temporal (P_TEMP = i8*)
                    # Este puede ser un literal o un resultado de concatenación.
                    val = arg.accept(self, env, builder, alloca, func)

                    if isinstance(arg, Literal):
                        # NO es memoria del heap. Se crea una copia para evitar free dentro de función.
                        val_to_pass = builder.call(self.string_runtime.copy(), [val])
                    elif isinstance(arg, (BinOper, FuncCall)):
                        # ya es un puntero en heap
                        val_to_pass = val
                    else:
                        # En caso de otras opereaciones con string
                        val_to_pass = builder.call(self.string_runtime.copy(), [val])

                    # Crear alloca temporal (i8**) en el scope
                    temp_ptr = alloca.alloca(val_to_pass.type, name="temp_ref_arg")
                    builder.store(val_to_pass, temp_ptr)

                    # Pasar la REFERENCIA (i8**)
                    args.append(temp_ptr)

                    # manejar la fuga de memoria
                    free_ref_temps.append(temp_ptr)
            elif isinstance(arg, VarLoc) and isinstance(arg.type, ArrayType):
                loc_ptr = env.get(arg.name)

                # Chequea si el tipo es i8*
                # Si loc_ptr es de tipo i8** (es una variable local como 'x') -> Cárgalo.
                # Genera la instrucción de carga: %"a_ptr_for_call" = load i8*, i8** %"a"
                if loc_ptr.type == IrTypes.generic_pointer_t:
                    array_ptr = loc_ptr  # ya es un puntero de referencia
                elif loc_ptr.type == IrTypes.generic_pointer_t.as_pointer():
                    array_ptr = builder.load(loc_ptr, name=f"{arg.name}_ptr_for_call")

                args.append(array_ptr)
            elif not arg.type == SimpleTypes.STRING.value:
                # Tipos primitivos (int, float, bool, etc.)
                args.append(arg.accept(self, env, builder, alloca, func))

        val = builder.call(fun_name, args)

        # limpiar los temporales
        for ptr in free_ref_temps:
            str_to_free = builder.load(ptr, name="arg_temp_to_free")
            builder.call(self.string_runtime.free(), [str_to_free])

        return val

    def visit(
        self,
        n: Location,
        env: Symtab,
        builder: ir.IRBuilder,
        alloca: ir.IRBuilder,
        func: ir.Function,
    ):
        pass

    def visit(
        self,
        n: VarLoc,
        env: Symtab,
        builder: ir.IRBuilder,
        alloca: ir.IRBuilder,
        func: ir.Function,
    ):
        """
        Obtener Puntero de la variable
        """
        var = env.get(n.name)
        return builder.load(var, name=n.name)

    def visit(
        self,
        n: ArrayLoc,
        env: Symtab,
        builder: ir.IRBuilder,
        alloca: ir.IRBuilder,
        func: ir.Function,
    ):
        array_var = env.get(n.array.name)

        # no cargar nuevamente el array
        if array_var.type == IrTypes.generic_pointer_t:
            array_ptr = array_var
        else:
            array_ptr = builder.load(array_var, name=f"{n.array.name}_struct_ptr")

        index = n.index.accept(self, env, builder, alloca, func)

        # Obtener el tipo de retorno LLVM
        return_type = IrTypes.get_type(n.type)

        # crear variable local
        temp_alloca = alloca.alloca(return_type, name="temp_get_val")

        # Castear al puntero genérico (i8*) para el runtime
        destination_ptr = builder.bitcast(
            temp_alloca, IrTypes.generic_pointer_t, name="dest_ptr"
        )

        # Cargar el valor
        get_fn = self.array_runtime.get()
        builder.call(get_fn, [array_ptr, index, destination_ptr])

        return builder.load(temp_alloca, name="array_element")
