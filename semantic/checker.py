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
from typing import Union, List

from utils import error
from parser.model import *
from .semantic_error import SemanticError
from .symtab import Symtab
from .typesys import typenames, check_binop, check_unaryop, CheckError


class Check(Visitor):
    @classmethod
    def checker(cls, n: Program):
        checker = cls()

        # Crear una nueva tabla de simbolos
        env = Symtab('global')

        # Visitar todas las declaraciones
        for decl in n.body:
            decl.accept(checker, env)

        return env

    def _error(self, msg: str, lineno: int, error_type: SemanticError = None):
        error(f"{error_type or SemanticError.UNKNOWN}: {msg}", lineno, error_type)

    # --- Statements

    def visit(self, n: Assignment, env: Symtab):
        # Validar n.loc (location) y n.expr
        n.location.accept(self, env)
        n.expr.accept(self, env)

        if n.location.type != n.expr.type:
            self._error(f"Assignment {n.loc.type} != {n.expr.type}", n.lineno,
                        SemanticError.MISMATCH_ASSIGNMENT)
            return


#     def visit(self, n: PrintStmt, env: Symtab):
#         # visitar n.exprs
#         for expr in n.exprs:
#             expr.accept(self, env)
#             if expr.type == '<infer>':
#                 error("No se puede inferir el tipo de expresión en Print", n.lineno)

#     def visit(self, n: IfStmt, env: Symtab):
#         # Visitar n.cond (validar tipos)
#         n.cond.accept(self, env)

#         if n.cond.type == '<infer>':
#             n.test.type = 'boolean'
#         if n.cond.type != 'boolean':
#             error(
#                 f"cond en IF debe ser 'boolean'. Se obtuvo {n.cond.type}", n.lineno)

#         # Visitar n.cons (consecuente)
#         for stmt in n.cons:
#             stmt.accept(self, env)

#         # Visitar n.alt (alterno)
#         if n.alt:
#             for stmt in n.alt:
#                 stmt.accept(self, env)

#     def visit(self, n: ForStmt, env: Symtab):
#         # Visitar n.init
#         if n.init:
#             n.init.accept(self, env)
#         if n.cond:
#             n.cond.accept(self, env)

#             if n.cond.type == '<infer>':
#                 n.cond.type = 'boolean'
#             if n.cond.type != 'boolean':
#                 error(
#                     f"test en ForStmt debe ser 'boolean'. Se obtuvo {n.cond.type}", n.lineno)

#     def visit(self, n: WhileStmt, env: Symtab):
#         # Visitar n.cond (validar tipos)
#         n.cond.accept(self, env)

#         if n.cond.type == '<infer>':
#             n.cond.type = 'bool'
#         if n.cond.type != 'bool':
#             error(
#                 f"test en While debe ser 'bool'. Se obtuvo {n.cond.type}", n.lineno)

#         # Marcar que se esta dentro de un While
#         env['$loop'] = True

#         # Visitar n.body
#         for b in n.body:
#             b.accept(self, env)

#         # Deshabilitar marca del While
#         env['$loop'] = False

#     '''
# 	def visit(self, n: Union[Break, Continue], env: Symtab):
# 		# Verificar que esta dentro de un ciclo while
# 		name = n.__class__.__name__.lower()
# 		if '$loop' not in env:
# 			error(f"'{name}' por fuera de un loop", n.lineno)
# 	'''

#     def visit(self, n: ReturnStmt, env: Symtab):
#         # Visitar n.expr y obtene tipo
#         n.expr.accept(self, env)

#         # Obtener la funcion
#         if '$func' not in env:
#             error("'Return' usado por fuera de una funcion", n.lineno)
#         else:
#             func = env.get('$func')

#             if func.type == 'void':
#                 pass
#             elif func.type != n.expr.type:
#                 error(
#                     f"Error de tipo. return {func.type} != {n.expr.type}", n.lineno)

#     # --- Declaration

#     def visit(self, n: Declaration, env: Symtab):
#         self.check(n, env)

#         # Todas las definiciones tienen nombre. Tras la
#         # comprobación, el nombre debe formar parte del
#         # entorno (de ahí el propósito de definirlo).
#         assert n.name in env

#         if '$func' in env:
#             n.scope = 'local'
#         else:
#             n.scope = 'global'


    def visit(self, n: VarDecl, env: Symtab):
        self.check(n, env)

    def check(self, n: VarDecl, env: Symtab):
        if n.value:
            n.value.accept(self, env)

            if n.type != n.value.type:
                self._error(
                    f"Declaration {n.name} has type {n.type} != {n.value.type}", n.lineno, SemanticError.MISMATCH_DECLARATION)
                return

        # Agregar n.name a symtab
        try:
            env.add(n.name, n)
        except Symtab.SymbolConflictError as ex:
            self._error(f"Variable '{n.name}' is already defined",
                        n.lineno, SemanticError.REDEFINE_VARIABLE_TYPE)
        except Symtab.SymbolDefinedError as exññ:
            self._error(f"Variable '{n.name}' is already defined",
                        n.lineno, SemanticError.REDEFINE_VARIABLE)

#     def check(self, n: ArrayDecl, env: Symtab):
#         ...

#     def check(self, n: FuncDecl, env: Symtab):
#         # Guardar la función en symtab actual
#         try:
#             env.add(n.name, n)
#         except Symtab.SymbolConflictError as ex:
#             error(
#                 f"La Función '{n.name}' ya definida y con tipo de dato diferente", n.lineno)
#         except Symtab.SymbolDefinedError as exññ:
#             error(f"La Función '{n.name}' ya definida", n.lineno)

#         # Crear una nueva symtab (local) para Function
#         env = Symtab(n.name, env)

