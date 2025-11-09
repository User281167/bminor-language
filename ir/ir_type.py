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
    pointer = ir.PointerType(ir.IntType(8))
    array_type = ir.ArrayType(ir.IntType(8), 10)
    array_structure = ir.LiteralStructType([ir.IntType(8), ir.IntType(32)], True)

    @classmethod
    def get_type(cls, name: str | SimpleType) -> ir.Type:
        if isinstance(name, SimpleType):
            name = name.name

        types = {
            "integer": cls.int32,
            "float": cls.float32,
            "char": cls.char8,
            "string": cls.pointer,
            "void": cls.void,
            "boolean": cls.bool1,
            "pointer": cls.pointer,
            "array": cls.array_type,
        }

        return types[name]
