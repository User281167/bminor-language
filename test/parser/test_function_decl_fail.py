import unittest
from parser import Parser
from scanner import Lexer
from model import *
from errors import errors_detected, clear_errors


def save_json(ast, code=""):
    import json

    with open("ast.json", "w") as f:
        def ast_to_dict(node):
            if isinstance(node, list):
                return [ast_to_dict(item) for item in node]
            elif hasattr(node, "__dict__"):
                result = {
                    "_type": node.__class__.__name__  # ← Aquí agregas el nombre de clase
                }
                for key, value in node.__dict__.items():
                    result[key] = ast_to_dict(value)
                return result
            else:
                return node

        f.write(json.dumps({
            'code': code,
            'ast': ast_to_dict(ast)
        }, indent=2))


class TestFunctionDeclError(unittest.TestCase):
    def setUp(self):
        self.lexer = Lexer()
        self.parser = Parser()
        clear_errors()

    def parse(self, code):
        tokens = self.lexer.tokenize(code)
        return self.parser.parse(tokens)

    def test_fun_invalid_name(self):
        code = "123myFunc: function integer () = { }"
        self.parse(code)
        self.assertEqual(errors_detected(), 1)

    def test_fun_invalid_name_num(self):
        code = "123: function integer () = { }"
        self.parse(code)
        self.assertEqual(errors_detected(), 1)

    def test_fun_invalid_function_without_name(self):
        code = "function integer () = { }"
        self.parse(code)
        self.assertEqual(errors_detected(), 1)

    def test_fun_invalid_function_without_param_decl(self):
        code = "main: function integer = { }"
        self.parse(code)
        self.assertEqual(errors_detected(), 1)

    def test_fun_invalid_function_without_body(self):
        code = "main: function integer ()"
        self.parse(code)
        self.assertEqual(errors_detected(), 1)

    def test_fun_invalid_function_without_return_type(self):
        code = "main: function () = { }"
        self.parse(code)
        self.assertEqual(errors_detected(), 1)

    def test_fun_no_two_dots(self):
        code = "main function integer () = { }"
        self.parse(code)
        self.assertEqual(errors_detected(), 1)

    def test_fun_invalid_return_type(self):
        code = "main: function int () = { }"
        self.parse(code)
        self.assertEqual(errors_detected(), 1)
