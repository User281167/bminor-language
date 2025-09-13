from dataclasses import dataclass, field
from multimethod import multimeta, multimethod
from typing import List, Union, Optional

# =====================================================================
# Clases Abstractas
# =====================================================================


class Visitor(metaclass=multimeta):
    pass


@dataclass
class Node:
    def accept(self, v: Visitor, *args, **kwargs):
        return v.visit(self, *args, **kwargs)


@dataclass
class Statement(Node):
    pass


@dataclass
class Expression(Node):
    pass

# =====================================================================
# Definiciones
# =====================================================================


@dataclass
class Program(Statement):
    body: List[Statement] = field(default_factory=list)


@dataclass
class Declaration(Statement):
    pass


@dataclass
class Type(Expression):
    pass


@dataclass
class SimpleType(Type):
    name: str  # integer, float, string, boolean


@dataclass
class ArrayType(Type):
    base: Type  # tipo simple o array
    size: Expression = None  # tamaño del array o None = []


@dataclass
class FuncType(Type):
    return_type: Type  # simple type | array type
    param_types: List[Type] = field(
        default_factory=list)  # tipos de parámetros


@dataclass
class VarDecl(Declaration):
    name: str
    type: Type
    value: Optional[Expression] = None


'''
Statement
    -- VarParm
    -- ArrayParm

  -- IfStmt
  -- ReturnStmt
  |
  +-- PrintStmt
  |
  +-- ForStmt
  |
  +-- WhileStmt
  |
  +-- DoWhileStmt
  |
  +-- Assignment
'''


@dataclass
class ReturnStmt(Statement):
    expr: Optional[Expression] = None  # puede ser return; o return expr;


@dataclass
class IfStmt(Statement):
    condition: Expression
    then_branch: List[Statement]
    else_branch: Optional[List[Statement]] = None


@dataclass
class WhileStmt(Statement):
    condition: Expression
    body: List[Statement]


@dataclass
class DoWhileStmt(Statement):
    body: List[Statement]
    condition: Expression


@dataclass
class ForStmt(Statement):
    init: Optional[Statement]
    condition: Optional[Expression]
    update: Optional[Statement]
    body: List[Statement]


@dataclass
class Location(Expression):
    pass


@dataclass
class Assignment(Statement):
    location: Location
    value: Expression


@dataclass
class PrintStmt(Statement):
    expr: Expression


'''
  +-- Declaration (abstract)
  | |
  | +-- VarDecl: Guardar la información de una declaración de variable
  | |
  | +-- ArrayDecl: Declaración de Arreglos (multi-dimencioanles)
  | |
  | +-- FuncDecl: Para guardar información sobre las funciones declaradas
'''


@dataclass
class ArrayDecl(Declaration):
    name: str
    type: ArrayType  # tipo de arreglo multi-dimensional
    size: Expression  # tamaño de arreglo evaluado
    value: List[Expression] = field(default_factory=list)  # valores iniciales


@dataclass
class Param(Node):
    # representar parámetros como x: INTEGER o arr: ARRAY [10] FLOAT.
    # param ::= 'ID' ':' type_simples
    name: str
    type: Type


@dataclass
class FuncDecl(Declaration):
    """
    return_type: puede ser SimpleType, ArrayType, etc.
    params: lista de nodos Param, que contienen nombre y tipo.
    body: lista de sentencias (Statement) que forman el bloque { ... }.

    FuncDecl(
        name="sum",
        return_type=SimpleType("integer"),
        params=[
            Param("a", SimpleType("integer")),
            Param("b", SimpleType("integer"))
        ],
        body=[
            ReturnStmt(BinOper("+", VarLoc("a"), VarLoc("b")))
        ]
    )
    """
    name: str
    return_type: Type
    params: List[Param] = field(default_factory=list)
    body: List[Statement] = field(default_factory=list)


# Expresiones


@dataclass
class BinOper(Expression):
    oper: str
    left: Expression
    right: Expression


@dataclass
class UnaryOper(Expression):
    oper: str
    expr: Expression


@dataclass
class Literal(Expression):
    value: Union[int, float, str, bool]
    type: str = None


@dataclass
class Integer(Literal):
    value: int

    def __post_init__(self):
        assert isinstance(self.value, int), "Value debe ser un 'integer'"
        self.type = 'integer'


@dataclass
class Float(Literal):
    value: float

    def __post_init__(self):
        assert isinstance(self.value, float), "Value debe ser un 'float'"
        self.type = 'float'


@dataclass
class Boolean(Literal):
    value: bool

    def __post_init__(self):
        assert isinstance(self.value, bool), "Value debe ser un 'boolean'"
        self.type = 'boolean'


'''
  - Char
  - String
  - Increment (pre/post fijo)
  - Decrement
  - FuncCall
'''


@dataclass
class FuncCall(Expression):
    name: str
    args: List[Expression] = field(default_factory=list)


@dataclass
class Char(Literal):
    value: str

    def __post_init__(self):
        # remove "''"
        self.value = self.value[1:-1]

        assert isinstance(self.value, str) and len(
            self.value) == 1, "Debe ser un solo carácter"
        self.type = 'char'


@dataclass
class String(Literal):
    value: str

    def __post_init__(self):
        # remove "''"
        self.value = self.value[1:-1]

        assert isinstance(self.value, str), "Debe ser una cadena de texto"
        self.type = 'string'


'''
  +-- Location ('load'/'store')
    -- VarLoc
    -- ArrayLoc

'''


@dataclass
class VarLoc(Location):
    name: str  # nombre de la variable


@dataclass
class ArrayLoc(Location):
    array: Expression  # VarLoc u otra expresión que evalúe a un arreglo
    index: Expression  # expresión que representa el índice


@dataclass
class Increment(Expression):
    location: Location
    # True si es postfijo (x++), False si es prefijo (++x)
    postfix: bool = False


@dataclass
class Decrement(Expression):
    location: Location
    postfix: bool = False
