import struct
from dataclasses import dataclass
from parser.model import SimpleType

from llvmlite import ir


@dataclass
class IrTypes:
    int32 = ir.IntType(32)
    float32 = ir.FloatType()
    char8 = ir.IntType(8)
    void = ir.VoidType()
    bool1 = ir.IntType(1)
    pointer = ir.PointerType(ir.IntType(struct.calcsize("P")))

    @classmethod
    def get_type(cls, name: str | SimpleType) -> ir.Type:
        if isinstance(name, SimpleType):
            name = name.name

        types = {
            "integer": cls.int32,
            "float": cls.float32,
            "char": cls.char8,
            "string": cls.pointer,
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
