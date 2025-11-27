"""
Tree-walking interpreter
"""

import sys
from parser.model import *

from rich import print

from semantic import Check, Symtab
from utils import errors_detected

from .builtins import BuiltinFunction, CallError, builtins, consts

# Recursividad limitada en python
# Problemas de rendimiento en el interprete por recursividad
# sys.setrecursionlimit(1000) # por defecto


# Veracidad en bminor
def _is_truthy(value):
    if isinstance(value, bool):
        return value
    elif value is None:
        return False
    else:
        return True


def _default_val(_type: SimpleType | ArrayType | None):
    if _type is None:
        return None

    if isinstance(_type, ArrayType):
        return []

    if _type == SimpleTypes.INTEGER.value:
        return 0
    elif _type == SimpleTypes.STRING.value:
        return ""
    elif _type == SimpleTypes.BOOLEAN.value:
        return False
    elif _type == SimpleTypes.CHAR.value:
        return "\\0"
    elif _type == SimpleTypes.FLOAT.value:
        return 0

    return None


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
    def __init__(self, node: FuncDecl, env: Symtab):
        self.node = node
        self.env = env

    @property
    def arity(self) -> int:
        return len(self.node.params)

    def __call__(self, interp, *args):
        new_env = Symtab("func", self.env)

        for name, arg in zip(self.node.params, args):
            new_env[name.name] = arg

        old_env = interp.env
        interp.env = new_env
        result = None

        try:
            for stmt in self.node.body or []:
                stmt.accept(interp)
        except ReturnException as e:
            result = e.value
        except Exception as e:
            raise RuntimeError(f"Un error inesperado en {self.node.name}: {e}")
        finally:
            interp.env = old_env

        if result is None and self.node.return_type != SimpleTypes.VOID.value:
            result = _default_val(self.node.return_type)

        return result

    def bind(self, instance):
        env = Symtab("func", self.env)
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

            # if not self.ctxt.have_errors:
            if errors_detected() == 0:
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

    def visit(self, node: FuncDecl):
        func = Function(node, self.env)
        self.env[node.name] = func

    def visit(self, node: VarDecl):
        if isinstance(node, AutoDecl) and isinstance(node.value, list):
            expr = [v.accept(self) for v in node.value]
        elif node.value:
            expr = node.value.accept(self)
        else:
            expr = _default_val(node.type)

        self.env[node.name] = expr

    def visit(self, node: ArrayDecl):
        vals = []

        for v in node.value or []:
            vals.append(v.accept(self))

        size = node.type.size.accept(self)

        if size and not vals:
            vals = [_default_val(node.type.base) for _ in range(size)]

        self.env[node.name] = vals

    def visit(self, node: VarLoc):
        return self.env.get(node.name)

    def visit(self, node: ArrayLoc):
        loc = node.array.accept(self)
        index = node.index.accept(self)

        return loc[index]

    def visit(self, node: Assignment):
        value = node.value.accept(self)

        if isinstance(node.location, ArrayLoc):
            loc = node.location.array.accept(self)
            index = node.location.index.accept(self)
            loc[index] = value
        else:
            loc = node.location.name
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

    def visit(self, node: WhileStmt):
        env_parent = self.env
        env = Symtab("while", env_parent)
        self.env = env

        while node.condition is None or _is_truthy(node.condition.accept(self)):
            self.env = env

            try:
                for stmt in node.body:
                    stmt.accept(self)
            except BreakException:
                break
            except ContinueException:
                continue
            finally:
                # Condition es con el env fuera del bucle
                self.env = env_parent

        self.env = env_parent

    def visit(self, node: DoWhileStmt):
        env_parent = self.env
        env = Symtab("do-while", env_parent)
        self.env = env

        is_break = False

        while True:
            try:
                for stmt in node.body:
                    stmt.accept(self)
            except BreakException:
                is_break = True
                break
            except ContinueException:
                continue
            finally:
                # salir sin actualizar o evaluar la condicion
                if is_break:
                    break

                # Condition es con el env fuera del bucle
                self.env = env_parent

                if not (
                    node.condition is None or _is_truthy(node.condition.accept(self))
                ):
                    break

                self.env = env

        self.env = env_parent

    def visit(self, node: ForStmt):
        env_parent = self.env
        env = Symtab("for", env_parent)
        self.env = env

        if node.init:
            node.init.accept(self)

        is_break = False

        while node.condition is None or _is_truthy(node.condition.accept(self)):
            self.env = env

            try:
                for stmt in node.body:
                    stmt.accept(self)
            except BreakException:
                is_break = True
                break
            except ContinueException:
                continue
            finally:
                # salir sin actualizar
                if is_break:
                    break

                # Update, Condition es con el env fuera del bucle
                self.env = env_parent

                if node.update:
                    node.update.accept(self)

        self.env = env_parent

    def visit(self, node: ContinueStmt):
        raise ContinueException

    def visit(self, node: BreakStmt):
        raise BreakException

    def visit(self, node: ReturnStmt):
        value = None if not node.expr else node.expr.accept(self)
        raise ReturnException(value)

    def visit(self, node: FuncCall):
        callee = self.env.get(node.name)

        if not callee:
            self.error(node, f"'{node.name}' no existe.")
            return None
        elif not isinstance(callee, Function) and not isinstance(
            callee, BuiltinFunction
        ):
            self.error(node, f"'{node.name}' no es invocable.")
            return None

        args = [arg.accept(self) for arg in node.args]

        if callee.arity != -1 and len(args) != callee.arity:
            self.error(
                node,
                f"La función '{node.name}' espera {callee.arity} argumentos, pero se recibieron {len(args)}.",
            )
            return None

        try:
            # Llama al método __call__ de la función (BuiltinFunction o Function).
            # El intérprete 'self' se pasa como primer argumento por convención.
            return callee(self, *args)
        except CallError as err:
            self.error(node, str(err))
        except KeyError as e:
            self.error(node, f"No existe la variable o función '{e.args[0]}'")
        except Exception as e:
            self.error(node, str(e))

        return None
