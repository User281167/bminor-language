from llvmlite import ir

from .ir_type import IrTypes


class ArrayRuntime:
    def __init__(self, module):
        self.module = module
        self._functions = {}

        # Declarar todas las funciones del runtime de strings
        self._declare_array_new()
        self._declare_array_free()
        self._declare_array_size()
        self._declare_array_set()
        self._declare_array_set_sting()
        self._declare_array_get()

    def _declare_array_new(self):
        # func(i32, i32, i32) -> i8*
        f_type = ir.FunctionType(
            IrTypes.generic_pointer_t,  # Tipo de retorno: i8*
            [IrTypes.i32, IrTypes.i32, IrTypes.i32],  # Argumento: i32
        )
        self._functions["_bminor_array_new"] = ir.Function(
            self.module, f_type, name="_bminor_array_new"
        )

    def _declare_array_free(self):
        # func(i8*) -> void
        f_type = ir.FunctionType(
            ir.VoidType(),  # Tipo de retorno: void
            [IrTypes.generic_pointer_t],  # Argumento: i8*
        )
        self._functions["_bminor_array_free"] = ir.Function(
            self.module, f_type, name="_bminor_array_free"
        )

    def _declare_array_size(self):
        # func(i8*) -> i32
        f_type = ir.FunctionType(
            IrTypes.i32,  # Tipo de retorno: i32
            [IrTypes.generic_pointer_t],  # Argumento: i8*
        )
        self._functions["_bminor_array_size"] = ir.Function(
            self.module, f_type, name="_bminor_array_size"
        )

    def _declare_runtime_error(self):
        f_type = ir.FunctionType(
            ir.VoidType(),  # Retorna void
            [IrTypes.generic_pointer_t],  # Argumento: i8* (puntero al mensaje)
        )
        self._functions["_bminor_runtime_error"] = ir.Function(
            self.module, f_type, name="_bminor_runtime_error"
        )

    def _declare_array_set(self):
        # func(i8*, i32, i8*) -> void
        f_type = ir.FunctionType(
            ir.VoidType(),  # Tipo de retorno: void
            [
                IrTypes.generic_pointer_t,
                IrTypes.i32,
                IrTypes.generic_pointer_t,
            ],
        )
        self._functions["_bminor_array_set"] = ir.Function(
            self.module, f_type, name="_bminor_array_set"
        )

    def _declare_array_set_sting(self):
        # func(i8*, i32, i8*) -> void
        f_type = ir.FunctionType(
            ir.VoidType(),  # Tipo de retorno: void
            [
                IrTypes.generic_pointer_t,
                IrTypes.i32,
                IrTypes.generic_pointer_t,
            ],
        )
        self._functions["_bminor_array_set_string"] = ir.Function(
            self.module, f_type, name="_bminor_array_set_string"
        )

    def _declare_array_get(self):
        # func(i8*, i32, i8*) -> void
        f_type = ir.FunctionType(
            IrTypes.void,
            [
                IrTypes.generic_pointer_t,
                IrTypes.i32,
                IrTypes.generic_pointer_t,
            ],
        )
        self._functions["_bminor_array_get"] = ir.Function(
            self.module, f_type, name="_bminor_array_get"
        )

    # --- Métodos de acceso para el generador de código ---

    def free(self):
        return self._functions["_bminor_array_free"]

    def size(self):
        return self._functions["_bminor_array_size"]

    def new(self):
        return self._functions["_bminor_array_new"]

    def runtime_error(self):
        return self._functions["_bminor_runtime_error"]

    def set(self):
        return self._functions["_bminor_array_set"]

    def set_string(self):
        return self._functions["_bminor_array_set_string"]

    def get(self):
        return self._functions["_bminor_array_get"]
