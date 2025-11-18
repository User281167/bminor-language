import codecs
import struct
from dataclasses import dataclass
from parser.model import SimpleType

from llvmlite import ir

from .string_runtime import StringRuntime


@dataclass
class IrTypes:
    int32 = ir.IntType(32)
    float32 = ir.FloatType()
    char8 = ir.IntType(8)
    void = ir.VoidType()
    bool1 = ir.IntType(1)
    pointer = ir.PointerType(ir.IntType(struct.calcsize("P")))
    generic_pointer = ir.IntType(8).as_pointer()

    bminor_string_struct = ir.LiteralStructType(
        [ir.IntType(32), ir.IntType(8).as_pointer()]  # length  # chars
    )
    # 2. El TIPO de una VARIABLE string (un puntero a la estructura)
    bminor_string_pointer = bminor_string_struct.as_pointer()

    const_int32 = ir.Constant(int32, 0)
    const_float32 = ir.Constant(float32, 0.0)
    const_char8 = ir.Constant(char8, 0)
    const_bool1 = ir.Constant(bool1, 0)

    @classmethod
    def get_type(cls, name: str | SimpleType) -> ir.Type:
        if isinstance(name, SimpleType):
            name = name.name

        types = {
            "integer": cls.int32,
            "float": cls.float32,
            "char": cls.char8,
            "string": cls.bminor_string_pointer,
            "boolean": cls.bool1,
            "void": cls.void,
            "pointer": cls.pointer,
            "array": cls.pointer,
        }

        return types[name]

    @classmethod
    def get_align(cls, t: str | SimpleType) -> int:
        if isinstance(t, SimpleType):
            name = t.name
        else:
            name = t

        arq = struct.calcsize("P") * 8

        types = {
            "integer": 4,
            "float": 4,
            "char": 1,
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
        return ir.Constant(cls.int32, value)

    @classmethod
    def const_float(cls, value: float) -> ir.Constant:
        return ir.Constant(cls.float32, value)

    @classmethod
    def const_char(cls, value: str | int) -> ir.Constant:
        if isinstance(value, int):
            return ir.Constant(cls.char8, value)

        val = value
        decoded = codecs.decode(val, "unicode_escape")  # '\\n' -> '\n'
        ascii_val = ord(decoded)
        return ir.Constant(cls.char8, ascii_val)

    @classmethod
    def const_bool(cls, value: bool) -> ir.Constant:
        return ir.Constant(cls.bool1, 1 if value else 0)

    @classmethod
    def const_pointer(cls, value: int) -> ir.Constant:
        return ir.Constant(cls.pointer, value)
        return ir.Constant(cls.pointer, value)
