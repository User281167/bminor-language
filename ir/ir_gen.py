# # checker.py
# '''
# Este archivo contendrá la parte de verificación/validación de tipos
# del compilador.  Hay varios aspectos que deben gestionarse para
# que esto funcione. Primero, debe tener una noción de "tipo" en su compilador.
# Segundo, debe administrar los entornos y el alcance para manejar los
# nombres de las definiciones (variables, funciones, etc.).

# Una clave para esta parte del proyecto es realizar pruebas adecuadas.
# A medida que agregue código, piense en cómo podría probarlo.
# '''
from parser.model import *
from uuid import uuid4

from llvmlite import ir
from rich import print

from semantic import Symtab
from utils import error, warning


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
        checker = cls()

        if module_name is None:
            module_name = str(uuid4())

        module = ir.Module(name=module_name)

        # # Visitar todas las declaraciones
        for decl in n.body:
            decl.accept(checker, env)

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

    def visit(self, n: VarDecl, env: Symtab):
        print(n)
        if env.name == "global":
            print("global")
        pass

    def check(self, n: ArrayDecl, env: Symtab):
        pass

    def check(self, n: FuncDecl, env: Symtab):
        pass

    def visit(self, n: Param, env: Symtab):
        pass

    # --- Expressions

    def visit(self, n: Literal, env: Symtab):
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
