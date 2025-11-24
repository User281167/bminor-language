import codecs
import struct
from dataclasses import dataclass
from parser.model import SimpleType

from llvmlite import ir


@dataclass
class IrTypes:
    i32 = ir.IntType(32)
    f32 = ir.FloatType()
    i8 = ir.IntType(8)  # characters
    void = ir.VoidType()
    i1 = ir.IntType(1)

    # Puntero determinado por la arquitectura (Portable)
    # Tamaño del puntero según la arquitectura del sistema (32-bit o 64-bit)
    pointer_t = ir.IntType(struct.calcsize("P") * 8).as_pointer()

    # Generic pointer (i8* en LLVM,  void*)
    generic_pointer_t = i8.as_pointer()

    i32_zero = ir.Constant(i32, 0)
    f32_zero = ir.Constant(f32, 0.0)
    i8_zero = ir.Constant(i8, 0)
    i1_false = ir.Constant(i1, 0)
    null_pointer = ir.Constant(generic_pointer_t, None)

    @classmethod
    def get_type(cls, name: str | SimpleType) -> ir.Type:
        if isinstance(name, SimpleType):
            name = name.name

        types = {
            "integer": cls.i32,
            "float": cls.f32,
            "char": cls.i8,
            "string": cls.generic_pointer_t,
            "boolean": cls.i1,
            "void": cls.void,
            "pointer": cls.pointer_t,
            "array": cls.pointer_t,
        }

        return types[name]

    @classmethod
    def get_align(cls, t: str | SimpleType) -> int:
        if isinstance(t, SimpleType):
            name = t.name
        else:
            name = t

        arq = struct.calcsize("P")

        types = {
            "integer": 4,
            "float": 4,
            "char": 4,
            "boolean": 1,
            "string": arq,
            "array": arq,
            "pointer": arq,
            "void": 0,
        }

        return types[name]

    @classmethod
    def get_ptr_size(cls) -> int:
        return struct.calcsize("P")

    @classmethod
    def const_int(cls, value: int) -> ir.Constant:
        return ir.Constant(cls.i32, value)

    @classmethod
    def const_float(cls, value: float) -> ir.Constant:
        return ir.Constant(cls.f32, value)

    @classmethod
    def const_char(cls, value: str | int) -> ir.Constant:
        if isinstance(value, int):
            return ir.Constant(cls.i8, value)

        val = value
        decoded = codecs.decode(val, "unicode_escape")  # '\\n' -> '\n'
        ascii_val = ord(decoded)
        return ir.Constant(cls.i8, ascii_val)

    @classmethod
    def const_bool(cls, value: bool) -> ir.Constant:
        return ir.Constant(cls.i1, 1 if value else 0)

    @classmethod
    def const_pointer(cls, value: int) -> ir.Constant:
        return ir.Constant(cls.pointer_t, value)
