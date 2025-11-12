import platform
import subprocess
import tempfile
from pathlib import Path


def run_cmd(cmd, **kwargs):
    return subprocess.run(cmd, capture_output=True, text=True, check=True, **kwargs)


def run_llvm_ir(ir_code: str) -> str:
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        ir_path = tmpdir / "temp.ll"

        ir_path.write_text(ir_code)
        result = run_cmd(["lli", ir_path])

    return ""


def run_llvm_clang_ir(ir_code: str, add_runtime=False) -> str:
    """
    Compila y ejecuta código LLVM IR usando clang.

    Args:
    ir_code: str, código LLVM IR a compilar y ejecutar
    add_runtime: bool, agregar runtime en c de bminor como prints

    Return:
    str, la salida del programa
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        ir_path = tmpdir / "temp.ll"
        bc_path = tmpdir / "temp.bc"
        exe_path = tmpdir / "temp_exe"
        runtime_c = "ir" / Path("runtime.c")

        ir_path.write_text(ir_code)

        if add_runtime:
            if platform.system() == "Windows":
                runtime_obj = tmpdir / "runtime.obj"
                run_cmd(["clang", "-c", str(runtime_c), "-o", str(runtime_obj)])
            else:
                runtime_obj = tmpdir / "runtime.o"
                run_cmd(["clang", "-c", str(runtime_c), "-o", str(runtime_obj)])

        run_cmd(["llvm-as", str(ir_path), "-o", str(bc_path)])
        cmd = ["clang", str(bc_path), "-fuse-ld=lld", "-o", str(exe_path)]

        if add_runtime:
            cmd.append(str(runtime_obj))

        run_cmd(cmd)
        result = run_cmd([str(exe_path)])

        return result.stdout

    return ""


if __name__ == "__main__":
    ir = """
    declare i32 @printf(i8*, ...)

    @.str = private constant [19 x i8] c"Hola desde LLVMA\0A\00"

    define i32 @main() {
    entry:
    %ptr = getelementptr [19 x i8], [19 x i8]* @.str, i32 0, i32 0
    call i32 (i8*, ...) @printf(i8* %ptr)
    ret i32 0
    }
    """
    print(run_llvm_ir(ir))
    print(run_llvm_clang_ir(ir))
