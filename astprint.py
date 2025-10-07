from graphviz import Digraph
from rich import print

from model import *


class ASTPrinter(Visitor):
    node_defaults = {
        'shape': 'box',
        'color': 'deepskyblue',
        'style': 'filled'
    }
    edge_defaults = {
        'arrowhead': 'none',
    }
    graph_defaults = {
        'rankdir': 'TB',       # Dirección del árbol: Top to Bottom
        'nodesep': '0.5',      # Espacio horizontal entre nodos
        'ranksep': '0.75',     # Espacio vertical entre niveles
        'splines': 'true',     # Curvas suaves en las aristas
        'pad': '0.5',          # Margen alrededor del gráfico
    }

    def __init__(self):
        self.dot = Digraph('AST')
        self.dot.attr('node', **self.node_defaults)
        self.dot.attr('edge', **self.edge_defaults)
        self.dot.graph_attr.update(**self.graph_defaults)
        self._seq = 0

    @property
    def name(self):
        self._seq += 1
        return f'n{self._seq:02d}'

    @classmethod
    def render(cls, n: Node):
        dot = cls()
        n.accept(dot)

        return dot.dot

    def visit(self, n: Program):
        name = self.name
        self.dot.node(name, label='Program')
        for stmt in n.body:
            self.dot.edge(name, stmt.accept(self))
        return name

    def visit(self, n: SimpleType):
        name = self.name
        self.dot.node(name, label=f'type:{n.name}')
        return name

    def visit(self, n: VarDecl):
        name = self.name
        self.dot.node(name, label=f'VarDecl\n{n.name}')
        self.dot.edge(name, n.type.accept(self))

        if n.value:
            self.dot.edge(name, n.value.accept(self))

        return name

    def visit(self, n: Literal):
        name = self.name
        self.dot.node(name, label=f'value:{n.value}')
        return name

    def visit(self, n: ArrayDecl):
        name = self.name
        self.dot.node(name, label=f'ArrayDecl\nname:{n.name}')
        self.dot.edge(name, n.type.accept(self))

        for value in n.value:
            self.dot.edge(name, value.accept(self))

        return name

    def visit(self, n: ArrayType):
        name = self.name
        self.dot.node(name, label=f'ArrayType')
        self.dot.edge(name, n.base.accept(self))

        if n.size:
            self.dot.edge(name, n.size.accept(self), label='size')

        return name

    def visit(self, n: FuncDecl):
        name = self.name
        self.dot.node(name, label=f'FuncDecl\nname:{n.name}')
        self.dot.edge(name, n.return_type.accept(self))

        for param in n.params:
            self.dot.edge(name, param.accept(self))

        for stmt in n.body or []:
            self.dot.edge(name, stmt.accept(self))

        return name

    def visit(self, n: Param):
        name = self.name
        self.dot.node(name, label=f'Param\nname:{n.name}')
        self.dot.edge(name, n.type.accept(self))
        return name

    def visit(self, n: FuncCall):
        name = self.name
        self.dot.node(name, label=f'FuncCall\nname:{n.name}')

        for arg in n.args:
            self.dot.edge(name, arg.accept(self), label='arg')

        return name

    def visit(self, n: FuncType):
        name = self.name
        self.dot.node(name, label=f'FuncType')
        self.dot.edge(name, n.return_type.accept(self))

        for param in n.param_types:
            self.dot.edge(name, param.accept(self), label='param')

        return name

    def visit(self, n: VarLoc):
        name = self.name
        self.dot.node(name, label=f'VarLoc\nname:{n.name}')
        return name

    def visit(self, n: ReturnStmt):
        name = self.name
        self.dot.node(name, label="Return")

        if n.expr:
            self.dot.edge(name, n.expr.accept(self))

        return name

    def visit(self, n: Decrement):
        name = self.name
        self.dot.node(name, label=f"Decrement\npostfix:{n.postfix}")
        self.dot.edge(name, n.location.accept(self))
        return name

    def visit(self, n: Increment):
        name = self.name
        self.dot.node(name, label=f"Increment\npostfix:{n.postfix}")
        self.dot.edge(name, n.location.accept(self))
        return name

    def visit(self, n: IfStmt):
        name = self.name
        self.dot.node(name, label="If")
        self.dot.edge(name, n.condition.accept(self))

        for stmt in n.then_branch:
            self.dot.edge(name, stmt.accept(self), label='then')

        for stmt in n.else_branch or []:
            self.dot.edge(name, stmt.accept(self), label='else')

        return name

    def visit(self, n: Assignment):
        name = self.name
        self.dot.node(name, label=f"Assignment")
        self.dot.edge(name, n.location.accept(self))
        self.dot.edge(name, n.value.accept(self))
        return name

    def visit(self, n: ArrayLoc):
        name = self.name
        self.dot.node(name, label=f"ArrayLoc")
        self.dot.edge(name, n.array.accept(self))
        self.dot.edge(name, n.index.accept(self), label='index')
        return name

    def visit(self, n: BinOper):
        name = self.name
        self.dot.node(name, label=f'{n.oper}', shape='circle')
        self.dot.edge(name, n.left.accept(self))
        self.dot.edge(name, n.right.accept(self))
        return name

    def visit(self, n: UnaryOper):
        name = self.name
        self.dot.node(name, label=f'{n.oper}', shape='circle')
        self.dot.edge(name, n.expr.accept(self))
        return name

    def visit(self, n: PrintStmt):
        name = self.name
        self.dot.node(name, label="Print")

        for expr in n.expr:
            self.dot.edge(name, expr.accept(self), label='arg')

        return name

    def visit(self, n: ForStmt):
        name = self.name
        self.dot.node(name, label="For")

        if n.init:
            self.dot.edge(name, n.init.accept(self))
        if n.condition:
            self.dot.edge(name, n.condition.accept(self), label='condition')
        if n.update:
            self.dot.edge(name, n.update.accept(self), label='update')

        for stmt in n.body:
            self.dot.edge(name, stmt.accept(self), label='body')

        return name

    def visit(self, n: WhileStmt):
        name = self.name
        self.dot.node(name, label="While")

        if n.condition:
            self.dot.edge(name, n.condition.accept(self), label='condition')

        for stmt in n.body:
            self.dot.edge(name, stmt.accept(self), label='body')

        return name

    def visit(self, n: DoWhileStmt):
        name = self.name
        self.dot.node(name, label="DoWhile")

        for stmt in n.body:
            self.dot.edge(name, stmt.accept(self), label='body')
        if n.condition:
            self.dot.edge(name, n.condition.accept(self), label='condition')

        return name


if __name__ == '__main__':
    import sys
    from scanner import Lexer
    from parser import Parser

    if len(sys.argv) != 2:
        raise SystemExit("Usage: python astprint.py <filename>")

    txt = open(sys.argv[1], encoding='utf-8').read()
    tokens = Lexer().tokenize(txt)
    ast = Parser().parse(tokens)

    dot = ASTPrinter.render(ast)
    print(dot)
    dot.format = 'svg'
    dot.render(f"{sys.argv[1].split('.')[0]}", view=True)
