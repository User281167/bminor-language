from llvmlite import ir


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

    def _declare_print_int(self):
        # Tipo de la función: void print_int(i32)
        f_type = ir.FunctionType(
            ir.VoidType(), [ir.IntType(32)]  # Tipo de retorno  # Argumentos
        )
        # Declarar la función en el módulo
        self._functions["print_int"] = ir.Function(
            self.module, f_type, name="print_int"
        )

    def _declare_print_float(self):
        # Tipo: void print_float(float)
        f_type = ir.FunctionType(ir.VoidType(), [ir.FloatType()])
        self._functions["print_float"] = ir.Function(
            self.module, f_type, name="print_float"
        )

    def _declare_print_char(self):
        # Tipo: void print_char(i8)
        f_type = ir.FunctionType(ir.VoidType(), [ir.IntType(8)])
        self._functions["print_char"] = ir.Function(
            self.module, f_type, name="print_char"
        )

    def _declare_print_bool(self):
        # Tipo: void print_bool(i1) -> C lo recibirá como i8
        f_type = ir.FunctionType(ir.VoidType(), [ir.IntType(1)])
        self._functions["print_bool"] = ir.Function(
            self.module, f_type, name="print_bool"
        )

    def get(self, func_name):
        return self._functions.get(func_name)

    def print_int(self):
        return self._functions["print_int"]

    def print_float(self):
        return self._functions["print_float"]

    def print_char(self):
        return self._functions["print_char"]

    def print_bool(self):
        return self._functions["print_bool"]
