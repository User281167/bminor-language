from llvmlite import ir

from .ir_type import IrTypes


class PrintRuntime:
    def __init__(self, module):
        self.module = module
        # Diccionario para guardar las funciones declaradas
        self._functions = {}

        # Declarar todas las funciones que necesitamos
        self._declare_print_int()
        self._declare_print_float()
        self._declare_print_char()
        self._declare_print_bool()
        self._declare_print_string()

    def _declare_print_int(self):
        # Tipo de la función: void print_int(i32)
        f_type = ir.FunctionType(
            ir.VoidType(), [IrTypes.i32]  # Tipo de retorno  # Argumentos
        )
        # Declarar la función en el módulo
        self._functions["print_int"] = ir.Function(
            self.module, f_type, name="_bminor_print_int"
        )

    def _declare_print_float(self):
        # Tipo: void print_float(float)
        f_type = ir.FunctionType(ir.VoidType(), [IrTypes.f32])
        self._functions["print_float"] = ir.Function(
            self.module, f_type, name="_bminor_print_float"
        )

    def _declare_print_char(self):
        # Tipo: void print_char(i8)
        f_type = ir.FunctionType(ir.VoidType(), [IrTypes.i8])
        self._functions["print_char"] = ir.Function(
            self.module, f_type, name="_bminor_print_char"
        )

    def _declare_print_bool(self):
        # Tipo: void print_bool(i1) -> C lo recibirá como i8
        f_type = ir.FunctionType(ir.VoidType(), [IrTypes.i1])
        self._functions["print_bool"] = ir.Function(
            self.module, f_type, name="_bminor_print_bool"
        )

    def _declare_print_string(self):
        # Tipo: void print_string(i8*)
        f_type = ir.FunctionType(ir.VoidType(), [IrTypes.generic_pointer_t])
        self._functions["print_string"] = ir.Function(
            self.module, f_type, name="_bminor_print_string"
        )

    def get(self, func_name):
        return self._functions.get(func_name)

    def print_int(self):
        return self._functions["print_int"]

    def print_float(self):
        return self._functions["print_float"]

    def print_char(self):
        return self._functions["print_char"]

    def print_string(self):
        return self._functions["print_string"]

    def print_bool(self):
        return self._functions["print_bool"]
