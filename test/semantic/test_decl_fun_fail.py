import unittest
from parser import Parser
from parser.model import *

from scanner import Lexer
from semantic.checker import Check, SemanticError
from utils import clear_errors, error, errors_detected, has_error


class TestFunctionDeclarationErrors(unittest.TestCase):
    def setUp(self):
        self.lexer = Lexer()
        self.parser = Parser()
        clear_errors()

    def semantic(self, code):
        tokens = self.lexer.tokenize(code)
        ast = self.parser.parse(tokens)
        return Check.checker(ast)

    def assertSemanticError(self, code, error_type):
        self.semantic(code)
        self.assertTrue(errors_detected())
        self.assertTrue(has_error(error_type))

    # ❌ Void como parámetro
    def test_void_parameter(self):
        code = "main: function void(a: void);"
        self.assertSemanticError(code, SemanticError.VOID_PARAMETER)

    # ❌ Array multidimensional como parámetro
    def test_multidimensional_array_param(self):
        code = "main: function void(a: array [] array [] integer);"
        self.assertSemanticError(code, SemanticError.MULTI_DIMENSIONAL_ARRAYS)

    # ❌ Array multidimensional como retorno
    def test_multidimensional_array_return(self):
        code = "main: function array [] array [] integer();"
        self.assertSemanticError(code, SemanticError.MULTI_DIMENSIONAL_ARRAYS)

    # ❌ Array con tamaño y multidimensional
    def test_array_param_with_size_and_nested(self):
        # code = "main: function void(a: array [3] array [] integer);" -> SyntaxError ya que debe tener expr en ambos indices
        code = "main: function void(a: array [3] array [2] integer);"
        self.assertSemanticError(code, SemanticError.MULTI_DIMENSIONAL_ARRAYS)

    # ❌ Void como retorno con parámetros válidos
    def test_void_param_and_array_return(self):
        code = "main: function array [] integer(a: void);"
        self.assertSemanticError(code, SemanticError.VOID_PARAMETER)

    # ❌ Array multidimensional como parámetro y retorno
    def test_array_nested_param_and_return(self):
        code = "main: function array [] array [] integer(a: array [] array [] integer);"
        self.assertSemanticError(code, SemanticError.MULTI_DIMENSIONAL_ARRAYS)

    def test_array_size_with_var(self):
        code = "x: integer; main: function void(a: array [x] integer);"
        self.assertSemanticError(code, SemanticError.ARRAY_SIZE_MUST_BE_INTEGER)

    def test_redeclaretion_type_error(self):
        code = "main: function void(a: integer); main: function integer(a: integer);"
        self.assertSemanticError(code, SemanticError.REDEFINE_FUNCTION_TYPE)

    def test_redeclaretion_type_args(self):
        code = "main: function void(a: integer); main: function void(a: string);"
        self.assertSemanticError(code, SemanticError.REDEFINE_FUNCTION)
