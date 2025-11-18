"""
Este archivo contiene la parte de generación de código intermedio con LLVMite.
El objetivo es tomar el AST generado por el parser y transformarlo en
código intermedio que pueda ser ejecutado por la maquina virtual de
LLVMite.
"""

import codecs
from parser.model import *

from llvmlite import ir

from semantic import Symtab
from utils import warning

from .ir_type import IrTypes
from .math_runtime import MathRuntime
from .print_runtime import PrintRuntime
from .string_runtime import StringRuntime


class IRGenerator(Visitor):
    @classmethod
    def generate_from_code(cls, code: str) -> ir.Module:
        from parser import Parser

        from scanner import Lexer
        from semantic import Check

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

        # Crear función run
        func_type = ir.FunctionType(ir.IntType(32), [])
        run_func = ir.Function(module, func_type, name="main")

        # Crear bloques en orden correcto
        alloca_block = run_func.append_basic_block(name="alloca_entry")
        entry_block = run_func.append_basic_block(name="entry")

        # Builder para allocas
        alloca_builder = ir.IRBuilder(alloca_block)

        # Builder para instrucciones normales
        run_builder = ir.IRBuilder(entry_block)

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
        setattr(gen, "_string_cache", {})

        # Entorno de símbolos
        env = Symtab("global")

        # Visitar todas las declaraciones
        for decl in n.body:
            try:
                gen.global_scope = True
                decl.accept(gen, env, run_builder, alloca_builder, run_func)
            except Exception as e:
                # print("Error decl = ")
                # decl.pretty()
                print(repr(e))
                print(e)

        try:
            gen._add_functions(n.body, env, run_builder, alloca_builder, run_func)
        except Exception as e:
            print(repr(e))
            print(e)

        alloca_builder.branch(entry_block)  # salto explícito al bloque principal
        # Posicionar run_builder al final del bloque antes de emitir ret
        run_builder.position_at_end(entry_block)

        main_env = semantic_env.get("main", recursive=False)

        if main_env:
            # si existe una función main, llamarla y retornar su valor si no return 0
            main_func = module.get_global(main_env.name + "_" + main_env.uid)

            if main_func and isinstance(main_func, ir.Function):
                # Llamar a main y retornar su resultado
                result = run_builder.call(main_func, [])

                if main_env.type == SimpleTypes.INTEGER.value:
                    run_builder.ret(result)
                else:
                    warning("Main function no return integer type")
                    run_builder.ret(ir.Constant(IrTypes.int32, 0))
        else:
            # No hay main, retornar 0
            run_builder.ret(ir.Constant(IrTypes.int32, 0))

        return module

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
        pass

    # --- Statements

    def visit(
        self,
        n: Assignment,
        env: Symtab,
        builder: ir.IRBuilder,
        alloca: ir.IRBuilder,
        func: ir.Function,
    ):
        # Obtener la variable de destino (loc).
        # 'loc' es un puntero a dónde se guarda el valor (BMinorString** o i32* etc.)
        if isinstance(n.location, VarLoc):
            loc = env.get(n.location.name)
            # Para globales, env.get puede devolver una tupla (var, node). Nos quedamos con la var.
            # if isinstance(loc, tuple):
            #     loc = loc[0]
        # ... (añadir lógica para ArrayLoc si es necesario) ...

        # =====================================================================
        # Distinguir entre tipos de string y tipos simples
        # =====================================================================
        if n.location.type == SimpleTypes.STRING.value:
            # --- LÓGICA ESPECIAL PARA LA ASIGNACIÓN DE STRINGS ---

            # 1. Cargar y liberar el valor ANTIGUO.
            #    Primero, cargamos el BMinorString* que está guardado en 'loc'.
            old_bminor_string_ptr = builder.load(loc, "old_value_to_free")
            #    Ahora sí, liberamos el puntero que acabamos de cargar.
            builder.call(self.string_runtime.free(), [old_bminor_string_ptr])

            # 2. Calcular el NUEVO valor (el lado derecho de la asignación).
            new_value_ir = n.value.accept(self, env, builder, alloca, func)

            # 3. Asegurarse de que el nuevo valor sea un BMinorString* nuevo e independiente.
            if new_value_ir.type == ir.PointerType(ir.IntType(8)):
                # Si el nuevo valor es un literal (i8*), creamos un BMinorString desde él.
                from_literal_fn = self.string_runtime.from_literal()
                final_new_ptr = builder.call(
                    from_literal_fn, [new_value_ir], "new_from_literal"
                )
            else:
                # Si el nuevo valor ya era un BMinorString* (de otra variable, etc.),
                # creamos una COPIA para mantener la semántica de valor.
                # Este es el caso de: str = var;
                copy_fn = self.string_runtime.copy()
                final_new_ptr = builder.call(copy_fn, [new_value_ir], "new_from_copy")

            # 4. Guardar el puntero al nuevo valor en la variable 'loc'.
            builder.store(final_new_ptr, loc)

        else:
            # --- LÓGICA PARA TIPOS SIMPLES ---
            new_value_ir = n.value.accept(self, env, builder, alloca, func)
            builder.store(new_value_ir, loc)

        # builder.store(val, loc)

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

        func_bminor_print = self.string_runtime.print()

        for expr in n.expr or []:
            val = expr.accept(self, env, builder, alloca, func)

            if (
                expr.type == SimpleTypes.STRING.value
                and val.type == self.string_runtime.get_string_type_pointer()
            ):
                builder.call(func_bminor_print, [val])

                if isinstance(expr, UnaryOper):
                    free = self.string_runtime.free()
                    builder.call(free, [val])

                continue

            fn = fun_call[str(expr.type)]
            builder.call(fn, [val])

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

        # El 'merge' block es donde el control se une después del if/else
        merge_block = func.append_basic_block(name="merge")

        condition_value = n.condition.accept(self, env, builder, alloca, func)

        # Generar la rama condicional (cbranch)
        builder.cbranch(
            condition_value, then_block, else_block if else_block else merge_block
        )

        builder.position_at_end(then_block)

        try:
            self._add_functions(n.then_branch or [], then_env, builder, alloca, func)
        except Exception as e:
            pass

        # Generar las sentencias dentro del bloque 'then'
        for stmt in n.then_branch:
            if not builder.block.is_terminated:
                stmt.accept(self, then_env, builder, alloca, func)

        # Al final del bloque 'then', siempre debe haber una rama incondicional al 'merge_block'
        # esto ya que continue o break pueden haber terminado el bloque
        if not builder.block.is_terminated:
            builder.branch(merge_block)

        # Si existe una rama 'else', posicionarse y generar su código
        if n.else_branch:
            builder.position_at_end(else_block)

            try:
                self._add_functions(
                    n.else_branch or [], else_env, builder, alloca, func
                )
            except Exception as e:
                pass

            # Generar las sentencias dentro del bloque 'else'
            for stmt in n.else_branch:
                if not builder.block.is_terminated:
                    stmt.accept(self, else_env, builder, alloca, func)

            # Al final del bloque 'else', siempre debe haber una rama incondicional al 'merge_block'
            # esto ya que continue o break pueden haber terminado el bloque
            if not builder.block.is_terminated:
                builder.branch(merge_block)

        # Posicionarse al final del bloque 'merge'
        # Cualquier código que siga al 'if' comenzará aquí.
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

        try:
            self._add_functions(n.body or [], local_env, builder, alloca, func)
        except Exception as e:
            pass

        for stmt in n.body or []:
            if not builder.block.is_terminated:
                stmt.accept(self, local_env, builder, alloca, func)

        if not builder.block.is_terminated:
            builder.branch(update_block)  # Ir al bloque de actualización

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

        try:
            self._add_functions(n.body or [], local_env, builder, alloca, func)
        except Exception as e:
            pass

        for stmt in n.body or []:
            if not builder.block.is_terminated:
                stmt.accept(self, local_env, builder, alloca, func)

        if not builder.block.is_terminated:
            builder.branch(condition_block)  # Volver a la condición

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

        try:
            self._add_functions(n.body or [], local_env, builder, alloca, func)
        except Exception as e:
            pass

        for stmt in n.body or []:
            if not builder.block.is_terminated:
                stmt.accept(self, local_env, builder, alloca, func)

        if not builder.block.is_terminated:
            builder.branch(condition_block)  # Volver a la condición

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
            return

        if not builder.block.is_terminated:
            val = n.expr.accept(self, env, builder, alloca, func)
            builder.ret(val)

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

    def visit(
        self,
        n: VarDecl,
        env: Symtab,
        builder: ir.IRBuilder,
        alloca: ir.IRBuilder,
        func: ir.Function,
    ):
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
                llvm_type
            )  # no agregar nombre ya que puede redefinir una var global

        if n.type != SimpleTypes.STRING.value:
            var.align = IrTypes.get_align(n.type) or 0

            # Asignar el valor
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

                if initial_val_ptr.type == ir.PointerType(ir.IntType(8)):
                    from_literal_fn = self.string_runtime.from_literal()
                    bminor_string_ptr = builder.call(from_literal_fn, [initial_val_ptr])
                else:
                    copy_fn = self.string_runtime.copy()
                    bminor_string_ptr = builder.call(copy_fn, [initial_val_ptr])

                builder.store(bminor_string_ptr, var)
            else:
                emtpy = self._create_global_string("", builder)
                from_literal_fn = self.string_runtime.from_literal()
                bminor_string_ptr = builder.call(from_literal_fn, [emtpy])
                builder.store(bminor_string_ptr, var)

        env.add(n.name, var)

    def visit(
        self,
        n: ArrayDecl,
        env: Symtab,
        builder: ir.IRBuilder,
        alloca: ir.IRBuilder,
        func: ir.Function,
    ):
        """
        Genera el IR para la declaración de un array usando una estructura descriptor.
        La estructura es: { i32 size, <base_type>* data }

        arr: array [1] boolean = {true};

        alloca_entry:
            %"arr.data" = alloca [1 x i1]
            %"arr" = alloca {i32, i1*}

        entry:
            store [1 x i1] [i1 true], [1 x i1]* %"arr.data"                                  # Inicializar el array
            %"arr.size_ptr" = getelementptr {i32, i1*}, {i32, i1*}* %"arr", i32 0, i32 0     # Acceder al campo size
            store i32 1, i32* %"arr.size_ptr"                                                # Asignar el tamaño

            %"arr.data_ptr" = getelementptr {i32, i1*}, {i32, i1*}* %"arr", i32 0, i32 1     # Acceder al campo data
            %".5" = bitcast [1 x i1]* %"arr.data" to i1*                                     # Apuntar al primer elemento del array
            store i1* %".5", i1** %"arr.data_ptr"                                            # Asignar el apuntador en la estructura
        """
        # Determinar el tipo base de los elementos del array (ej: i32, float)
        # Definir el tipo de la estructura descriptor
        base_type = IrTypes.get_type(n.type.base)
        struct_type = ir.LiteralStructType([IrTypes.int32, base_type.as_pointer()])

        size_val = None
        initial_values = None
        array_len = 0

        # Determinar el tamaño y el contenido inicial del array
        # El array se define con una lista de inicialización (ej: x = {1, 2, 3})
        if n.value:
            content = []

            for v in n.value:
                item = self._get_literal_value(v)

                if item is None:
                    item = v.accept(self, env, builder, alloca, func)

                content.append(item)

            array_len = len(content)
            # Check problema cuando el array tiene un tamaño variable
            # size_val = IrTypes.const_int(array_len)  # El tamaño es una constante
            array_ty = ir.ArrayType(base_type, array_len)
            initial_values = ir.Constant(array_ty, content)

        # El array se define con un tamaño explícito (ej: array[10] integer)
        if n.type.size:
            const_size = self._get_literal_value(n.type.size)

            # El tamaño es una constante literal (ej: [10])
            if const_size is not None:
                array_len = const_size
                size_val = IrTypes.const_int(array_len)

            # El tamaño es una variable o expresión (ej: [n])
            else:
                size_val = n.type.size.accept(self, env, builder, alloca, func)
                # No conocemos array_len en tiempo de compilación
        else:
            # Un array debe tener un tamaño o un inicializador
            raise ValueError(
                "La declaración del array es inválida: falta tamaño o inicializador."
            )

        # Reservar memoria para los datos del array en la pila
        data_ptr = None

        if array_len > 0 or isinstance(size_val, ir.Constant):
            # Si el tamaño es conocido en tiempo de compilación, creamos un ArrayType
            array_type = ir.ArrayType(base_type, array_len)
            data_ptr = alloca.alloca(array_type, name=f"{n.name}.data")
        else:
            # Si el tamaño es dinámico (una variable), usamos la sintaxis de VLA de alloca
            data_ptr = alloca.alloca(base_type, size=size_val, name=f"{n.name}.data")

        # Si había valores iniciales, los almacenamos en el puntero de datos
        if initial_values:
            builder.store(initial_values, data_ptr)

        builder.comment(f"Declaring array {n.name}")

        # Reservar memoria para la estructura en la pila
        struct_ptr = alloca.alloca(struct_type, name=n.name)

        # Agregar valores a la estructura
        # Almacenar el tamaño en el primer campo (índice 0)
        size_field_ptr = builder.gep(
            struct_ptr,
            [IrTypes.const_int(0), IrTypes.const_int(0)],
            name=f"{n.name}.size_ptr",
        )

        builder.store(size_val, size_field_ptr)

        # Almacenar el puntero a los datos en el segundo campo (índice 1)
        data_field_ptr = builder.gep(
            struct_ptr,
            [IrTypes.const_int(0), IrTypes.const_int(1)],
            name=f"{n.name}.data_ptr",
        )

        # El puntero `data_ptr` es de tipo `[N x T]*` o `T*`. La estructura necesita `T*`.
        # Un `bitcast` asegura que el tipo sea el correcto.
        casted_data_ptr = builder.bitcast(data_ptr, base_type.as_pointer())
        builder.store(casted_data_ptr, data_field_ptr)

        # Agregar linea de espacio
        builder.comment(f"end of array {n.name}")
        builder.comment("")

        # Registrar el puntero al descriptor en la tabla de símbolos
        env.add(n.name, struct_ptr)

        return struct_ptr

    def default_return(self, builder: ir.IRBuilder, ret_type: ir.Type | None):
        if not builder.block.is_terminated:
            if ret_type == ir.VoidType() or ret_type is None:
                builder.ret_void()
            elif ret_type == IrTypes.int32:
                builder.ret(IrTypes.const_int(0))
            elif ret_type == IrTypes.float32:
                builder.ret(IrTypes.const_float(0.0))
            elif ret_type == IrTypes.char8:
                builder.ret(IrTypes.const_char("\0"))
            elif ret_type == IrTypes.bool1:
                builder.ret(IrTypes.const_bool(False))

    def _add_functions(
        self,
        n: list[Statement],
        env: Symtab,
        builder: ir.IRBuilder,
        alloca: ir.IRBuilder,
        func,
    ):
        """
        Declara todas las funciones en el módulo antes de generar sus cuerpos.

        n: Lista de declaraciones (Program)
        """

        # PRIMERA PASADA: Declarar todas las funciones
        for decl in n:
            try:
                if isinstance(decl, FuncDecl):
                    self.declare_function(decl, env, builder.module)
            except Exception as e:
                print(f"Error al declarar la función {decl.name}: {e}")

        # SEGUNDA PASADA: Definir todas las funciones
        for decl in n:
            try:
                if isinstance(decl, FuncDecl):
                    self.define_function(decl, env)
            except Exception as e:
                print(f"Error al definir la función {decl.name}: {e}")

    def declare_function(
        self, n: FuncDecl, env: Symtab, module
    ):  # Funcion para declarar

        # 1. Obtener tipo de retorno
        ret_type = IrTypes.get_type(n.return_type)

        # 2. Obtener tipos de parámetros
        param_types = [IrTypes.get_type(p.type) for p in n.params]

        # 3. Crear tipo de función LLVM
        func_type = ir.FunctionType(ret_type, param_types)

        # 4. Crear la función LLVM (pero sin cuerpo)
        func_body = ir.Function(module, func_type, name=n.name + "_" + n.uid)

        # self._override_func(n, env)
        existing_entry = env.get(n.name, recursive=False)

        if existing_entry:
            # La entrada ya existe, comprobar si es una función
            if isinstance(existing_entry, ir.Function):  # Verificar que sea una función
                env[n.name] = func_body
            else:
                raise Exception(f"Error: {n.name} already declared as a variable")
        else:
            env.add(n.name, func_body)

    def define_function(self, n: FuncDecl, env: Symtab):  # Funcion para definir
        if n.body is None:
            return

        self.global_scope = False

        # 1. Buscar la función en la tabla de símbolos
        func_body = env.get(n.name, recursive=False)

        # 2. Obtener tipo de retorno
        ret_type = IrTypes.get_type(n.return_type)

        # 3. Obtener tipos de parámetros
        param_types = [IrTypes.get_type(p.type) for p in n.params]

        # 4. Crear bloques, alloca-entry
        alloca_block = func_body.append_basic_block(name="alloca")
        entry_block = func_body.append_basic_block(name="entry")

        alloca_builder = ir.IRBuilder(alloca_block)
        body_builder = ir.IRBuilder(entry_block)

        # 5. Crear entorno local
        local_env = Symtab(n.name + "_" + n.uid, parent=env)

        # 6. Asignar parámetros a variables locales
        for i, param in enumerate(n.params):
            llvm_type = param_types[i]
            ptr = alloca_builder.alloca(llvm_type, name=param.name)
            ptr.align = IrTypes.get_align(param.type)

            body_builder.store(func_body.args[i], ptr)
            local_env.add(param.name, ptr)

        try:
            self._add_functions(
                n.body or [], local_env, body_builder, alloca_builder, func_body
            )
        except Exception as e:
            pass

        # 7. Visitar cuerpo
        for stmt in n.body or []:
            if not body_builder.block.is_terminated:
                stmt.accept(self, local_env, body_builder, alloca_builder, func_body)

        alloca_builder.branch(entry_block)

        # 8. Si no hay return explícito, retornar 0 o equivalente
        self.default_return(body_builder, ret_type)

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
        """
        # 1. Comprobar si el string ya está en la caché
        interpreted_string = py_string.encode("utf-8").decode("unicode_escape")
        str_val = interpreted_string.encode("utf8") + b"\00"

        if str_val in self._string_cache:
            global_var = self._string_cache[str_val]
        else:
            # 2. Si no está, crear una nueva variable global
            str_type = ir.ArrayType(ir.IntType(8), len(str_val))

            # Crear un nombre único para la variable global
            name = f".str.{len(self._string_cache)}"

            global_var = ir.GlobalVariable(self.module, str_type, name=name)
            global_var.linkage = "internal"  # Solo visible dentro de este módulo
            global_var.global_constant = True
            global_var.initializer = ir.Constant(str_type, bytearray(str_val))

            # 3. Guardar la nueva variable en la caché
            self._string_cache[str_val] = global_var

        # 4. Obtener un puntero al primer elemento (i8*) usando GEP
        zero = ir.Constant(ir.IntType(32), 0)
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

    def visit(
        self,
        n: Increment,
        env: Symtab,
        builder: ir.IRBuilder,
        alloca: ir.IRBuilder,
        func: ir.Function,
    ):
        if isinstance(n.location, VarLoc):
            ptr = env.get(n.location.name)
        else:
            ptr = n.location.accept(self, env, builder, alloca, func)

        if type(ptr) == type(IrTypes.const_int32) or type(ptr) == ir.Instruction:
            val = ptr
        else:
            val = builder.load(ptr)

        incremented = builder.add(val, IrTypes.const_int(1))

        if isinstance(n.location, VarLoc):
            builder.store(incremented, ptr)

        if n.postfix:
            return val  # devuelve el valor original

        return incremented  # devuelve el valor incrementado

    def visit(
        self,
        n: Decrement,
        env: Symtab,
        builder: ir.IRBuilder,
        alloca: ir.IRBuilder,
        func: ir.Function,
    ):
        if isinstance(n.location, VarLoc):
            ptr = env.get(n.location.name)
        else:
            ptr = n.location.accept(self, env, builder, alloca, func)

        if type(ptr) == type(IrTypes.const_int32) or type(ptr) == ir.Instruction:
            val = ptr
        else:
            val = builder.load(ptr)

        incremented = builder.sub(val, IrTypes.const_int(1))

        if isinstance(n.location, VarLoc):
            builder.store(incremented, ptr)

        if n.postfix:
            return val  # devuelve el valor original

        return incremented  # devuelve el valor incrementado

    def _concatenate_string(
        self, left: ir.Value, right: ir.Value, builder: ir.IRBuilder
    ) -> ir.Value:
        """
        Genera el IR para concatenar dos strings, que pueden ser literales (i8*)
        o el resultado de otra operación (BMinorString*).
        """
        # Obtenemos las funciones del runtime
        from_literal_fn = self.string_runtime.from_literal()
        concat_fn = self.string_runtime.concat()

        free_left = False
        free_right = False

        # --- Operando Izquierdo ---
        # Si 'left' es un literal (i8*), lo promovemos a BMinorString*
        if left.type == ir.PointerType(ir.IntType(8)):
            s1_ptr = builder.call(from_literal_fn, [left], "s1_struct")
            free_left = True
        else:  # Si ya era un BMinorString*, lo usamos directamente
            s1_ptr = left

        # --- Operando Derecho ---
        # Si 'right' es un literal (i8*), lo promovemos a BMinorString*
        if right.type == ir.PointerType(ir.IntType(8)):
            s2_ptr = builder.call(from_literal_fn, [right], "s2_struct")
            free_right = True
        else:  # Si ya era un BMinorString*, lo usamos directamente
            s2_ptr = right

        # --- Concatenación ---
        # Llamamos a la función de C con los dos punteros a BMinorString
        result = builder.call(concat_fn, [s1_ptr, s2_ptr], "concat_result")

        # NOTA SOBRE MEMORIA: s1_ptr y s2_ptr (si fueron creados por from_literal)
        # ahora son fugas de memoria (memory leaks). Esto es aceptable por ahora.
        # En un sistema más avanzado, los liberaríamos aquí con _bminor_free_string.

        if free_left:
            builder.call(self.string_runtime.free(), [s1_ptr], "free_s1")
        if free_right:
            builder.call(self.string_runtime.free(), [s2_ptr], "free_s2")

        return result

    def visit(
        self,
        n: BinOper,
        env: Symtab,
        builder: ir.IRBuilder,
        alloca: ir.IRBuilder,
        func: ir.Function,
    ):
        left = n.left.accept(self, env, builder, alloca, func)
        right = n.right.accept(self, env, builder, alloca, func)
        is_int = left.type in (ir.IntType(32), ir.IntType(8))

        if (n.left.type, n.right.type) == (
            SimpleTypes.STRING.value,
            SimpleTypes.STRING.value,
        ):
            return self._concatenate_string(left, right, builder)

        if n.oper == "^":
            fn = self.math_runtime.pow_int()
            return builder.call(fn, [left, right])

        fn = {
            "+": builder.add if is_int else builder.fadd,
            "-": builder.sub if is_int else builder.fsub,
            "*": builder.mul if is_int else builder.fmul,
            "/": builder.sdiv if is_int else builder.fdiv,
            "%": builder.srem if is_int else builder.frem,
        }

        fn_log = {
            "<=": (builder.icmp_signed if is_int else builder.fcmp_ordered),
            "<": (
                builder.icmp_signed
                if is_int
                else builder.fcmp_ordered  # ordered para evitar problemas con NaN
            ),
            ">=": (builder.icmp_signed if is_int else builder.fcmp_ordered),
            ">": (builder.icmp_signed if is_int else builder.fcmp_ordered),
            "==": (builder.icmp_signed if is_int else builder.fcmp_ordered),
            "!=": (builder.icmp_signed if is_int else builder.fcmp_ordered),
        }

        fn_bool = {
            "LAND": builder.and_,
            "LOR": builder.or_,
        }

        if n.oper in fn:
            return fn[n.oper](left, right)
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
        args = [arg.accept(self, env, builder, alloca, func) for arg in n.args]
        return builder.call(fun_name, args)

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

    def check(
        self,
        n: ArrayLoc,
        env: Symtab,
        builder: ir.IRBuilder,
        alloca: ir.IRBuilder,
        func: ir.Function,
    ):
        pass
