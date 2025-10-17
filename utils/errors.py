"""
Gestión de errores del compilador.

Una de las partes más importantes (y molestas) de escribir un compilador
es la notificación fiable de mensajes de error al usuario. Este archivo
debería consolidar algunas funciones básicas de gestión de errores en un solo lugar.
Facilitar la notificación de errores. Facilitar la detección de errores.

Podría ampliarse para que sea más potente posteriormente.

Variable global que indica si se ha producido algún error. El compilador puede
consultar esto posteriormente para decidir si debe detenerse.
"""

from rich import print


_errors_detected = 0
_errors = []


def error(message, lineno=None, error_type=None):
    global _errors_detected, _errors

    if error_type:
        _errors.append(error_type)
    if lineno:
        print(f"{lineno}: [red]{message}[/red]")
    else:
        print(f"[red]{message}[/red]")

    _errors_detected += 1


def errors_detected() -> int:
    return _errors_detected


def clear_errors() -> None:
    global _errors, _errors_detected
    _errors = []
    _errors_detected = 0


def get_errors() -> list:
    return _errors.copy()


def has_error(error_type) -> bool:
    return any([e == error_type for e in _errors])
