from llvmlite import ir


class MathRuntime:
    def __init__(self, module):
        self.module = module
        # Diccionario para guardar las funciones declaradas
        self._functions = {}

        # Declarar todas las funciones que necesitamos
        self._declare_pow_int()

    def _declare_pow_int(self):
        # Tipo de la función: void print_int(i32)
        f_type = ir.FunctionType(
            ir.IntType(32),
            [ir.IntType(32), ir.IntType(32)],  # Argumentos
        )

        # Declarar la función en el módulo
        self._functions["pow_int"] = ir.Function(self.module, f_type, name="pow_int")

    def get(self, func_name):
        return self._functions.get(func_name)

    def pow_int(self):
        return self._functions["pow_int"]
