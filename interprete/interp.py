"""
Tree-walking interpreter
"""

from collections import ChainMap
from parser.model import *

# from checker import Checker
# from model import *
from rich import print

# from typesys import Array, Bool, CObject, Nil, Number, String
from semantic import Check, Symtab
from utils import errors_detected

from .builtins import CallError, builtins, consts


# Veracidad en bminor
def _is_truthy(value):
    if isinstance(value, bool):
        return value
    elif value is None:
        return False
    else:
        return True


class ReturnException(Exception):
    def __init__(self, value):
        self.value = value


class BreakException(Exception):
    pass


class ContinueException(Exception):
    pass


class BminorExit(BaseException):
    pass


class AttributeError(Exception):
    pass


class Function:
    def __init__(self, node, env):
        self.node = node
        self.env = env

    @property
    def arity(self) -> int:
        return len(self.node.params)

    def __call__(self, interp, *args):
        newenv = self.env.new_child()

        for name, arg in zip(self.node.params, args):
            newenv[name] = arg

        oldenv = interp.env
        interp.env = newenv

        try:
            self.node.stmts.accept(interp)
            result = None
        except ReturnException as e:
            result = e.value
        finally:
            interp.env = oldenv
        return result

    def bind(self, instance):
        env = self.env.new_child()
        env["this"] = instance
        return Function(self.node, env)


