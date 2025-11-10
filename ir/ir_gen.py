"""
Este archivo contiene la parte de generación de código intermedio con LLVMite.
El objetivo es tomar el AST generado por el parser y transformarlo en
código intermedio que pueda ser ejecutado por la maquina virtual de
LLVMite.
"""

import codecs
from parser.model import *
from uuid import uuid4

from llvmlite import ir

from semantic import Symtab

from .ir_type import IrTypes


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
    def Generate(cls, n: Program, env: Symtab, module_name: str | None) -> ir.Module:
        """
        Genera un módulo de IR a partir del AST y la tabla de símbolos.
        Visita todas las declaraciones y llama a accept() para cada una.
        Si hay un error en alguna de las declaraciones, imprime el error y sigue adelante.
        Devuelve el módulo de IR generado.

        args:
            n (Program): AST del programa, el ast generado por el analizador semántico ya que este inyecta los tipos en cada nodo
            env (Symtab): Tabla de símbolos
            module_name (str | None): Nombre del módulo de IR
        """

        gen = cls()

        if module_name is None:
            module_name = str(uuid4())

        module = ir.Module(name=module_name)

        # Crear función run
        func_type = ir.FunctionType(ir.IntType(32), [])
        run_func = ir.Function(module, func_type, name="run")

        # Crear bloques en orden correcto
        alloca_block = run_func.append_basic_block(name="alloca_entry")
        entry_block = run_func.append_basic_block(name="entry")

        # Builder para allocas
        alloca_builder = ir.IRBuilder(alloca_block)
        alloca_builder.branch(entry_block)  # salto explícito al bloque principal

        # Builder para instrucciones normales
        run_builder = ir.IRBuilder(entry_block)

        # Entorno de símbolos
        env = Symtab("global")

        # Visitar todas las declaraciones
        for decl in n.body:
            try:
                decl.accept(gen, run_builder, alloca_builder, env)
            except Exception as e:
                print("Error decl = ")
                decl.pretty()
                print(e)

        # Posicionar run_builder al final del bloque antes de emitir ret
        run_builder.position_at_end(entry_block)

        # si existe una función main, llamarla y retornar su valor si no return 0
        main_func = module.get_global("main") if "main" in module.globals else None

        if main_func and isinstance(main_func, ir.Function):
            # Llamar a main y retornar su resultado
            result = run_builder.call(main_func, [])
            run_builder.ret(result)
        else:
            # No hay main, retornar 0
            run_builder.ret(ir.Constant(IrTypes.int32, 0))

        return module

    def _inject_fun_builtins(
        self, builder: ir.IRBuilder, alloca: ir.IRBuilder, env: Symtab
    ):
        pass

    def _check_fun_call_builtins(
        self, n: FuncCall, builder: ir.IRBuilder, alloca: ir.IRBuilder
    ) -> bool:
        pass

    def _error(self, msg: str, lineno: int):
        pass

    def visit(
        self, n: BlockStmt, builder: ir.IRBuilder, alloca: ir.IRBuilder, env: Symtab
    ):
        pass

    # --- Statements

    def visit(
        self, n: Assignment, builder: ir.IRBuilder, alloca: ir.IRBuilder, env: Symtab
    ):
        pass

    def visit(
        self, n: PrintStmt, builder: ir.IRBuilder, alloca: ir.IRBuilder, env: Symtab
    ):
        pass

    def visit(
        self, n: IfStmt, builder: ir.IRBuilder, alloca: ir.IRBuilder, env: Symtab
    ):
        pass

    def visit(
        self, n: ForStmt, builder: ir.IRBuilder, alloca: ir.IRBuilder, env: Symtab
    ):
        pass

    def visit(
        self, n: WhileStmt, builder: ir.IRBuilder, alloca: ir.IRBuilder, env: Symtab
    ):
        pass

    def visit(
        self, n: DoWhileStmt, builder: ir.IRBuilder, alloca: ir.IRBuilder, env: Symtab
    ):
        pass

    def _search_env_name(
        self, builder: ir.IRBuilder, alloca: ir.IRBuilder, env_name: str
    ) -> bool:
        pass

    def visit(
        self, n: ContinueStmt, builder: ir.IRBuilder, alloca: ir.IRBuilder, env: Symtab
    ):
        pass

    def visit(
        self, n: BreakStmt, builder: ir.IRBuilder, alloca: ir.IRBuilder, env: Symtab
    ):
        pass

    def visit(
        self, n: ReturnStmt, builder: ir.IRBuilder, alloca: ir.IRBuilder, env: Symtab
    ):
        pass

    # --- Declaration

    def visit(
        self, n: Declaration, builder: ir.IRBuilder, alloca: ir.IRBuilder, env: Symtab
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
        self, n: VarDecl, builder: ir.IRBuilder, alloca: ir.IRBuilder, env: Symtab
    ):
        llvm_type = IrTypes.get_type(n.type)
        # var = builder.alloca(llvm_type, name=n.name)
        var = alloca.alloca(llvm_type, name=n.name)
        env.add(n.name, var)

        if n.type in (SimpleTypes.INTEGER.value, SimpleTypes.FLOAT.value):
            var.align = 4
        elif n.type == SimpleTypes.CHAR.value:
            var.align = 1
        elif n.type == SimpleTypes.BOOLEAN.value:
            var.align = 1

        # Asignar el valor
        if not n.value:
            builder.store(ir.Constant(llvm_type, 0), var)
        else:
            val = self._get_literal_value(n.value)

            if not val is None:
                builder.store(ir.Constant(llvm_type, val), var)
            else:
                val = n.value.accept(self, builder, alloca, env)
                builder.store(val, var)

    def check(
        self, n: ArrayDecl, builder: ir.IRBuilder, alloca: ir.IRBuilder, env: Symtab
    ):
        pass

    def check(
        self, n: FuncDecl, builder: ir.IRBuilder, alloca: ir.IRBuilder, env: Symtab
    ):
        pass

    def visit(self, n: Param, builder: ir.IRBuilder, alloca: ir.IRBuilder, env: Symtab):
        pass

    # --- Expressions

    def visit(
        self, n: Literal, builder: ir.IRBuilder, alloca: ir.IRBuilder, env: Symtab
    ):
        pass

    def visit(
        self, n: SimpleType, builder: ir.IRBuilder, alloca: ir.IRBuilder, env: Symtab
    ):
        pass

    def visit(
        self, n: ArrayType, builder: ir.IRBuilder, alloca: ir.IRBuilder, env: Symtab
    ):
        pass

    def visit(
        self, n: Increment, builder: ir.IRBuilder, alloca: ir.IRBuilder, env: Symtab
    ):
        pass

    def visit(
        self, n: Decrement, builder: ir.IRBuilder, alloca: ir.IRBuilder, env: Symtab
    ):
        pass

    def visit(
        self, n: BinOper, builder: ir.IRBuilder, alloca: ir.IRBuilder, env: Symtab
    ):
        pass

    def visit(
        self, n: UnaryOper, builder: ir.IRBuilder, alloca: ir.IRBuilder, env: Symtab
    ):
        val = n.expr.accept(self, builder, env)

        if n.oper == "-":
            return builder.neg(val)

    def visit(
        self, n: FuncCall, builder: ir.IRBuilder, alloca: ir.IRBuilder, env: Symtab
    ):
        pass

    def visit(
        self, n: Location, builder: ir.IRBuilder, alloca: ir.IRBuilder, env: Symtab
    ):
        # self.check(n, env)
        pass

    def visit(
        self, n: VarLoc, builder: ir.IRBuilder, alloca: ir.IRBuilder, env: Symtab
    ):
        """
        Obtener Puntero de la variable
        """
        var = env.get(n.name)
        return builder.load(var, name=n.name)

    def check(
        self, n: ArrayLoc, builder: ir.IRBuilder, alloca: ir.IRBuilder, env: Symtab
    ):
        pass