#         # Magic variable that references the current function
#         env['$func'] = n

#         # Agregar todos los n.params dentro de symtab
#         for p in n.parms:
#             p.accept(self, env)

#         # Visitar n.stmts
#         if n.body:
#             for stmt in n.body:
#                 stmt.accept(self, env)

#         env['$func'] = None

#     def check(self, n: VarParm, env: Symtab):
#         # Guardar Parameter (name, type) en symtab
#         try:
#             env.add(n.name, n)
#         except Symtab.SymbolConflictError as ex:
#             error(
#                 f"El Parámetro '{n.name}' ya definido y con tipo de dato diferente", n.lineno)
#         except Symtab.SymbolDefinedError as exññ:
#             error(f"El Parámetro '{n.name}' ya definido", n.lineno)

#     def check(self, n: VarParm, env: Symtab):
#         ...

#     # --- Expressions

    def visit(self, n: Literal, env: Symtab):
        # No hay nada que hacer. Los literales son
        # primitivos básicos. Ya tienen un tipo
        # definido en el archivo model.py.
        pass

    def visit(self, n: SimpleType, env: Symtab):
        # No hay nada que hacer. Los tipos simples son
        # primitivos básicos. Ya tienen un tipo
        # definido en el archivo model.py.
        pass

    def visit(self, n: BinOper, env: Symtab):
        # Visitar n.left y n.right
        n.left.accept(self, env)
        n.right.accept(self, env)

        # Verificar compatibilidad de tipos
        try:
            n.type = check_binop(n.oper, n.left.type.name, n.right.type.name)
        except CheckError as e:
            self._error(str(e), n.lineno,
                        SemanticError.INVALID_BINARY_OP)
            n.type = SimpleType('undefined')
            return

        if not n.type and (n.left.type and n.right.type):
            self._error(f"{n.left.type} {n.oper} {n.right.type}", n.lineno,
                        SemanticError.BINARY_OP_TYPE)

    def visit(self, n: UnaryOper, env: Symtab):
        # Visitar n.expr (operando)
        n.expr.accept(self, env)

        # Validar si es un operador unario valido
        try:
            n.type = check_unaryop(n.oper, n.expr.type.name)
        except CheckError as e:
            self._error(str(e), n.lineno,
                        SemanticError.INVALID_UNARY_OP)
            n.type = SimpleType('undefined')
            return

        if not n.type and n.expr.type:
            self._error(f"{n.oper} {n.expr.type}", n.lineno,
                        SemanticError.UNARY_OP_TYPE)

#     '''
# 	def visit(self, n:TypeCast, env:Symtab):
# 		# Visitar n.expr para validar
# 		n.expr.accept(self, env)

# 		# Ya se tiene un tipo establecido (el objetivo de
# 		# la conversión).  Se debe comprobar si la
# 		# expresión asociada se puede convertir a ese
# 		# tipo.
# 		# x = int(3.4);

# 		# retornar el tipo del cast n.type
# 		if n.expr.type == '<infer>':
# 			n.expr.type = n.type
# 	'''

#     def visit(self, n: FuncCall, env: Symtab):
#         # Validar si n.name existe
#         func = env.get(n.name)

#         if func is None:
#             error(f"Function {n.name} no definida", n.lineno)
#             return

#         # La funcion debe ser una Function
#         if not isinstance(func, Function):
#             error(f'{n.name} no es función', n.lineno)
#             # Si no es una función, no es posible realizar más comprobaciones
#             return

#         # El número de argumentos de la función debe coincidir con los parámetros
#         if len(n.args) != len(func.parms):
#             error(
#                 f'Se esperaban {len(func.parms)} argumentos. Se obtubieron {len(node.args)}.', n.lineno)

#         # Los tipos de argumentos de la función deben coincidir con los tipos de parámetros
#         for pos, (parm, arg) in enumerate(zip(func.parms, n.args), 1):
#             arg.accept(self, env)

#             if parm.type != arg.type:
#                 error(
#                     f"Error de tipo en el argumento {pos}. {parm.type} != {arg.type}", parm.lineno)

#         # El tipo de resultado es el tipo de retorno de la función
#         n.type = func.type

    def check(self, n: VarLoc, env: Symtab):
        # Verificar si n.name existe symtab
        decl = env.get(n.name)

        if not decl:
            self._error(
                f"{SemanticError.UNDECLARED_VARIABLE} {n.name!r}", n.lineno, SemanticError.UNDECLARED_VARIABLE)
            return

        # Propaga informacion sobre tipo
        n.type = decl.type

    def visit(self, n: Location, env: Symtab):
        self.check(n, env)


#     '''
# 	def check(self, n:MemoryLocation, env:Symtab):
# 		# Visitar n.address (expression) para validar
# 		n.address.accept(self, env)
# 		if n.address.type != 'int':
# 			error(f"Dirección de Memoria debe ser 'integer'", n.lineno)

# 		# Retornar el tipo de datos
# 		n.type = '<infer>'
# 		n.mutable = True
# 	'''


if __name__ == '__main__':
    import sys

    if sys.platform != 'ios':
        if len(sys.argv) != 2:
            raise SystemExit("Usage: python gcheck.py <filename>")

        filename = sys.argv[1]

    else:
        from File_Picker import file_picker_dialog

        filename = file_picker_dialog(
            title='Seleccionar una archivo',
            root_dir='./test',
            file_pattern='^.*[.]bminor'
        )

    if filename:
        from parser import Parser
        from scanner import Lexer

        txt = open(filename, encoding='utf-8').read()
        tokens = Lexer.tokenize(code)
        top = Parser.parse(tokens)
        env = Check.checker(top)

        if not errors_detected():
            env.print()
