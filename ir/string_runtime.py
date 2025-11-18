from llvmlite import ir


class StringRuntime:
    def __init__(self, module):
        self.module = module
        self._functions = {}

        # 1. Definir el tipo de la estructura BMinorString en LLVM IR
        # struct BMinorString {
        #   i32 length;
        #   i8* chars;
        # };
        self.bminor_string_type = ir.LiteralStructType(
            [ir.IntType(32), ir.IntType(8).as_pointer()]  # length  # chars
        )

        # 2. Declarar todas las funciones del runtime de strings
        self._declare_string_from_literal()
        self._declare_print_bminor_string()
        self._declare_string_concat()
        self._declare_string_copy()
        self._declare_string_free()

    def _declare_string_from_literal(self):
        # Tipo: BMinorString* _bminor_string_from_literal(i8*)
        f_type = ir.FunctionType(
            self.bminor_string_type.as_pointer(),  # Tipo de retorno: BMinorString*
            [ir.IntType(8).as_pointer()],  # Argumento: const char* (i8*)
        )
        self._functions["_bminor_string_from_literal"] = ir.Function(
            self.module, f_type, name="_bminor_string_from_literal"
        )

    def _declare_print_bminor_string(self):
        # Tipo: void print_bminor_string(BMinorString*)
        f_type = ir.FunctionType(
            ir.VoidType(),  # Tipo de retorno: void
            [self.bminor_string_type.as_pointer()],  # Argumento: const BMinorString*
        )
        self._functions["print_bminor_string"] = ir.Function(
            self.module, f_type, name="print_bminor_string"
        )

    def _declare_string_concat(self):
        # Tipo: BMinorString* _bminor_string_concat(BMinorString*, BMinorString*)
        f_type = ir.FunctionType(
            self.bminor_string_type.as_pointer(),  # Tipo de retorno: BMinorString*
            [  # Argumentos:
                self.bminor_string_type.as_pointer(),  # const BMinorString* s1
                self.bminor_string_type.as_pointer(),  # const BMinorString* s2
            ],
        )
        self._functions["_bminor_string_concat"] = ir.Function(
            self.module, f_type, name="_bminor_string_concat"
        )

    def _declare_string_copy(self):
        # Tipo: BMinorString* _bminor_string_copy(BMinorString*)
        f_type = ir.FunctionType(
            self.bminor_string_type.as_pointer(),  # Tipo de retorno: BMinorString*
            [
                self.bminor_string_type.as_pointer()
            ],  # Argumento: const BMinorString* source
        )
        self._functions["_bminor_string_copy"] = ir.Function(
            self.module, f_type, name="_bminor_string_copy"
        )

    def _declare_string_free(self):
        # Tipo: void _bminor_string_free(BMinorString*)
        f_type = ir.FunctionType(
            ir.VoidType(),  # Tipo de retorno: void
            [self.bminor_string_type.as_pointer()],  # Argumento: BMinorString*
        )
        self._functions["_bminor_string_free"] = ir.Function(
            self.module, f_type, name="_bminor_string_free"
        )

    # --- Métodos de acceso para el generador de código ---

    def get_string_type(self):
        """Devuelve el tipo ir.LiteralStructType para BMinorString."""
        return self.bminor_string_type

    def get_string_type_pointer(self):
        """Devuelve el tipo ir.LiteralStructType para BMinorString*."""
        return self.bminor_string_type.as_pointer()

    def from_literal(self):
        """Devuelve la función LLVM para crear un string desde un literal."""
        return self._functions["_bminor_string_from_literal"]

    def print(self):
        """Devuelve la función LLVM para imprimir un BMinorString."""
        return self._functions["print_bminor_string"]

    def concat(self):
        """Devuelve la función LLVM para concatenar dos BMinorStrings."""
        return self._functions["_bminor_string_concat"]

    def copy(self):
        """Devuelve la función LLVM para copiar un BMinorString."""
        return self._functions["_bminor_string_copy"]

    def free(self):
        """Devuelve la función LLVM para liberar la memoria de un BMinorString."""
        return self._functions["_bminor_string_free"]
