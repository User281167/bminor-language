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
from typing import List, Union

from utils import error

from .semantic_error import SemanticError
from .symtab import Symtab
from .typesys import CheckError, check_binop, check_unaryop, typenames


class Check(Visitor):
    @classmethod
    def checker(cls, n: Program):
        checker = cls()

        # Crear una nueva tabla de simbolos
        env = Symtab("global")

        # Visitar todas las declaraciones
        for decl in n.body:
            decl.accept(checker, env)

        return env

    def _error(self, msg: str, lineno: int, error_type: SemanticError = None):
        error(f"{error_type or SemanticError.UNKNOWN}: {msg}", lineno, error_type)

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
            self._error(f"{dec_type} '{n.name}' is already defined", n.lineno, conflict)
        except Symtab.SymbolDefinedError as ex:
            self._error(f"{dec_type} '{n.name}' is already defined", n.lineno, defined)

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
            return

        if n.location.type != n.value.type:
            name = None

            if isinstance(n.location, VarLoc):
                name = "variable " + n.location.name
            elif isinstance(n.location, ArrayLoc):
                name = "array " + n.location.array.name

            self._error(
                f"Assignment {n.location.type} != {n.value.type} in {name}",
                n.lineno,
                SemanticError.MISMATCH_ASSIGNMENT,
            )

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
                f"Variable '{n.name}' has void type",
                n.lineno,
                SemanticError.VOID_VARIABLE,
            )

        if n.value:
            n.value.accept(self, env)

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
        Dado un nodo UnaryOper, devuelve el valor de la expresi o n si es una expresi o n  unaria de enteros v lida.
        De lo contrario, devuelve None.

        Por ejemplo, si la expresi o n es "-5", esta funci o n devolver  -5.
        Si la expresi o n es "+5", esta funci o n devolver  5.
        Si la expresi o n no es una expresi o n  unaria de enteros v lida (por ejemplo "+5.5"), esta funci o n devolver  None.
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
                f"{msg} '{n.name}' is not declared",
                n.lineno,
                SemanticError.UNDECLARED_VARIABLE,
            )
        elif isinstance(value_decl, ArrayType):
            self._error(
                f"{msg} '{n.name}' must be integer no array type",
                n.lineno,
                SemanticError.ARRAY_SIZE_MUST_BE_INTEGER,
            )
        elif value_decl.type != SimpleTypes.INTEGER.value:
            self._error(
                f"{msg} '{n.name}' must be integer no '{value_decl.type.name}'",
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
                f"Multi-dimensional arrays are not supported '{n.name}'",
                n.lineno,
                SemanticError.MULTI_DIMENSIONAL_ARRAYS,
            )
            return
        elif n.type.base == SimpleTypes.VOID.value:
            self._error(
                f"Array '{n.name}' has void type", n.lineno, SemanticError.VOID_ARRAY
            )
            return

        # Visitar type
        n.type.size.accept(self, env)

        if isinstance(n.type.size, VarLoc):
            loc = env.get(n.type.size.name)

            if not loc:
                self._error(
                    f"Array size '{n.type.size.name}' is not defined in '{n.name}'",
                    n.lineno,
                    SemanticError.UNDECLARED_VARIABLE,
                )
                return
        # Verificar tipo base y size
        if isinstance(n.type.size.type, ArrayType):
            self._error(
                f"Array size must be integer no array type '{n.name}'",
                n.lineno,
                SemanticError.ARRAY_SIZE_MUST_BE_INTEGER,
            )
            return
        elif n.type.size.type != SimpleTypes.INTEGER.value:
            self._error(
                f"Array size must be integer no '{n.type.size.type.name}' '{n.name}'",
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
                    f"Array size for '{n.name}' must be positive no '{size_value}'",
                    n.lineno,
                    SemanticError.ARRAY_SIZE_MUST_BE_POSITIVE,
                )
            elif size_value != len(n.value) and n.value:
                self._error(
                    f"Array size in '{n.name}' is {size_value} != {len(n.value)}",
                    n.lineno,
                    SemanticError.ARRAY_SIZE_MISMATCH,
                )

        for item in n.value or []:
            item.accept(self, env)

            if n.type.base != item.type:
                self._error(
                    f"Declaration {n.name} has type {n.type.base} != {item.type}",
                    n.lineno,
                    SemanticError.MISMATCH_ARRAY_ASSIGNMENT,
                )

    def check(self, n: FuncDecl, env: Symtab):
        # Guardar la función en symtab actual
        """
        Verificar que la declaración de la función sea correcta.

        Primero, se verifica si la función ya existe en el entorno
        actual. Si no existe, se crea una nueva tabla de símbolos
        local para la función.

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

        self._add_to_env(
            n,
            env,
            "Function",
            SemanticError.REDEFINE_FUNCTION_TYPE,
            SemanticError.REDEFINE_FUNCTION,
        )

        # Crear una nueva symtab (local) para Function
        # env = Symtab("function " + n.name, env)
        env = Symtab("function " + n.name, env)
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

        env["$func"] = None

    def visit(self, n: Param, env: Symtab):
        """
        Validar que Param no sea void.
        Agregar Param a la tabla de símbolos.
        """
        n.type.accept(self, env)

        if n.type == SimpleTypes.VOID.value:
            self._error(
                f"Parameter '{n.name}' has void type",
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
        pass

    def visit(self, n: ArrayType, env: Symtab):
        """ "
        ArrayDecl y ArrayLoc verifican inicialización o index
        ArrayTpe verifica tipos de parámetros o retorno en funciones
        No se acepta que tenga un tamaño especifico en el parámetro o retorno
        """

        n.base.accept(self, env)

        if isinstance(n.base, ArrayType):
            self._error(
                f"Multidimensional arrays are not supported in function parameters or return type",
                n.lineno,
                SemanticError.MULTI_DIMENSIONAL_ARRAYS,
            )
        if n.size:
            self._error(
                f"Array not supported size in function parameters or return type",
                n.lineno,
                SemanticError.ARRAY_NOT_SUPPORTED_SIZE,
            )

    def visit(self, n: BinOper, env: Symtab):
        """
        Verificar tipos de operadores binarios.
        Verificar si la operación es soportada para los tipos
        de los operandos.
        """

        n.left.accept(self, env)
        n.right.accept(self, env)

        # Verificar compatibilidad de tipos
        try:
            n.type = check_binop(n.oper, n.left.type.name, n.right.type.name)
        except CheckError as e:
            self._error(str(e), n.lineno, SemanticError.INVALID_BINARY_OP)
            n.type = SimpleTypes.UNDEFINED
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

        # Validar si es un operador unario valido
        try:
            n.type = check_unaryop(n.oper, n.expr.type.name)
        except CheckError as e:
            self._error(str(e), n.lineno, SemanticError.INVALID_UNARY_OP)
            n.type = SimpleTypes.UNDEFINED
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
        func = env.get(n.name)

        if func is None:
            self._error(
                f"Function {n.name} not defined",
                n.lineno,
                SemanticError.UNDEFINED_FUNCTION,
            )
            return

        # La funcion debe ser una Function
        if not isinstance(func, FuncDecl):
            self._error(
                f"{n.name} is not a function", n.lineno, SemanticError.IS_NOT_FUNCTION
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

            if parm.type != arg.type:
                self._error(
                    f"Function {n.name!r} parameter {pos}. expected {parm.type} given {arg.type}",
                    arg.lineno,
                    SemanticError.MISMATCH_ARGUMENT_TYPE,
                )

    def visit(self, n: Location, env: Symtab):
        self.check(n, env)

    def check(self, n: VarLoc, env: Symtab):
        # Verificar si n.name existe symtab
        decl = env.get(n.name)

        if not decl:
            self._error(
                f"{n.name!r} is not defined",
                n.lineno,
                SemanticError.UNDECLARED_VARIABLE,
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
        n.type = SimpleTypes.UNDEFINED

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
                f"Array index must be integer, not another array in '{load_arr.name}'",
                n.lineno,
                SemanticError.ARRAY_INDEX_MUST_BE_INTEGER,
            )
            return
        if n.index.type != SimpleTypes.INTEGER.value:
            self._error(
                f"Array index must be integer, not {n.index.type} for array '{load_arr.name}'",
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
                    f"Index {index_value} cannot be negative for array '{load_arr.name}'",
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
