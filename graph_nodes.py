from astprint import ASTPrinter
from model import *
from scanner import Lexer
from parser import Parser


def save_graph_svg(code: str, path: str):
    tokens = Lexer().tokenize(code)
    ast = Parser().parse(tokens)
    asb_path = "./ast_img/" + path

    dot = ASTPrinter.render(ast)
    dot.format = 'svg'
    dot.render(asb_path, view=False)


if __name__ == '__main__':
    # declarations
    save_graph_svg("x:integer = 5;", VarDecl.__name__)
    save_graph_svg("x:array [1] integer;", ArrayDecl.__name__)
    save_graph_svg(
        "x:array [2] integer = {1, 2};", ArrayDecl.__name__ + "_init_list")

    # function declaration
    save_graph_svg("main: function integer();", FuncDecl.__name__)
    save_graph_svg(
        "main: function integer(x: string, y: float);", FuncDecl.__name__ + "_params")
    save_graph_svg(
        "main: function array [2] char();", FuncDecl.__name__ + "_array")

    save_graph_svg("x:integer = main(123, abc);", FuncDecl.__name__+"_call")

    save_graph_svg(
        "main: function integer() = {x = 5;}", VarDecl.__name__ + "body")

    save_graph_svg(
        "main: function integer() = {if (x()){x++;}}", VarDecl.__name__ + "funttype")

    # return
    save_graph_svg(
        "main: function integer() = {return x;}", ReturnStmt.__name__)

    # inc, dec
    save_graph_svg(
        "main: function integer() = {x++;}", Increment.__name__)
    save_graph_svg(
        "main: function integer() = {--x;}", Decrement.__name__)

    # if
    save_graph_svg(
        "main: function integer() = {if (x()){x++;}}", IfStmt.__name__)
    save_graph_svg(
        "main: function integer() = {if (false){x++;} else {x--;}}", IfStmt.__name__ + "_else")
    save_graph_svg(
        "main: function integer() = {if (x){x++;} else if (y()){y--;} else {y++;}}", IfStmt.__name__ + "_else_if")

    # loc
    save_graph_svg(
        "main: function integer() = {x = 5;}", Assignment.__name__)
    save_graph_svg(
        "main: function integer() = {x[1] = 5;}", ArrayLoc.__name__)

    # unary
    save_graph_svg(
        "main: function integer() = {!x;}", UnaryOper.__name__)
    save_graph_svg(
        "main: function integer() = {-x;}", UnaryOper.__name__ + "_neg")

    # bin
    save_graph_svg(
        "main: function integer() = {x + y;}", BinOper.__name__ + "_add")
    save_graph_svg(
        "main: function integer() = {x ^ y;}", BinOper.__name__ + "_pow")
    save_graph_svg(
        "main: function integer() = {x == y;}", BinOper.__name__ + "_eq")
    save_graph_svg(
        "main: function integer() = {x != y;}", BinOper.__name__ + "_ne")
    save_graph_svg(
        "main: function integer() = {x <= y;}", BinOper.__name__ + "_le")

    # print
    save_graph_svg(
        "main: function integer() = {print x, \"hello\", y();}", PrintStmt.__name__)

    # loops
    save_graph_svg(
        "main: function integer() = {for (x = 0; x < 10; x++){x++;}}", ForStmt.__name__)
    save_graph_svg(
        "main: function integer() = {for (; ;){x++;}}", ForStmt.__name__+"_empty")

    save_graph_svg(
        "main: function integer() = {while (x < 10){x++;x = x + 1;}}", WhileStmt.__name__)

    save_graph_svg(
        "main: function integer() = {while (){x++;}}", WhileStmt.__name__+"_empty")

    save_graph_svg(
        "main: function integer() = {do {x++;x = x + 1;} while (x < 10);}", DoWhileStmt.__name__)

    # expr
    save_graph_svg(
        "x: integer = 1 + 3 * 5 - 2 / 2;", BinOper.__name__ + "_expr")
    # logical expr
    save_graph_svg(
        "x: boolean = 1 && 2 || 3 && 4 || 5 && 6;", BinOper.__name__ + "_logical")
    # relational expr
    save_graph_svg(
        "x: boolean = 1 == 2 != 3 <= 4 >= 5 < 6 > 7;", BinOper.__name__ + "_relational")
    # additive expr
    save_graph_svg(
        "x: integer = 1 + 2 - 3 * 4 / 5 % 6;", BinOper.__name__ + "_additive")
    # multiplicative expr
    save_graph_svg(
        "x: integer = 1 * 2 / 3 % 4 + 5 - 6;", BinOper.__name__ + "_multiplicative")
    # unary expr
    save_graph_svg(
        "x: integer = !1 + -2 * 3 / 4 % 5 - 6;", UnaryOper.__name__ + "_unary")

    # sieve
    with open("./bminor-examples/sieve.bminor", encoding='utf-8') as f:
        code = f.read()
        save_graph_svg(code, "sieve")
    # knight
    with open("./bminor-examples/knight.bminor", encoding='utf-8') as f:
        code = f.read()
        save_graph_svg(code, "knight")
    # test
    with open("./bminor-examples/test.bminor", encoding='utf-8') as f:
        code = f.read()
        save_graph_svg(code, "test")
