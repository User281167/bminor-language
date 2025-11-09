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

        # Visitar todas las declaraciones
        for decl in n.body:
            try:
                decl.accept(gen, env, module)
            except Exception as e:
                print("Error decl = ", decl)
                print(e)

        return module

    def _inject_fun_builtins(self, env: Symtab):
        pass

    def _check_fun_call_builtins(self, n: FuncCall, env: Symtab) -> bool:
        pass

    def _error(self, msg: str, lineno: int):
        pass

    def visit(self, n: BlockStmt, env: Symtab):
        pass

    # --- Statements

    def visit(self, n: Assignment, env: Symtab):
        pass

    def visit(self, n: PrintStmt, env: Symtab):
        pass

    def visit(self, n: IfStmt, env: Symtab):
        pass

    def visit(self, n: ForStmt, env: Symtab):
        pass

    def visit(self, n: WhileStmt, env: Symtab):
        pass

    def visit(self, n: DoWhileStmt, env: Symtab):
        pass

    def _search_env_name(self, env: Symtab, env_name: str) -> bool:
        pass

    def visit(self, n: ContinueStmt, env: Symtab):
        pass

    def visit(self, n: BreakStmt, env: Symtab):
        pass

    def visit(self, n: ReturnStmt, env: Symtab):
        pass

    # --- Declaration

    def visit(self, n: Declaration, env: Symtab):
        pass

    def visit(self, n: VarDecl, env: Symtab, module: ir.Module):
        if n.value:
            n.value.accept(self, env, module)

        if env.name == "global":
            llvm_type = IrTypes.get_type(n.type)
            var = ir.GlobalVariable(module, llvm_type, n.name)
            var.linkage = "dso_local"

            var.global_constant = isinstance(n, ConstantDecl)

            if n.type in (SimpleTypes.INTEGER.value, SimpleTypes.FLOAT.value):
                var.align = 4
            elif n.type == SimpleTypes.CHAR.value:
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
                else:
                    var.initializer = ir.Constant(llvm_type, int(n.value.value))

        pass

    def check(self, n: ArrayDecl, env: Symtab):
        pass

    def check(self, n: FuncDecl, env: Symtab):
        pass

    def visit(self, n: Param, env: Symtab):
        pass

    # --- Expressions

    def visit(self, n: Literal, env: Symtab, module: ir.Module):
        pass

    def visit(self, n: SimpleType, env: Symtab):
        pass

    def visit(self, n: AutoDecl, env: Symtab):
        pass

    def visit(self, n: ArrayType, env: Symtab):
        pass

    def visit(self, n: Increment, env: Symtab):
        pass

    def visit(self, n: Decrement, env: Symtab):
        pass

    def visit(self, n: BinOper, env: Symtab):
        pass

    def visit(self, n: UnaryOper, env: Symtab):
        pass

    def visit(self, n: FuncCall, env: Symtab):
        pass

    def visit(self, n: Location, env: Symtab):
        # self.check(n, env)
        pass

    def visit(self, n: VarLoc, env: Symtab):
        # self.check(n, env)
        pass

    def check(self, n: VarLoc, env: Symtab):
        pass

    def check(self, n: ArrayLoc, env: Symtab):
        pass
