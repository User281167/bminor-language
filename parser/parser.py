# grammar.py
import logging

import sly
from rich import print

from scanner import Lexer
from utils import error, errors_detected

from .model import *
from .parser_errors import ParserError


def _L(node, p):
    node.lineno = p.lineno
    return node


class Parser(sly.Parser):
    log = logging.getLogger()
    log.setLevel(logging.ERROR)
    expected_shift_reduce = 1
    debugfile = "grammar.txt"

    tokens = Lexer.tokens

    @_("decl_list")
    def prog(self, p):
        return Program(p.decl_list)

    # Declarations

    @_("decl decl_list")
    def decl_list(self, p):
        return [p.decl] + p.decl_list

    @_("empty")
    def decl_list(self, p):
        return []

    @_("ID ':' type_simple ';'")
    def decl(self, p):
        return _L(VarDecl(name=p.ID, type=p.type_simple), p)

    @_("ID ':' type_array_sized ';'")
    def decl(self, p):
        return _L(ArrayDecl(name=p.ID, type=p.type_array_sized), p)

    @_("ID ':' type_func ';'")
    def decl(self, p):
        return _L(
            FuncDecl(
                name=p.ID,
                return_type=p.type_func.return_type,
                params=p.type_func.param_types,
                body=[],
            ),
            p,
        )

    @_("decl_init")
    def decl(self, p):
        return p.decl_init

    @_("ID ':' type_simple '=' expr ';'")
    def decl_init(self, p):
        return _L(VarDecl(name=p.ID, type=p.type_simple, value=p.expr), p)

    @_("ID ':' type_array_sized '=' '{' opt_expr_list '}' ';'")
    def decl_init(self, p):
        # type_array_sized.size ya contiene la expresión del índice en el modelo ArrayType
        return _L(
            ArrayDecl(name=p.ID, type=p.type_array_sized, value=p.opt_expr_list), p
        )

    @_("ID ':' type_func '=' '{' opt_stmt_list '}'")
    def decl_init(self, p):
        return _L(
            FuncDecl(
                name=p.ID,
                return_type=p.type_func.return_type,
                params=p.type_func.param_types,
                body=p.opt_stmt_list,
            ),
            p,
        )

    # Statements

    @_("stmt_list")
    def opt_stmt_list(self, p):
        return p.stmt_list

    @_("empty")
    def opt_stmt_list(self, p):
        return []

    @_("stmt stmt_list")
    def stmt_list(self, p):
        return [p.stmt] + p.stmt_list

    @_("stmt")
    def stmt_list(self, p):
        return [p.stmt]
        # return _L(BlockStmt([p.stmt]), p)

    @_("open_stmt")
    @_("closed_stmt")
    def stmt(self, p):
        return p[0]

    @_("if_stmt_closed")
    @_("for_stmt_closed")
    @_("simple_stmt")
    def closed_stmt(self, p):
        return p[0]

    @_("if_stmt_open", "for_stmt_open")
    def open_stmt(self, p):
        return p[0]

    # @_("IF '(' opt_expr ')'")
    @_("IF '(' expr ')'")
    def if_cond(self, p):
        # return p.opt_expr
        return p.expr

    @_("if_cond closed_stmt ELSE closed_stmt")
    def if_stmt_closed(self, p):
        return _L(
            IfStmt(
                condition=p.if_cond,
                then_branch=p.closed_stmt0,
                else_branch=p.closed_stmt1,
            ),
            p,
        )

    @_("if_cond stmt")
    def if_stmt_open(self, p):
        return _L(
            IfStmt(
                condition=p.if_cond,
                then_branch=p.stmt,
            ),
            p,
        )

    @_("if_cond closed_stmt ELSE if_stmt_open")
    def if_stmt_open(self, p):
        return _L(
            IfStmt(
                condition=p.if_cond,
                then_branch=p.closed_stmt,
                else_branch=p.if_stmt_open,
            ),
            p,
        )

    @_("FOR '(' opt_expr ';' opt_expr ';' opt_expr ')'")
    def for_header(self, p):
        return (p.opt_expr0, p.opt_expr1, p.opt_expr2)

    @_("for_header open_stmt")
    def for_stmt_open(self, p):
        init, cond, update = p.for_header
        return _L(
            ForStmt(
                init=init,
                condition=cond,
                update=update,
                body=p.open_stmt,
            ),
            p,
        )

    @_("for_header closed_stmt")
    def for_stmt_closed(self, p):
        init, cond, update = p.for_header
        return _L(
            ForStmt(init=init, condition=cond, update=update, body=p.closed_stmt),
            p,
        )

    @_("WHILE '(' opt_expr ')' open_stmt")
    def while_stmt_open(self, p):
        return _L(
            WhileStmt(
                condition=p.opt_expr,
                body=p.open_stmt,
            ),
            p,
        )

    @_("WHILE '(' opt_expr ')' closed_stmt")
    def while_stmt_closed(self, p):
        return _L(
            WhileStmt(
                condition=p.opt_expr,
                body=p.closed_stmt,
            ),
            p,
        )

    @_("while_stmt_open")
    def open_stmt(self, p):
        return p.while_stmt_open

    @_("while_stmt_closed")
    def closed_stmt(self, p):
        return p.while_stmt_closed

    @_("DO closed_stmt WHILE '(' expr ')' ';'")
    def do_while_stmt(self, p):
        return _L(
            DoWhileStmt(
                body=p.closed_stmt,
                condition=p.expr,
            ),
            p,
        )

    @_("do_while_stmt")
    def closed_stmt(self, p):
        return p.do_while_stmt

    # Simple statements are not recursive

    @_("print_stmt")
    @_("return_stmt")
    @_("continue_stmt")
    @_("break_stmt")
    @_("block_stmt")
    @_("decl")
    @_("expr ';'")
    def simple_stmt(self, p):
        return p[0]

    @_("PRINT opt_expr_list ';'")
    def print_stmt(self, p):
        return _L(PrintStmt(p.opt_expr_list), p)

    @_("RETURN opt_expr ';'")
    def return_stmt(self, p):
        return _L(ReturnStmt(p.opt_expr), p)

    @_("CONTINUE ';'")
    def continue_stmt(self, p):
        return _L(ContinueStmt(), p)

    @_("BREAK ';'")
    def break_stmt(self, p):
        return _L(BreakStmt(), p)

    @_("'{' stmt_list '}'")
    def block_stmt(self, p):
        return _L(BlockStmt(p.stmt_list), p)
        # return p.stmt_list  # ya que stmt_list devuelve una lista de Statement

    # Expressions

    @_("empty")
    def opt_expr_list(self, p):
        return []

    @_("expr_list")
    def opt_expr_list(self, p):
        return p.expr_list

    @_("expr ',' expr_list")
    def expr_list(self, p):
        return [p.expr] + p.expr_list

    @_("expr")
    def expr_list(self, p):
        return [p.expr]

    # TODO
    @_("empty")
    def opt_expr(self, p):
        return None

    @_("expr")
    def opt_expr(self, p):
        return p.expr

    @_("expr1")
    def expr(self, p):
        return p.expr1

    @_("lval '=' expr1")
    def expr1(self, p):
        return _L(Assignment(p.lval, p.expr1), p)

    @_("lval '=' expr ';'")
    # puede ser una sentencia
    def simple_stmt(self, p):
        return _L(Assignment(location=p.lval, value=p.expr), p)

    @_("expr2")
    def expr1(self, p):
        return p.expr2

    @_("ID")
    def lval(self, p):
        return _L(_L(VarLoc(p.ID), p), p)

    @_("ID index")
    def lval(self, p):
        return _L(ArrayLoc(array=_L(VarLoc(p.ID), p), index=p[1]), p)

    @_("expr2 LOR expr3")
    def expr2(self, p):
        return _L(BinOper("LOR", p.expr2, p.expr3), p)

    @_("expr3")
    def expr2(self, p):
        return p.expr3

    @_("expr3 LAND expr4")
    def expr3(self, p):
        return _L(BinOper("LAND", p.expr3, p.expr4), p)

    @_("expr4")
    def expr3(self, p):
        return p.expr4

    @_("expr4 EQ expr5")
    @_("expr4 NE expr5")
    @_("expr4 LT expr5")
    @_("expr4 LE expr5")
    @_("expr4 GT expr5")
    @_("expr4 GE expr5")
    def expr4(self, p):
        return _L(BinOper(p[1], p.expr4, p.expr5), p)

    @_("expr5")
    def expr4(self, p):
        return p.expr5

    @_("expr5 '+' expr6")
    @_("expr5 '-' expr6")
    def expr5(self, p):
        return _L(BinOper(p[1], p.expr5, p.expr6), p)

    @_("expr6")
    def expr5(self, p):
        return p.expr6

    @_("expr6 '*' expr7")
    @_("expr6 '/' expr7")
    @_("expr6 '%' expr7")
    def expr6(self, p):
        return _L(BinOper(p[1], p.expr6, p.expr7), p)

    @_("expr7")
    def expr6(self, p):
        return p.expr7

    @_("expr7 '^' expr8")
    def expr7(self, p):
        return _L(BinOper(p[1], p.expr7, p.expr8), p)

    @_("expr8")
    def expr7(self, p):
        return p.expr8

    @_("'-' expr8")
    @_("'+' expr8")
    @_("'!' expr8")
    def expr8(self, p):
        return _L(UnaryOper(p[0], p.expr8), p)

    @_("expr9")
    def expr8(self, p):
        return p.expr9

    @_("expr9 INC")
    def expr9(self, p):
        return _L(Increment(location=p.expr9, postfix=True), p)

    @_("INC expr9")
    def expr9(self, p):
        return _L(Increment(location=p.expr9, postfix=False), p)

    @_("expr9 DEC")
    def expr9(self, p):
        return _L(Decrement(location=p.expr9, postfix=True), p)

    @_("DEC expr9")
    def expr9(self, p):
        return _L(Decrement(location=p.expr9, postfix=False), p)

    @_("group")
    def expr9(self, p):
        return p.group

    @_("'(' expr ')'")
    def group(self, p):
        return p.expr

    @_("ID '(' opt_expr_list ')'")
    def group(self, p):
        return _L(FuncCall(name=p.ID, args=p.opt_expr_list), p)

    @_("ID index")
    def group(self, p):
        return _L(ArrayLoc(array=_L(VarLoc(p.ID), p), index=p[1]), p)

    @_("factor")
    def group(self, p):
        return p.factor

    @_("'[' expr ']'")
    def index(self, p):
        return p.expr

    @_("ID")
    def factor(self, p):
        return _L(_L(VarLoc(p.ID), p), p)

    @_("INTEGER_LITERAL")
    def factor(self, p):
        return _L(Integer(p.INTEGER_LITERAL), p)

    @_("FLOAT_LITERAL")
    def factor(self, p):
        return _L(Float(p.FLOAT_LITERAL), p)

    @_("CHAR_LITERAL")
    def factor(self, p):
        return _L(Char(p.CHAR_LITERAL), p)

    @_("STRING_LITERAL")
    def factor(self, p):
        return _L(String(p.STRING_LITERAL), p)

    @_("TRUE")
    @_("FALSE")
    def factor(self, p):
        return _L(Boolean(p[0] == "true"), p)

    # Types
    @_("INTEGER")
    @_("FLOAT")
    @_("BOOLEAN")
    @_("CHAR")
    @_("STRING")
    @_("VOID")
    def type_simple(self, p):
        # return p[0]
        return _L(SimpleType(p[0].lower()), p)

    # @_("ARRAY '[' ']' type_simple")
    # @_("ARRAY '[' ']' type_array")
    # def type_array(self, p):
    #     ...

    @_("ARRAY index type_simple")
    def type_array_sized(self, p):
        return _L(ArrayType(base=p.type_simple, size=p[1]), p)

    @_("ARRAY index type_array_sized")
    def type_array_sized(self, p):
        return _L(ArrayType(base=p.type_array_sized, size=p[1]), p)

    @_("ARRAY '[' ']' type_simple")
    def type_array(self, p):
        return _L(ArrayType(base=p.type_simple), p)

    @_("ARRAY '[' ']' type_array")
    def type_array(self, p):
        return _L(ArrayType(base=p.type_array), p)

    @_("FUNCTION type_simple '(' opt_param_list ')'")
    @_("FUNCTION type_array '(' opt_param_list ')'")
    @_("FUNCTION type_array_sized '(' opt_param_list ')'")
    def type_func(self, p):
        return _L(FuncType(return_type=p[1], param_types=p.opt_param_list), p)

    @_("empty")
    def opt_param_list(self, p):
        return []

    @_("param_list")
    def opt_param_list(self, p):
        return p.param_list

    @_("param_list ',' param")
    def param_list(self, p):
        return p.param_list + [p.param]

    @_("param")
    def param_list(self, p):
        return [p.param]

    @_("ID ':' type_simple")
    def param(self, p):
        return _L(Param(name=p.ID, type=p.type_simple), p)

    @_("ID ':' type_array")
    def param(self, p):
        return _L(Param(name=p.ID, type=p.type_array), p)

    @_("ID ':' type_array_sized")
    def param(self, p):
        return _L(Param(name=p.ID, type=p.type_array_sized), p)

    @_("")
    def empty(self, p):
        return None

    def error(self, p):
        lineno = p.lineno if p else "EOF"
        value = repr(p.value) if p else "EOF"

        if p and not isinstance(p.value, str):
            error_type = ParserError.UNEXPECTED_TOKEN
            message = f"Syntax error: {error_type.value} near {value}"
            error(message, lineno, error_type)
            return
        elif not p or p is None:
            if lineno == "EOF":
                error_type = ParserError.UNEXPECTED_EOF
                message = f"Syntax error: {error_type.value}"
                error(message, lineno, error_type)
                return

            error_type = ParserError.SYNTAX_ERROR
            message = f"Syntax error: {error_type.value} at {value}"
            error(message, lineno, error_type)
            return

        from scanner import Lexer, TokenType

        # Clasificación de errores
        if p.value in "&|~":
            error_type = ParserError.UNSUPPORTED_OPERATOR
            message = f"{error_type.value} near {value}"
        elif p.value in [
            "&&",
            "==",
            "!=",
            "<=",
            ">=",
            "<",
            ">",
            "||",
            "+",
            "-",
            "*",
            "/",
            "%",
        ]:
            error_type = ParserError.MISSING_EXPRESSION
            message = f"{error_type.value} near {value}"
        elif repr(p.value) in ("'++'", "'--'"):
            error_type = ParserError.INVALID_INC_DEC
            message = f"{error_type.value} near {value}"
        elif p.value == "=":
            error_type = ParserError.INVALID_ASSIGNMENT
            message = f"{error_type.value} near {value}"
        elif p.value == "!":
            error_type = ParserError.INVALID_NOT
            message = f"{error_type.value} near {value}"
        elif p.value == "'":
            error_type = ParserError.MALFORMED_CHAR
            message = f"{error_type.value} near {value}"
        elif p.value == '"':
            error_type = ParserError.MALFORMED_STRING
            message = f"{error_type.value} near {value}"
        elif p.value == ":":
            error_type = ParserError.UNEXPECTED_COLON
            message = f"{error_type.value} near {value}"
        elif p.value == "[":
            error_type = ParserError.INVALID_ARRAY_SYNTAX
            message = f"{error_type.value} unexpected '[' near {value}"
        elif p.value == "]":
            error_type = ParserError.INVALID_ARRAY_SYNTAX
            message = f"{error_type.value} unexpected ']' near {value}"
        elif p.value == "{":
            error_type = ParserError.INVALID_STATEMENT
            message = f"{error_type.value} unexpected {value}"
        elif p.value == "}":
            error_type = ParserError.INVALID_STATEMENT
            message = f"{error_type.value} unexpected {value}"
        elif p.value == "(":
            error_type = ParserError.INCOMPLETE_FUNCTION_DECLARATION
            message = f"{error_type.value} unexpected '(' or expected list of parameters after {value}"
        elif p.value == ")":
            error_type = ParserError.MISSING_EXPRESSION
            message = f"{error_type.value}, unexpected ')' or expected list of parameters after {value}"
        elif p.value == ";":
            error_type = ParserError.MISSING_STATEMENT
            message = f"{error_type.value} near {value}"
        elif p.value in [t.lower() for t in Lexer.tokens]:
            error_type = ParserError.UNEXPECTED_TOKEN
            message = f"{error_type.value} near {value}"
        elif p.type == "ID":
            error_type = ParserError.UNEXPECTED_IDENTIFIER
            message = f"{error_type.value} near {value}"
        else:
            error_type = ParserError.SYNTAX_ERROR
            message = f"at {value}"

        message = f"Syntax error: {message} at line {lineno}"
        error(message, lineno, error_type)


def ast_to_dict(node):
    # Convertir el AST a una representación JSON para mejor visualización
    if isinstance(node, list):
        return [ast_to_dict(item) for item in node]
    elif hasattr(node, "__dict__"):
        return {key: ast_to_dict(value) for key, value in node.__dict__.items()}
    else:
        return node


def parse(txt):
    l = Lexer()
    p = Parser()

    return p.parse(l.tokenize(txt))


if __name__ == "__main__":
    import json
    import sys

    if sys.platform != "ios":

        if len(sys.argv) != 2:
            raise SystemExit("Usage: python parse.py <filename>")

        filename = sys.argv[1]

    else:
        from File_Picker import file_picker_dialog

        filename = file_picker_dialog(
            title="Seleccionar una archivo",
            root_dir="./test",
            file_pattern="^.*[.]bminor",
        )

    if filename:
        txt = open(filename, encoding="utf-8").read()
        ast = parse(txt)

        print(ast)