class Interpreter(Visitor):
    def __init__(self, ctxt, get_output=False):
        self.ctxt = ctxt
        # self.env = ChainMap()
        # self.check_env = ChainMap()
        self.env = Symtab("global")
        self.check_env = Symtab("global")
        self.localmap = {}
        self.get_output = get_output
        self.output = ""

    def _check_numeric_operands(self, node, left, right):
        if isinstance(left, (int, float)) and isinstance(right, (int, float)):
            return True
        else:
            self.error(node, f"En '{node.oper}' los operandos deben ser numeros")

    def _check_numeric_char_operands(self, node, left, right):
        if isinstance(left, (int, float)) and isinstance(right, (int, float)):
            return left, right
        elif (
            isinstance(left, str)
            and isinstance(right, str)
            and (len(left) == 1)
            and (len(right) == 1)
        ):
            return ord(left), ord(right)
        else:
            self.error(
                node, f"En '{node.oper}' los operandos deben ser numeros o caracteres"
            )

    def _check_numeric_operand(self, node, value):
        if isinstance(value, (int, float)):
            return True
        else:
            self.error(node, f"En '{node.oper}' el operando debe ser un numero")

    def error(self, position, message):
        self.ctxt.error(position, message)
        raise BminorExit()

    def _print(self, value):
        if self.get_output:
            self.output += str(value)

        print(value, end="")

    # Punto de entrada alto-nivel
    def interpret(self, node):
        for name, cval in consts.items():
            self.check_env[name] = cval
            self.env[name] = cval

        for name, func in builtins.items():
            self.check_env[name] = func
            self.env[name] = func

        try:
            Check.check_interpreter(node, self.check_env, self)

            if not self.ctxt.have_errors:
                node.accept(self)
        except BminorExit as e:
            pass
        except Exception as e:
            # self.error(node, f"Un error inesperado: {e.__class__.__name__}")
            # raise RuntimeError(f"{e}")
            print(e)

    def visit(self, node: Program):
        for stmt in node.body:
            try:
                stmt.accept(self)
            except Exception as e:
                raise RuntimeError(
                    f"Error in {type(stmt).__name__} line {stmt.lineno} \n\n {e}"
                )

    def visit(self, node: BlockStmt):
        env = Symtab("block", parent=self.env)
        self.env = env

        for stmt in node.body:
            try:
                stmt.accept(self)
            except Exception as e:
                raise RuntimeError(
                    f"Error in {type(stmt).__name__} line {stmt.lineno} \n\n {e}"
                )

        self.env = env.parent

    # Statements

    def visit(self, node: PrintStmt):
        for expr in node.expr:
            val = expr.accept(self)

            if isinstance(val, bool):
                if val:
                    self._print("true")
                else:
                    self._print("false")
            else:
                self._print(val)

    def visit(self, node: Literal):
        val = node.value

        if isinstance(val, str):
            val = val.encode("utf-8").decode("unicode_escape")

        return val

    # Expressions

    def visit(self, node: UnaryOper):
        expr = node.expr.accept(self)

        if node.oper == "+":
            return expr
        elif node.oper == "-":
            return -expr
        elif node.oper == "!":
            return not _is_truthy(expr)
        else:
            raise NotImplementedError(node.oper)

    def check(self, node: BinOper, left):
        """
        Pasar left ya que en el visit se acepto, evitar doble visit
            0++, se agrega el valor después debería dar 0 pero con doble visit da 1
        """
        right = node.right.accept(self)

        if node.oper == "+":
            if (
                isinstance(left, str) and isinstance(right, str)
            ) or self._check_numeric_operands(node, left, right):
                return left + right

        elif node.oper == "-":
            self._check_numeric_operands(node, left, right)
            return left - right

        elif node.oper == "*":
            self._check_numeric_operands(node, left, right)
            return left * right

        elif node.oper == "/":
            self._check_numeric_operands(node, left, right)
            if isinstance(left, int) and isinstance(right, int):
                return left // right

            return left / right

        elif node.oper == "%":
            self._check_numeric_operands(node, left, right)
            return left % right

        elif node.oper == "==":
            return left == right

        elif node.oper == "!=":
            return left != right

        elif node.oper == "<":
            left, right = self._check_numeric_char_operands(node, left, right)
            return left < right

        elif node.oper == ">":
            left, right = self._check_numeric_char_operands(node, left, right)
            return left > right

        elif node.oper == "<=":
            left, right = self._check_numeric_char_operands(node, left, right)
            return left <= right

        elif node.oper == ">=":
            left, right = self._check_numeric_char_operands(node, left, right)
            return left >= right

        else:
            raise NotImplementedError(f"Mal operador {node.oper}")

    def visit(self, node: BinOper):
        left = node.left.accept(self)

        if node.oper == "LOR":
            return left if _is_truthy(left) else node.right.accept(self)
        if node.oper == "LAND":
            return node.right.accept(self) if _is_truthy(left) else left

        return self.check(node, left)

    # Declarations

    # def visit(self, node: FuncDecl):
    #     func = Function(node, self.env)
    #     self.env[node.name] = func

    def _default_val(self, node: VarDecl):
        if not hasattr(node, "type"):
            return None

        if node.type == SimpleTypes.INTEGER.value:
            return 0
        elif node.type == SimpleTypes.STRING.value:
            return ""
        elif node.type == SimpleTypes.BOOLEAN.value:
            return False
        elif node.type == SimpleTypes.CHAR.value:
            return 0
        elif node.type == SimpleTypes.FLOAT.value:
            return 0

        return None

    def visit(self, node: VarDecl):
        if node.value:
            expr = node.value.accept(self)
        else:
            expr = self._default_val(node)

        self.env.add(node.name, expr)

    def visit(self, node: VarLoc):
        return self.env.get(node.name)

    def visit(self, node: Assignment):
        loc = node.location.name

        value = node.value.accept(self)
        self.env.set(loc, value)

        return value

    def visit(self, node: Increment | Decrement):
        if isinstance(node.location, VarLoc):
            loc = node.location.name
            value = self.env.get(loc)
        else:
            value = node.location.accept(self)
            loc = None

        if isinstance(node, Increment):
            new_value = value + 1
        else:
            new_value = value - 1

        if loc:
            self.env.set(loc, new_value)

        if node.postfix:
            return value
        else:
            return new_value

    # def visit(self, node: WhileStmt):
    #     while _is_truthy(node.expr.accept(self)):
    #         try:
    #             node.stmt.accept(self)
    #         except BreakException:
    #             return
    #         except ContinueException:
    #             raise NotImplementedError

    def visit(self, node: IfStmt):
        expr = node.condition.accept(self)

        if _is_truthy(expr):
            env = Symtab("if", self.env)
            self.env = env

            for stmt in node.then_branch:
                stmt.accept(self)

            self.env = self.env.parent
        elif node.else_branch:
            env = Symtab("else", self.env)
            self.env = env

            for stmt in node.else_branch:
                stmt.accept(self)

            self.env = self.env.parent

    # def visit(self, node: ReturnStmt):
    #     # Ojo: node.expr es opcional
    #     value = 0 if not node.expr else node.expr.accept(self)
    #     raise ReturnException(value)

    # def visit(self, node: FuncCall):
    #     callee = node.func.accept(self)
    #     if not callable(callee):
    #         self.error(
    #             node.func, f"{self.ctxt.find_source(node.func)!r} no es invocable"
    #         )

    #     args = [arg.accept(self) for arg in node.args]

    #     if callee.arity != -1 and len(args) != callee.arity:
    #         self.error(node.func, f"Experado {callee.arity} argumentos")

    #     try:
    #         return callee(self, *args)
    #     except CallError as err:
    #         self.error(node.func, str(err))
    #         self.error(node.func, str(err))
    #         self.error(node.func, str(err))
