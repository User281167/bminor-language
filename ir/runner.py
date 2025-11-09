import subprocess
import tempfile
from pathlib import Path


def run_llvm_ir(ir_code: str, use_lli=True) -> str:
    def run_cmd(cmd, **kwargs):
        return subprocess.run(cmd, capture_output=True, text=True, check=True, **kwargs)

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        ir_path = tmpdir / "temp.ll"
        bc_path = tmpdir / "temp.bc"
        exe_path = tmpdir / "temp_exe"

        ir_path.write_text(ir_code)

        if use_lli:
            result = run_cmd(["lli", ir_path])
        else:
            run_cmd(["llvm-as", ir_path, "-o", bc_path])
            run_cmd(["clang", bc_path, "-fuse-ld=lld", "-o", exe_path])
            result = run_cmd([exe_path])

        return result.stdout.strip()

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
    print(run_llvm_ir(ir, use_lli=True))
    print(run_llvm_ir(ir, use_lli=False))
