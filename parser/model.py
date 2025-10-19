from dataclasses import dataclass, field
from typing import List, Optional, Union

from multimethod import multimeta, multimethod
from rich.console import Console
from rich.text import Text
from rich.tree import Tree

console = Console()

# =====================================================================
# Clases Abstractas
# =====================================================================


class Visitor(metaclass=multimeta):
    # multimeta para hacer double dispatch
    # Double dispatch (envío doble)
    # vinculación dinámica junto a métodos sobrecargados.
    pass


@dataclass
class Node:
    def accept(self, v: Visitor, *args, **kwargs):
        return v.visit(self, *args, **kwargs)

    def pretty(self, show_lineno=False):
        tree = self._build_tree(show_lineno)
        console.print(tree)

    def _build_tree(self, show_lineno=False, indent=0):
        label = Text(f"{self.__class__.__name__}", style="bold magenta")
        tree = Tree(label)

        for field_name, value in self.__dict__.items():
            if field_name == "lineno" and not show_lineno:
                continue

            field_label = Text(f"{field_name}:", style="bold cyan")

            if isinstance(value, Node):
                subtree = value._build_tree(show_lineno, indent + 1)
                tree.add(Tree(field_label).add(subtree))
            elif isinstance(value, list):
                list_tree = Tree(field_label)
                for item in value:
                    if isinstance(item, Node):
                        list_tree.add(item._build_tree(show_lineno, indent + 1))
                    else:
                        list_tree.add(Text(str(item), style="green"))
                tree.add(list_tree)
            else:
                tree.add(Text(f"{field_name}: {value}", style="green"))

        return tree

    def to_string(self, indent=0, show_lineo=False):
        pad = "  " * indent
        result = f"{pad}{self.__class__.__name__}("

        for field_name, value in self.__dict__.items():
            if field_name == "lineno" and not show_lineo:
                continue

            if isinstance(value, Node):
                result += f"\n{pad}  {field_name}:\n{value.to_string(indent + 2)}"
            elif isinstance(value, list):
                result += f"\n{pad}  {field_name}: ["

                for item in value:
                    if isinstance(item, Node):
                        result += f"\n{item.to_string(indent + 2)}"
                    else:
                        result += f"\n{pad}    {item}"

                result += f"\n{pad}  ]"
            else:
                result += f"\n{pad}  {field_name}: {value}"

        result += f"\n{pad})"

        return result

    def __str__(self):
        return self.to_string()

    def __repr__(self):
        return self.to_string()


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

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name


@dataclass
class ArrayType(Type):
    base: Type  # tipo simple o array
    size: Expression = None  # tamaño del array o None = []


@dataclass
class FuncType(Type):
    return_type: Type  # simple type | array type
    param_types: List[Type] = field(default_factory=list)  # tipos de parámetros


@dataclass
class VarDecl(Declaration):
    name: str
    type: Type
    value: Optional[Expression] = None


"""
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
"""


@dataclass
class ReturnStmt(Statement):
    expr: Optional[Expression] = None  # puede ser return; o return expr;


@dataclass
class IfStmt(Statement):
    condition: Expression
    then_branch: List[Statement]
    else_branch: List[Statement] = None


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
    expr: List[Expression] = field(default_factory=list)


"""
  +-- Declaration (abstract)
  | |
  | +-- VarDecl: Guardar la información de una declaración de variable
  | |
  | +-- ArrayDecl: Declaración de Arreglos (multi-dimencioanles)
  | |
  | +-- FuncDecl: Para guardar información sobre las funciones declaradas
"""


@dataclass
class ArrayDecl(Declaration):
    name: str
    type: ArrayType  # tipo de arreglo multi-dimensional
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
    # type: str = None
    type: SimpleType = field(init=False)


@dataclass
class Integer(Literal):
    value: int

    def __post_init__(self):
        assert isinstance(self.value, int), "Value debe ser un 'integer'"
        self.type = SimpleType("integer")


@dataclass
class Float(Literal):
    value: float

    def __post_init__(self):
        assert isinstance(self.value, float), "Value debe ser un 'float'"
        self.type = SimpleType("float")


@dataclass
class Boolean(Literal):
    value: bool

    def __post_init__(self):
        assert isinstance(self.value, bool), "Value debe ser un 'boolean'"
        self.type = SimpleType("boolean")


"""
  - Char
  - String
  - Increment (pre/post fijo)
  - Decrement
  - FuncCall
"""


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

        # assert isinstance(self.value, str) and len(
        # self.value) in (0, 1), "Debe ser un solo carácter"
        self.type = SimpleType("char")


@dataclass
class String(Literal):
    value: str

    def __post_init__(self):
        # remove "''"
        self.value = self.value[1:-1]

        # assert isinstance(self.value, str), "Debe ser una cadena de texto"
        self.type = SimpleType("string")


"""
  +-- Location ('load'/'store')
    -- VarLoc
    -- ArrayLoc

"""


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


from enum import Enum


class SimpleTypes(Enum):
    INTEGER = SimpleType("integer")
    FLOAT = SimpleType("float")
    BOOLEAN = SimpleType("boolean")
    CHAR = SimpleType("char")
    STRING = SimpleType("string")
    VOID = SimpleType("void")

    UNDEFINED = SimpleType("undefined")
