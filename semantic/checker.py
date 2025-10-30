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

from rich import print

from utils import error

from .semantic_error import SemanticError
from .symtab import Symtab
from .typesys import CheckError, check_binop, check_unaryop


class Check(Visitor):
    @classmethod
    def checker(cls, n: Program):
        checker = cls()

        # Crear una nueva tabla de simbolos
        env = Symtab("global")
        checker._inject_fun_builtins(env)

        # Visitar todas las declaraciones
        for decl in n.body:
            decl.accept(checker, env)

        return env

    def _inject_fun_builtins(self, env: Symtab):
        """
        Inyectar las funciones predefinidas por el lenguaje en la tabla de
        símbolos.  Esto es para no tener que hacer nuevos tokens y redefinir
        la gramática. Las funciones
        """

        array_length = FuncDecl(
            name="array_length",
            return_type=SimpleTypes.INTEGER.value,
            params=[
                Param("array", ArrayType(base=SimpleTypes.UNDEFINED.value, size=None))
            ],
            body=[],  # para evitar redefinir la función
        )
        env.add(array_length.name, array_length)

    def _check_fun_call_builtins(self, n: FuncCall, env: Symtab) -> bool:
        if n.name != "array_length":
            return False

        n.type = SimpleTypes.INTEGER.value

        # verificar que tenga solo un parámetro y que sea array de cualquier tipo
        if len(n.args) != 1:
            self._error(
                f"Expected 1 argument, but got {len(n.args)} for function {n.name!r}",
                n.lineno,
                SemanticError.WRONG_NUMBER_OF_ARGUMENTS,
            )
            return True

        arg = n.args[0]
        arg.accept(self, env)

        if hasattr(arg, "type") and not isinstance(arg.type, ArrayType):
            self._error(
                f"Expected an array for function {n.name!r} but got '{arg.type}'",
                n.lineno,
                SemanticError.MISMATCH_ARGUMENT_TYPE,
            )

        return True

    def _error(self, msg: str, lineno: int, error_type: SemanticError = None):
        if not hasattr(self, "_has_semantic_error"):
            self._has_semantic_error = True
            print("\n[bold red]Semantic Errors:[/bold red]")

        error(
            f"{(error_type or SemanticError.UNKNOWN).value}{':' if msg else ''} {msg}",
            lineno,
            error_type,
        )

    def _add_to_env(
        self,
        n,
        env: Symtab,
        dec_type: str = "VarDecl",
        conflict: SemanticError = SemanticError.REDEFINE_VARIABLE_TYPE,
        defined: SemanticError = SemanticError.REDEFINE_VARIABLE,
    ):
        # Agregar n.name a symtab
        try:
            env.add(n.name, n)
        except Symtab.SymbolConflictError as ex:
            self._error(f"{dec_type} {n.name!r} is already defined", n.lineno, conflict)
        except Symtab.SymbolDefinedError as ex:
            self._error(f"{dec_type} {n.name!r} is already defined", n.lineno, defined)

    def visit(self, n: BlockStmt, env: Symtab):
        """
        Validar scopes de tipo {} que no son body de funciones, if, o bucles, sino que son aislados

        ejemplo

        main: function void() = {
            {
                // scope
            }

            if () {
                ...
                {
                    // scope
                }
            }
        }
        """

        # Crear una nueva symtab (local) para el scope
        env = Symtab(
            f"scope line {n.lineno} - level {n.deep}",
            env,
        )
        n.env = env

        # Magic variable that references the current scope
        env["$scope"] = n

        for stmt in n.body:
            if isinstance(stmt, BlockStmt):
                stmt.deep = n.deep + 1

            stmt.accept(self, env)

        env["$scope"] = None

    # --- Statements

    def visit(self, n: Assignment, env: Symtab):
        """
        Validar n.loc (location) y n.expr

        Primero se llama a accept() sobre n.loc y n.expr para
        que realicen sus respectivas verificaciones.

        Validar que n.loc.type == n.expr.type tanto para
        variables como para arrays
        """
        n.location.accept(self, env)
        n.value.accept(self, env)
        n.type = n.location.type

        # si son arrays verificar que la base sea la misma no importa el tamaño
        # get_data: function array[] integer ();
        # data: array [5] integer;

        # main: function void () = {
        #     data = get_data();
        # }
        if (
            isinstance(n.location.type, ArrayType)
            and isinstance(n.value.type, ArrayType)
            and not n.value.type.size
        ):
            if n.location.type.base != n.value.type.base:
                self._error(
                    f"Assignment {n.location.type} != {n.value.type} in {n.location.name!r}",
                    n.lineno,
                    SemanticError.MISMATCH_ASSIGNMENT,
                )
            return

        if n.location.type != n.value.type:
            name = None

            if isinstance(n.location, VarLoc):
                name = "variable " + n.location.name
            elif isinstance(n.location, ArrayLoc):
                name = "array " + n.location.array.name

            if isinstance(n, AutoDecl):
                name = "auto " + n.name

            loc_type = n.location.type
            value_type = n.value.type

            self._error(
                f"Assignment {loc_type} != {value_type} in {name!r}",
                n.lineno,
                SemanticError.MISMATCH_ASSIGNMENT,
            )

    def visit(self, n: PrintStmt, env: Symtab):

        # visitar n.exprs
        for expr in n.expr:
            expr.accept(self, env)

            if expr.type == SimpleTypes.VOID.value:
                self._error(
                    f"Cannot print void type",
                    n.lineno,
                    SemanticError.PRINT_VOID_EXPRESSION,
                )
            elif isinstance(expr.type, ArrayType):
                self._error(
                    f"Arrays not allowed in print",
                    n.lineno,
                    SemanticError.PRINT_ARRAY_NOT_ALLOWED,
                )

    def visit(self, n: IfStmt, env: Symtab):
        # Visitar n.cond (validar tipos)
        n.condition.accept(self, env)

        if isinstance(n.condition, ArrayType):
            self._error(
                f"Got {n.condition.type.name}",
                n.lineno,
                SemanticError.IF_CONDITION_MUST_BE_BOOLEAN,
            )
            return
        elif isinstance(n.condition.type, ArrayType):
            self._error(
                f"Got array type",
                n.lineno,
                SemanticError.IF_CONDITION_MUST_BE_BOOLEAN,
            )
            return
        elif n.condition.type != SimpleTypes.BOOLEAN.value:
            self._error(
                f"Got {n.condition.type.name}",
                n.lineno,
                SemanticError.IF_CONDITION_MUST_BE_BOOLEAN,
            )
            return

        # Crear una nueva symtab (local) para if
        env = Symtab(f"if line {n.lineno}", env)
        n.env = env

        # Magic variable that references the current function
        env["$if"] = n

        # Visitar then (branch)
        for stmt in n.then_branch:

            stmt.accept(self, env)

        # Visitar n.else (alterno)
        if n.else_branch:
            for stmt in n.else_branch:
                stmt.accept(self, env)

        env["$if"] = None

    def _check_loop_condition(self, n, env) -> bool:
        if n is None or n.condition is None:
            return True

        n.condition.accept(self, env)

        if isinstance(n.condition.type, ArrayType):
            self._error(
                f"Got array type",
                n.lineno,
                SemanticError.LOOP_CONDITION_MUST_BE_BOOLEAN,
            )
            return False
        if n.condition.type != SimpleTypes.BOOLEAN.value:
            self._error(
                f"Got {n.condition.type.name}",
                n.lineno,
                SemanticError.LOOP_CONDITION_MUST_BE_BOOLEAN,
            )
            return False

        return True

    def visit(self, n: ForStmt, env: Symtab):
        # Visitar n.init
        """
        Validar n.init, n.condition y n.update

        Primero se llama a accept() sobre n.init, n.condition y n.update
        para que realicen sus respectivas verificaciones.

        Luego se verifica que n.condition.type sea booleano, de lo
        contrario se lanza un SemanticError.LOOP_CONDITION_MUST_BE_BOOLEAN

        Finalmente se crea una nueva tabla de símbolos local para el
        loop y se visita n.body
        """
        if n.init:
            n.init.accept(self, env)
        if not self._check_loop_condition(n, env):
            return
        if n.update:
            n.update.accept(self, env)

        # Crear una nueva symtab (local) para for
        env = Symtab(f"for line {n.lineno}", env)
        n.env = env

        # Magic variable that references the current function
        env["$loop"] = n

        # Visitar n.body
        for stmt in n.body:
            stmt.accept(self, env)

        env["$loop"] = None

    def visit(self, n: WhileStmt, env: Symtab):
        if n.condition:
            n.condition.accept(self, env)

        if not self._check_loop_condition(n, env):
            return

        # Nueva symtab (local) para while
        env = Symtab(f"while line {n.lineno}", env)
        n.env = env

        # Magic variable that references the current function
        env["$loop"] = True

        # Visitar n.body
        for stm in n.body:
            stm.accept(self, env)

        # Deshabilitar marca del While
        env["$loop"] = False

    def visit(self, n: DoWhileStmt, env: Symtab):
        n.condition.accept(self, env)

        if not self._check_loop_condition(n, env):
            return

        # Crear una nueva symtab (local) para do-while
        env = Symtab(f"do-while line {n.lineno}", env)
        n.env = env
        env["$loop"] = n

        for stmt in n.body:
            stmt.accept(self, env)

        # Marcar que se esta dentro de un While
        env["$loop"] = True

    def _search_env_name(self, env: Symtab, env_name: str) -> bool:
        parent = env

        while env and env_name not in env:
            env = env.parent

        # env = None si no encontramos la etiqueta, devolvemos parent
        return env or parent

    def visit(self, n: ContinueStmt, env: Symtab):
        # Verificar que esta dentro de un ciclo
        if "$loop" not in self._search_env_name(env, "$loop"):
            self._error(
                f"",
                n.lineno,
                SemanticError.CONTINUE_OUT_OF_LOOP,
            )

    def visit(self, n: BreakStmt, env: Symtab):
        # Verificar que esta dentro de un ciclo
        if "$loop" not in self._search_env_name(env, "$loop"):
            self._error(
                f"",
                n.lineno,
                SemanticError.BREAK_OUT_OF_LOOP,
            )

    def visit(self, n: ReturnStmt, env: Symtab):
        """
        Visita el nodo ReturnStmt y obtiene el tipo de la expresión
        n.expr. Luego, verifica que la función actual sea la
        correcta y que el tipo de la expresión coincida con el tipo
        de la función.

        Si la función retorna void y return no es void entonces se
        produce un error.

        Permitir return de func que retorna array sin tamaño
            example: function array [] integer(){
                array [N] integer;
                return a;
            }
        """

        if not n.expr is None:
            n.expr.accept(self, env)

        # Obtener la función actual
        if "$func" not in self._search_env_name(env, "$func"):
            self._error(
                f"",
                n.lineno,
                SemanticError.RETURN_OUT_OF_FUNCTION,
            )
        else:
            func = env.get("$func")

            if isinstance(n.expr, VarLoc) and not env.get(n.expr.name):
                self._error(
                    f"Variable {n.expr.name!r} not defined in current scope {env.name!r}",
                    n.lineno,
                    SemanticError.UNDECLARED_VARIABLE,
                )
                return
            elif n.expr is None and func.return_type != SimpleTypes.VOID.value:
                self._error(
                    f"Must return a value of type {func.return_type} in function '{func.name}'",
                    n.lineno,
                    SemanticError.RETURN_IN_VOID_FUNCTION,
                )
                return
            elif n.expr is None and func.return_type == SimpleTypes.VOID.value:
                return

            if (
                func.return_type == SimpleTypes.VOID.value
                and n.expr.type != SimpleTypes.VOID.value
            ):
                self._error(
                    f"Expected 'return;' got 'return {n.expr.type}'",
                    n.lineno,
                    SemanticError.RETURN_IN_VOID_FUNCTION,
                )

            if func.return_type == SimpleTypes.VOID.value:
                pass
            # Permitir cualquier tamaño si return array no tiene tamaño fijo
            elif (
                isinstance(func.return_type, ArrayType)
                and isinstance(n.expr.type, ArrayType)
                and not func.return_type.size
            ):
                pass
            elif func.return_type != n.expr.type:
                self._error(
                    f"return {func.return_type} != {n.expr.type}",
                    n.lineno,
                    SemanticError.RETURN_TYPE_MISMATCH,
                )

    # --- Declaration

    def visit(self, n: Declaration, env: Symtab):
        self.check(n, env)

        # Todas las definiciones tienen nombre. Tras la
        # comprobación, el nombre debe formar parte del
        # entorno (de ahí el propósito de definirlo).
        assert n.name in env

        if "$func" in env:
            n.scope = "local"
        else:
            n.scope = "global"

    def check(self, n: VarDecl, env: Symtab):
        """
        Comprueba la declaración de variable n en el entorno symtab actual.
        Se encarga de verificar que el tipo de la variable sea valido y
        que el tipo de la variable coincida con el tipo de su valor inicial
        si es que lo tiene.
        """

        if n.type == SimpleTypes.VOID.value:
            self._error(
                f"Variable {n.name!r} has void type",
                n.lineno,
                SemanticError.VOID_VARIABLE,
            )

        if n.value:
            n.value.accept(self, env)

            if not hasattr(n.value, "type"):
                n.value.type = SimpleTypes.UNDEFINED.value

            if n.type != n.value.type:
                self._error(
                    f"Declaration {n.name!r} has type {n.type} != {n.value.type}",
                    n.lineno,
                    SemanticError.MISMATCH_DECLARATION,
                )

        # Agregar n.name a symtab aunque el tipo no sea valido
        self._add_to_env(n, env)

    def _get_unary_integer(self, n: UnaryOper):
        """
        Dado un nodo UnaryOper, devuelve el valor de la expresión n si es una expresión  unaria de enteros válida.
        De lo contrario, devuelve None.

        Por ejemplo, si la expresión es "-5", esta función devolver  -5.
        Si la expresión es "+5", esta función devolver  5.
        Si la expresión no es una expresión  unaria de enteros válida (por ejemplo "+5.5"), esta función devolver  None.
        """
        if isinstance(n.expr, Integer):
            if n.oper == "-":
                return -n.expr.value
            elif n.oper == "+":
                return n.expr.value

        return None

    def _get_varloc_integer(self, n: VarLoc, env: Symtab, msg: str):
        """
        Intentar obtener el valor de una variable.

        Uso en index o array size para validar. Si la Si la variable es un array, se produce un error,
        ya que el tamaño del array debe ser un entero. Si el valor de la variable
        no es un entero, se produce un error.

        Si el valor de la variable es un entero, se devuelve el valor. Si el valor
        de la variable es una expresión unaria de enteros válida, se devuelve el valor
        de la expresión. Si el valor de la variable es una variable, se sigue
        buscando el valor de la variable.
        """

        value_decl = env.get(n.name)
        size_value = None

        if not value_decl:
            self._error(
                f"{msg} {n.name!r} is not declared",
                n.lineno,
                SemanticError.UNDECLARED_VARIABLE,
            )
        elif isinstance(value_decl, ArrayType):
            self._error(
                f"{msg} {n.name!r} must be integer no array type",
                n.lineno,
                SemanticError.ARRAY_SIZE_MUST_BE_INTEGER,
            )
        elif value_decl.type != SimpleTypes.INTEGER.value:
            self._error(
                f"{msg} {n.name!r} must be integer no '{value_decl.type.name}'",
                n.lineno,
                SemanticError.ARRAY_SIZE_MUST_BE_INTEGER,
            )
        elif isinstance(value_decl.value, Integer):
            size_value = value_decl.value.value
        elif isinstance(value_decl.value, UnaryOper):
            size_value = self._get_unary_integer(value_decl.value)
        elif isinstance(value_decl.value, VarLoc):
            # seguir buscando el valor si es una variable
            size_value = self._get_varloc_integer(value_decl.value, env, msg)

        return size_value

    def _get_array_size(self, size, env: Symtab):
        """
        Intentar obtener el valor de un array size.
        """
        size_value = None

        if isinstance(size, Integer):
            size_value = size.value
        elif isinstance(size, UnaryOper):
            size_value = self._get_unary_integer(size)
        elif isinstance(size, VarLoc):
            size_value = self._get_varloc_integer(size, env, "Array size")

        return size_value

    def check(self, n: ArrayDecl, env: Symtab):
        # Agregar n.name a symtab
        """
        Verificar que el array decl es correcto.

        Primero, se verifica si el nombre del array ya existe en el
        entorno actual. Si no existe.

        Luego se verifica si el tipo base del array es un array
        o void. Si es alguno de los dos.

        Después, se verifica el tipo base y el valor de size. Si
        el valor de size es una variable, se sigue buscando el valor
        de la variable. Si el valor de size es una expresIón unaria de
        enteros válida, se devuelve el valor de la expresIón.

        Luego se verifica si el valor de size es un entero.

        Finalmente, se verifica si el valor de size es positivo. Si
        no lo es. Si el valor de size coincide
        con el n mero de elementos en el array, se produce un error.

        Por último, se verifica que cada elemento del array tenga el
        mismo tipo que el tipo base del array.
        """
        self._add_to_env(n, env, "Array variable")

        # Multi-dimencionales o void no soportados
        if isinstance(n.type.base, ArrayType):
            self._error(
                f"{n.name!r}",
                n.lineno,
                SemanticError.MULTI_DIMENSIONAL_ARRAYS,
            )
            return
        elif n.type.base == SimpleTypes.VOID.value:
            self._error(
                f"Array {n.name!r} has void type", n.lineno, SemanticError.VOID_ARRAY
            )
            return

        # Visitar type
        n.type.size.accept(self, env)

        if isinstance(n.type.size, VarLoc):
            loc = env.get(n.type.size.name)

            if not loc:
                self._error(
                    f"Array size '{n.type.size.name}' is not defined in {n.name!r}",
                    n.lineno,
                    SemanticError.UNDECLARED_VARIABLE,
                )
                return
        # Verificar tipo base y size
        if isinstance(n.type.size.type, ArrayType):
            self._error(
                f"No array type {n.name!r}",
                n.lineno,
                SemanticError.ARRAY_SIZE_MUST_BE_INTEGER,
            )
            return
        elif n.type.size.type != SimpleTypes.INTEGER.value:
            self._error(
                f"No '{n.type.size.type.name}' {n.name!r}",
                n.lineno,
                SemanticError.ARRAY_SIZE_MUST_BE_INTEGER,
            )
            return

        # Intentar obtener valor del size si es posible
        size_value = None

        if isinstance(n.type.size, Integer):
            size_value = n.type.size.value
        elif isinstance(n.type.size, UnaryOper):
            size_value = self._get_unary_integer(n.type.size)
        elif isinstance(n.type.size, VarLoc):
            size_value = self._get_varloc_integer(n.type.size, env, "Array size")

        # Validar valor si lo tenemos
        if size_value is not None:
            if size_value < 0:
                self._error(
                    f"Size for {n.name!r} is '{size_value}'",
                    n.lineno,
                    SemanticError.ARRAY_SIZE_MUST_BE_POSITIVE,
                )
            elif size_value != len(n.value) and n.value:
                self._error(
                    f"Size in {n.name!r} is {size_value} != {len(n.value)}",
                    n.lineno,
                    SemanticError.ARRAY_SIZE_MISMATCH,
                )

        for i, item in enumerate(n.value or [], 1):
            item.accept(self, env)

            if n.type.base != item.type:
                self._error(
                    f"Declaration {n.name!r} has type {n.type.base} != {item.type} at index {i}",
                    n.lineno,
                    SemanticError.MISMATCH_ARRAY_ASSIGNMENT,
                )

    def _override_func(self, n: FuncDecl, env: Symtab):
        """
        Verificar si se intenta sobreescribir una función.
        Si es así, verificar si los parámetros tienen los mismos tipos.

        Solo sobreescribe funciones definidas en el mismo nivel del scope actual

        Ejemplo:
            fn: function void();

            fn: function void() {...} -> Sobreescrita

            {
                fn: function void() {...} -> No sobreescrita nuevo scope
            }
        """

        old_fun = env.get(n.name, recursive=False)

        if (
            isinstance(old_fun, FuncDecl)
            and old_fun
            and not isinstance(old_fun.body, list)
            and isinstance(n.body, list)
        ):
            # sobreescribir la función
            # verificar si tienen los mismos parámetros
            # solo comprueba tipos no nombres
            if old_fun.type != n.type:
                self._error(
                    f"Function {n.name!r} return type {old_fun.type} != {n.type}",
                    n.lineno,
                    SemanticError.REDEFINE_FUNCTION_TYPE,
                )

            old_args_types = [a.type for a in old_fun.params]
            new_args_types = [a.type for a in n.params]

            if old_args_types != new_args_types:
                self._error(
                    f"Function {n.name!r} parameters types "
                    + str(old_args_types).replace("[", "(").replace("]", ")")
                    + " != "
                    + str(new_args_types).replace("[", "(").replace("]", ")"),
                    n.lineno,
                    SemanticError.REDEFINE_PARAMETER_TYPE,
                )
                return

            del env[n.name]

    def check(self, n: FuncDecl, env: Symtab):
        # Guardar la función en symtab actual
        """
        Verificar que la declaración de la función sea correcta.

        Primero, se verifica si la función ya existe en el entorno
        actual. Si no existe, se crea una nueva tabla de símbolos
        local para la función, Si existe pero la función no tiene cuerpo se sobreescribe.

        Luego se verifica el tipo de retorno y los parámetros de la
        función.

        Después, se verifica el cuerpo de la función.

        Por último, se elimina la tabla de símbolos local y se
        elimina la referencia a la función actual.

        Se produce un error si se encuentra algún error en la
        declaración de la función.
        """

        # Visitar n.type
        n.return_type.accept(self, env)
        n.type = n.return_type
        self._override_func(n, env)

        self._add_to_env(
            n,
            env,
            "Function",
            SemanticError.REDEFINE_FUNCTION_TYPE,
            SemanticError.REDEFINE_FUNCTION,
        )

        # Crear una nueva symtab (local) para Function
        env = Symtab(f"fun {n.name} in {env.name}", env)
        n.env = env

        # Magic variable that references the current function
        env["$func"] = n

        # Agregar todos los n.params dentro de symtab
        for p in n.params:
            p.accept(self, env)

        # Visitar n.stmts
        if n.body:
            for stmt in n.body:
                stmt.accept(self, env)

        if n.return_type != SimpleTypes.VOID.value and not n.body is None:
            # buscar si hay retorno return expr;
            # alerta si no hay o hay más de un return por defecto
            stms = filter(lambda stmt: isinstance(stmt, ReturnStmt), n.body)
            stms = list(stms)

            if not stms:
                print(
                    f"\n[bold yellow]Warning: Function {n.name!r} has no an default return statement[/bold yellow]"
                )
            elif len(stms) > 1:
                print(
                    f"\n[bold yellow]Warning: Function {n.name!r} has more than one default return statement[/bold yellow]"
                )

        # Eliminar la referencia a la función actual
        env["$func"] = None

    def visit(self, n: Param, env: Symtab):
        """
        Validar que Param no sea void.
        Agregar Param a la tabla de símbolos.
        """
        n.type.accept(self, env)

        if n.type == SimpleTypes.VOID.value:
            self._error(
                f"Parameter {n.name!r} has void type",
                n.lineno,
                SemanticError.VOID_PARAMETER,
            )

        # Guardar Parameter (name, type) en symtab
        self._add_to_env(
            n,
            env,
            "Parameter",
            SemanticError.REDEFINE_PARAMETER_TYPE,
            SemanticError.REDEFINE_PARAMETER,
        )

    # --- Expressions

    def visit(self, n: Literal, env: Symtab):
        # No hay nada que hacer. Los literales son
        # primitivos básicos. Ya tienen un tipo
        # definido en el archivo model.py.
        pass

    def visit(self, n: SimpleType, env: Symtab):
        # No hay nada que hacer. Los tipos simples son
        # primitivos básicos. Ya tienen un tipo
        # definido en el archivo model.py.
        # n.type = n
        pass

    def visit(self, n: AutoDecl, env: Symtab):
        # visitar primero la expresión para obtener el tipo
        if isinstance(n.value, list):
            for i, item in enumerate(n.value, 1):
                item.accept(self, env)

                if item.type in (SimpleTypes.UNDEFINED.value, SimpleTypes.VOID.value):
                    self._error(
                        f"Declaration {n.name!r} has undefined or void type at index {i}",
                        n.lineno,
                        SemanticError.VOID_ARRAY,
                    )
                    break
                elif n.type == SimpleTypes.UNDEFINED.value:
                    n.type = ArrayType(item.type, len(n.value))
                elif n.type.base != item.type:
                    self._error(
                        f"Declaration array {n.name!r} has type {n.type.base} != {item.type} at index {i}",
                        n.lineno,
                        SemanticError.MISMATCH_ARRAY_ASSIGNMENT,
                    )
                    break
        else:
            n.value.accept(self, env)
            n.type = n.value.type

            if (
                n.value.type == SimpleTypes.UNDEFINED.value
                or n.value.type == SimpleTypes.VOID.value
            ):
                self._error(
                    f"Variable {n.name!r} has undefined or void type",
                    n.lineno,
                    SemanticError.UNDEFINED_FUNCTION,
                )

        self._add_to_env(
            n,
            env,
            "VarDecl",
            SemanticError.REDEFINE_VARIABLE_TYPE,
            SemanticError.REDEFINE_VARIABLE,
        )

    def visit(self, n: ArrayType, env: Symtab):
        """ "
        ArrayDecl y ArrayLoc verifican inicialización o index
        ArrayType verifica tipos de parámetros o retorno en funciones
        Se acepta que tenga un tamaño especifico en el parámetro o retorno
        """

        n.base.accept(self, env)
        n.type = n.base

        if isinstance(n.base, ArrayType):
            self._error(
                f"In function parameters or return type",
                n.lineno,
                SemanticError.MULTI_DIMENSIONAL_ARRAYS,
            )
        elif isinstance(n.size, VarLoc) or (
            n.size and n.size.type != SimpleTypes.INTEGER.value
        ):
            self._error(
                f"Must be integer literal in function parameters or return type",
                n.lineno,
                SemanticError.ARRAY_SIZE_MUST_BE_INTEGER,
            )
        # if n.size:
        #     self._error(
        #         f"Array not supported size in function parameters or return type",
        #         n.lineno,
        #         SemanticError.ARRAY_NOT_SUPPORTED_SIZE,
        #     )

    def visit(self, n: Increment, env: Symtab):
        n.location.accept(self, env)
        n.type = n.location.type

        if n.location.type != SimpleTypes.INTEGER.value:
            self._error(
                f"Only literal integers can be incremented",
                n.lineno,
                SemanticError.INVALID_INCREMENT,
            )

    def visit(self, n: Decrement, env: Symtab):
        n.location.accept(self, env)
        n.type = n.location.type

        if n.location.type != SimpleTypes.INTEGER.value:
            self._error(
                f"Only literal integers can be decremented",
                n.lineno,
                SemanticError.INVALID_DECREMENT,
            )

    def visit(self, n: BinOper, env: Symtab):
        """
        Verificar tipos de operadores binarios.
        Verificar si la operación es soportada para los tipos
        de los operandos.
        """

        n.left.accept(self, env)
        n.right.accept(self, env)
        n.type = SimpleTypes.UNDEFINED.value

        # Verificar compatibilidad de tipos
        try:
            if isinstance(n.left.type, ArrayType) or isinstance(
                n.right.type, ArrayType
            ):
                self._error(
                    f"Array types not supported in binary operations",
                    n.lineno,
                    SemanticError.BINARY_ARRAY_OP,
                )
                return

            n.type = check_binop(n.oper, n.left.type.name, n.right.type.name)
        except CheckError as e:
            self._error(str(e), n.lineno, SemanticError.INVALID_BINARY_OP)
            n.type = SimpleTypes.UNDEFINED.value
            return

        if not n.type and (n.left.type and n.right.type):
            self._error(
                f"{n.left.type} {n.oper} {n.right.type}",
                n.lineno,
                SemanticError.BINARY_OP_TYPE,
            )

    def visit(self, n: UnaryOper, env: Symtab):
        """
        Verificar tipos de operadores unarios.
        Verificar si la operación es soportada para el tipo
        del operando.
        """

        n.expr.accept(self, env)
        n.type = SimpleTypes.UNDEFINED.value

        # Validar si es un operador unario valido
        try:
            n.type = check_unaryop(n.oper, n.expr.type.name)
        except CheckError as e:
            self._error(str(e), n.lineno, SemanticError.INVALID_UNARY_OP)
            n.type = SimpleTypes.UNDEFINED.value
            return

        if not n.type and n.expr.type:
            self._error(
                f"{n.oper} {n.expr.type}", n.lineno, SemanticError.UNARY_OP_TYPE
            )

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

    def visit(self, n: FuncCall, env: Symtab):
        """
        Visitar una llamada a función.

        Verificar si la función existe y tiene el tipo de retorno
        correcto. Luego, verificar si el número de argumentos y
        sus tipos coinciden con los parámetros de la función.

        si un parámetro es array [] se le puede pasar un array [N]

        Si la función no existe, se produce un error.
        Si el número de argumentos no coincide con el número
        de parámetros, se produce un error.
        Si los tipos de argumentos no coinciden con los tipos
        de parámetros, se produce un error.
        """
        if self._check_fun_call_builtins(n, env):
            return

        func = env.get(n.name)

        if func is None:
            self._error(
                f"Function {n.name!r} not defined",
                n.lineno,
                SemanticError.UNDEFINED_FUNCTION,
            )
            return

        if not isinstance(func, FuncDecl):
            self._error(
                f"{n.name!r} is not a function", n.lineno, SemanticError.IS_NOT_FUNCTION
            )
            return

        # El tipo de resultado es el tipo de retorno de la función
        n.type = func.return_type

        # El número de argumentos de la función debe coincidir con los parámetros
        if len(n.args) != len(func.params):
            self._error(
                f"Function {n.name!r} has {len(func.params)} parameters but {len(n.args)} arguments were given",
                n.lineno,
                SemanticError.WRONG_NUMBER_OF_ARGUMENTS,
            )
            return

        # Los tipos de argumentos de la función deben coincidir con los tipos de parámetros
        for pos, (parm, arg) in enumerate(zip(func.params, n.args), 1):
            arg.accept(self, env)

            if (
                isinstance(arg.type, ArrayType)
                and isinstance(parm.type, ArrayType)
                and not parm.type.size
                and arg.type.base == parm.type.base
            ):
                continue
            elif parm.type != arg.type:
                self._error(
                    f"Function {n.name!r} parameter {pos}. expected {parm.type} given {arg.type}",
                    arg.lineno,
                    SemanticError.MISMATCH_ARGUMENT_TYPE,
                )

    def visit(self, n: Location, env: Symtab):
        self.check(n, env)

    def visit(self, n: VarLoc, env: Symtab):
        self.check(n, env)

    def check(self, n: VarLoc, env: Symtab):
        # Verificar si n.name existe symtab
        decl = env.get(n.name)
        n.type = SimpleTypes.UNDEFINED.value

        if not decl:
            self._error(
                f"{n.name!r} is not defined",
                n.lineno,
                SemanticError.UNDECLARED_VARIABLE,
            )
            return
        elif isinstance(decl, FuncDecl):
            self._error(
                f"Function '{n.name}' used without invocation",
                n.lineno,
                SemanticError.FUNCTION_USED_AS_VALUE,
            )
            return

        # Propaga informacion sobre tipo
        n.type = decl.type

    def check(self, n: ArrayLoc, env: Symtab):
        """
        Verificar que el ArrayLoc sea correcto.
        Se verifica si el array que se est ́ accediendo existe y si es un
        array. Si no es un array, se produce un error.
        Además, se verifica que el índice sea un entero y que no
        supere el tamaño del array. Si el índice es negativo o
        supera el tamaño del array, se produce un error.
        """

        n.array.accept(self, env)
        n.index.accept(self, env)

        # verificar que array que es el ID sea de typo array
        load_arr = env.get(n.array.name)
        n.type = SimpleTypes.UNDEFINED.value

        if not load_arr:
            self._error(
                f"{n.array.name!r} array is not defined",
                n.lineno,
                SemanticError.UNDECLARED_ARRAY,
            )
            return
        # Dentro de una función se puede usar un array como parámetro comprobar que el parámetro es un array
        elif isinstance(load_arr, Param) and not isinstance(load_arr.type, ArrayType):
            self._error(
                f"{n.array.name!r} is not an array",
                n.lineno,
                SemanticError.ARRAY_EXPECTED,
            )
            return
        # si no es param array deber ser una declaración
        elif not isinstance(load_arr, Param) and not isinstance(load_arr, ArrayDecl):
            self._error(
                f"{n.array.name!r} is not an array",
                n.lineno,
                SemanticError.ARRAY_EXPECTED,
            )
            return

        # Propaga información sobre tipo
        n.type = load_arr.type.base

        # check index
        index_value = None
        n.index.accept(self, env)

        if isinstance(n.index.type, ArrayType):
            self._error(
                f"Not another array in '{load_arr.name}'",
                n.lineno,
                SemanticError.ARRAY_INDEX_MUST_BE_INTEGER,
            )
            return
        if n.index.type != SimpleTypes.INTEGER.value:
            self._error(
                f"Got {n.index.type} in '{load_arr.name}'",
                n.lineno,
                SemanticError.ARRAY_INDEX_MUST_BE_INTEGER,
            )
            return

        if isinstance(n.index, Integer):
            index_value = n.index.value
        elif isinstance(n.index, UnaryOper):
            index_value = self._get_unary_integer(n.index)
        elif isinstance(n.index, VarLoc):
            index_value = self._get_varloc_integer(n.index, env, "Array index")

        # obtener el tamaño del array
        array_size = None

        if not load_arr.type.size is None:
            array_size = self._get_array_size(load_arr.type.size, env)

        if index_value is not None:
            if index_value < 0:
                self._error(
                    f"Index {index_value} in '{load_arr.name}'",
                    n.lineno,
                    SemanticError.INDEX_MUST_BE_POSITIVE,
                )
            elif array_size is not None and index_value >= array_size:
                self._error(
                    f"Index {index_value} out of bounds for array of size {array_size} in '{load_arr.name}'",
                    n.lineno,
                    SemanticError.INDEX_OUT_OF_BOUNDS,
                )

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


if __name__ == "__main__":
    import sys

    if sys.platform != "ios":
        if len(sys.argv) != 2:
            raise SystemExit("Usage: python gcheck.py <filename>")

        filename = sys.argv[1]

    else:
        from File_Picker import file_picker_dialog

        filename = file_picker_dialog(
            title="Seleccionar una archivo",
            root_dir="./test",
            file_pattern="^.*[.]bminor",
        )

    if filename:
        from parser import Parser

        from scanner import Lexer

        txt = open(filename, encoding="utf-8").read()
        tokens = Lexer.tokenize(code)
        top = Parser.parse(tokens)
        env = Check.checker(top)

        if not errors_detected():
            env.print()
