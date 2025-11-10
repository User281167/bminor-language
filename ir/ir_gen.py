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
        setattr(gen, "module", module)
        setattr(gen, "env", env)

        # Visitar todas las declaraciones
        for decl in n.body:
            try:
                decl.accept(gen, ir.IRBuilder())
            except Exception as e:
                print("Error decl = ", decl)
                print(e)

        if hasattr(gen, "_init_builder"):
            builder = gen._init_builder
            builder.ret_void()

        return gen.module

    def _inject_fun_builtins(self, builder: ir.IRBuilder):
        pass

    def _check_fun_call_builtins(self, n: FuncCall, builder: ir.IRBuilder) -> bool:
        pass

    def _error(self, msg: str, lineno: int):
        pass

    def visit(self, n: BlockStmt, builder: ir.IRBuilder):
        pass

    # --- Statements

    def visit(self, n: Assignment, builder: ir.IRBuilder):
        pass

    def visit(self, n: PrintStmt, builder: ir.IRBuilder):
        pass

    def visit(self, n: IfStmt, builder: ir.IRBuilder):
        pass

    def visit(self, n: ForStmt, builder: ir.IRBuilder):
        pass

    def visit(self, n: WhileStmt, builder: ir.IRBuilder):
        pass

    def visit(self, n: DoWhileStmt, builder: ir.IRBuilder):
        pass

    def _search_env_name(self, builder: ir.IRBuilder, env_name: str) -> bool:
        pass

    def visit(self, n: ContinueStmt, builder: ir.IRBuilder):
        pass

    def visit(self, n: BreakStmt, builder: ir.IRBuilder):
        pass

    def visit(self, n: ReturnStmt, builder: ir.IRBuilder):
        pass

    # --- Declaration

    def visit(self, n: Declaration, builder: ir.IRBuilder):
        pass

    def _calc_init(self, n: VarDecl):
        if not n.value:
            return

        # init function
        # permitir iniciar valores globales que no son inicializados con valor literal
        # ejemplo x: integer = 1 + 2; z = x + y;
        if not hasattr(self, "_init_builder"):
            func_type = ir.FunctionType(ir.VoidType(), [])
            self._init_func = ir.Function(self.module, func_type, name="__init_globals")
            block = self._init_func.append_basic_block(name="entry")
            self._init_builder = ir.IRBuilder(block)

        builder = self._init_builder
        n.value.accept(self, builder)

    def __get_literal_value(self, n: Literal | UnaryOper | BinOper):
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

    def _get_literal_value(self, n: Literal | UnaryOper | BinOper):
        val = self.__get_literal_value(n)

        if val is None:
            return

        if n.type == SimpleTypes.INTEGER.value:
            return int(val)
        elif n.type == SimpleTypes.FLOAT.value:
            return float(val)
        elif n.type == SimpleTypes.CHAR.value:
            return ord(val)
        elif n.type == SimpleTypes.BOOLEAN.value:
            return bool(val)

        return val

    def visit(self, n: VarDecl, builder: ir.IRBuilder):
        if self.env.name == "global":
            llvm_type = IrTypes.get_type(n.type)
            var = ir.GlobalVariable(self.module, llvm_type, n.name)
            var.linkage = "dso_local"

            var.global_constant = isinstance(n, ConstantDecl)

            if n.type in (SimpleTypes.INTEGER.value, SimpleTypes.FLOAT.value):
                var.align = 4
            elif n.type == SimpleTypes.CHAR.value:
                var.align = 1
            elif n.type == SimpleTypes.BOOLEAN.value:
                var.align = 1

            # Asignar el valor
            if not n.value:
                var.initializer = ir.Constant(llvm_type, 0)
            elif isinstance(n.value, Literal):
                if llvm_type == ir.FloatType():
                    var.initializer = ir.Constant(llvm_type, float(n.value.value))
                elif llvm_type == ir.IntType(8):  # char
                    val = n.value.value
                    decoded = codecs.decode(val, "unicode_escape")  # '\\n' -> '\n'
                    ascii_val = ord(decoded)
                    var.initializer = ir.Constant(llvm_type, ascii_val)
                elif llvm_type == ir.IntType(1):  # boolean
                    var.initializer = ir.Constant(llvm_type, bool(n.value.value))
                else:
                    var.initializer = ir.Constant(llvm_type, int(n.value.value))
            else:
                val = self._get_literal_value(n.value)

                if not val is None:
                    var.initializer = ir.Constant(llvm_type, val)
                else:
                    # inicializa con cero y calcular valor en __init_globals
                    self._calc_init(n)
        pass

    def check(self, n: ArrayDecl, builder: ir.IRBuilder):
        pass

    def check(self, n: FuncDecl, builder: ir.IRBuilder):
        pass

    def visit(self, n: Param, builder: ir.IRBuilder):
        pass

    # --- Expressions

    def visit(self, n: Literal, builder: ir.IRBuilder):
        pass

    def visit(self, n: SimpleType, builder: ir.IRBuilder):
        pass

    def visit(self, n: ArrayType, builder: ir.IRBuilder):
        pass

    def visit(self, n: Increment, builder: ir.IRBuilder):
        pass

    def visit(self, n: Decrement, builder: ir.IRBuilder):
        pass

    def visit(self, n: BinOper, builder: ir.IRBuilder):
        pass

    def visit(self, n: UnaryOper, builder: ir.IRBuilder):
        print(n)
        pass

    def visit(self, n: FuncCall, builder: ir.IRBuilder):
        pass

    def visit(self, n: Location, builder: ir.IRBuilder):
        # self.check(n, env)
        pass

    def visit(self, n: VarLoc, builder: ir.IRBuilder):
        # self.check(n, env)
        pass

    def check(self, n: VarLoc, builder: ir.IRBuilder):
        pass

    def check(self, n: ArrayLoc, builder: ir.IRBuilder):
        pass
