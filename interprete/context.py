from parser.model import Node

from utils import error


class Context:
    def __init__(self, source_code: str):
        self.source_code = source_code
        self.have_errors = False
        self.errors = []

    def error(self, position: Node, message: str):
        """
        Registra un error usando la posición (nodo AST) y un mensaje.
        """
        self.have_errors = True
        lineno = getattr(position, "lineno", "N/A")
        error(message=message, lineno=lineno, error_type="InterpreterError")
        self.errors.append(f"[Error en Línea {lineno}]: {message}")
        self.have_errors = True

    # Método para encontrar la fuente del error (el texto original)
    def find_source(self, position: Node) -> str:
        """
        Intenta encontrar la porción de texto del código fuente
        que corresponde al nodo AST (posición).
        """
        # Esta es la parte más compleja. Para simplificar,
        # asumiremos que los nodos tienen un atributo 'value' o 'name'.

        # En el ejemplo de FuncCall:
        # f"{self.ctxt.find_source(node.func)!r}"
        # busca el nombre de la función que no es invocable.

        if hasattr(position, "name"):
            return position.name
        elif hasattr(position, "value"):
            return position.value
        else:
            # Si no podemos encontrar la fuente específica, devolvemos una cadena vacía
            return "<?objeto?>"

    # Método para mostrar todos los errores (opcional, pero útil)
    def report_errors(self):
        """Imprime todos los errores recolectados."""
        if self.have_errors:
            print("\n--- Errores del Compilador/Intérprete ---")
            for e in self.errors:
                print(e)
            print("---------------------------------------")
            print("---------------------------------------")
            print("---------------------------------------")
            print("---------------------------------------")
