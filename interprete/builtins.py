# Helper para funciones integradas simples
class BuiltinFunction:
    def __init__(self, name, arity, func):
        self.name = name
        self._arity = arity
        self._func = func

    @property
    def arity(self) -> int:
        # Aridad (número de argumentos esperados).
        return self._arity

    def __call__(self, interp, *args):
        # El intérprete ('interp') se pasa como primer argumento por convención
        # si la función necesita acceder al estado del intérprete (como ctxt para errores).
        return self._func(*args)


class CallError(Exception):
    def __init__(self, message):
        self.message = message


def get_array_length(array):
    if not isinstance(array, list):
        raise CallError("Se esperaba un array como argumento.")

    return len(array)


builtins = {
    "array_length": BuiltinFunction("array_length", 1, get_array_length),
}

consts = {}
