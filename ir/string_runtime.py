from llvmlite import ir

from .ir_type import IrTypes


class StringRuntime:
    def __init__(self, module):
        self.module = module
        self._functions = {}

        # Declarar todas las funciones del runtime de strings
        self._declare_string_concat()
        self._declare_string_copy()
        self._declare_string_free()

    def _declare_string_concat(self):
        # func(i8*, i8*) -> i8*

        f_type = ir.FunctionType(
            IrTypes.generic_pointer_t,
            [
                IrTypes.generic_pointer_t,
                IrTypes.generic_pointer_t,
            ],
        )
        self._functions["_bminor_string_concat"] = ir.Function(
            self.module, f_type, name="_bminor_string_concat"
        )

    def _declare_string_copy(self):
        # func(i8*) -> i8*
        f_type = ir.FunctionType(
            IrTypes.generic_pointer_t,
            [IrTypes.generic_pointer_t],
        )
        self._functions["_bminor_string_copy"] = ir.Function(
            self.module, f_type, name="_bminor_string_copy"
        )

    def _declare_string_free(self):
        # func(i8*) -> void
        f_type = ir.FunctionType(
            ir.VoidType(),  # Tipo de retorno: void
            [IrTypes.generic_pointer_t],  # Argumento: i8*
        )
        self._functions["_bminor_string_free"] = ir.Function(
            self.module, f_type, name="_bminor_string_free"
        )

    # --- Métodos de acceso para el generador de código ---

    def concat(self):
        """Devuelve la función LLVM para concatenar dos BMinorStrings."""
        return self._functions["_bminor_string_concat"]

    def copy(self):
        """Devuelve la función LLVM para copiar un BMinorString."""
        return self._functions["_bminor_string_copy"]

    def free(self):
        """Devuelve la función LLVM para liberar la memoria de un BMinorString."""
        return self._functions["_bminor_string_free"]
