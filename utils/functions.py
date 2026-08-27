import os
import shutil
import subprocess
import tempfile

from rich.console import Console

from utils.ui import print_command_execution

console = Console()

# Symbols the compiler itself can inject (stack protector, struct/array
# copies, etc.) that aren't a "forbidden function" the student called.
#
# Note: these are matched against symbol names with ALL leading underscores
# already stripped (see the `.lstrip("_")` below) to stay consistent with
# both Mach-O's single leading `_` and other manglings — so entries here
# must be written without any leading underscore.
COMPILER_ARTIFACTS = {
    "memcpy",
    "memset",
    "memmove",
    "bzero",
    "stack_chk_fail",
    "stack_chk_guard",
    "stack_chk_fail_local",
    "chkstk_darwin",
    # Reading `errno` - with no call written in the student's source at all -
    # leaves an undefined symbol behind, because <errno.h> defines errno as a
    # macro that calls a per-thread accessor. The accessor differs per libc:
    # macOS uses `(*__error())`, glibc `(*__errno_location())`, musl
    # `(*__errno_location())` too. Several C10 exercises explicitly say "You
    # may use the variable errno", so none of these may ever be flagged.
    #
    # Names are matched with leading underscores stripped, hence the bare
    # spellings. Missing the glibc one made every errno-using exercise report
    # FORBIDDEN FN on Linux while passing on macOS - caught by running the
    # fixture sweep inside the Ubuntu image (tools/docker/), not on the host.
    "error",
    "errno_location",
    "errno",
}


def get_defined_functions(file_path, extra_flags=None):
    # Function names `file_path` defines with external linkage - used so a
    # multi-file exercise's cross-file helper calls (e.g. ft_convert_base.c
    # calling into ft_convert_base2.c) aren't mistaken for forbidden calls
    # when the caller is compiled alone and can't see the definition.
    if shutil.which("cc") is None or shutil.which("nm") is None:
        return set()

    obj_fd, obj_path = tempfile.mkstemp(suffix=".o")
    os.close(obj_fd)

    try:
        compile_result = subprocess.run(
            ["cc", "-x", "c"] + (extra_flags or []) + ["-c", file_path, "-o", obj_path],
            capture_output=True,
            text=True,
            timeout=5,
        )

        if compile_result.returncode != 0:
            return set()

        nm_result = subprocess.run(
            ["nm", obj_path], capture_output=True, text=True, timeout=5
        )

        defined = set()
        for line in nm_result.stdout.splitlines():
            parts = line.split()
            if len(parts) == 3 and parts[1] == "T":
                defined.add(parts[2].lstrip("_"))
        return defined

    except Exception:
        return set()

    finally:
        if os.path.exists(obj_path):
            os.remove(obj_path)


def check_allowed_functions(file_path, allowed, extra_flags=None):
    filename = os.path.basename(file_path)
    allowed_display = ", ".join(allowed) if allowed else "none"

    print_command_execution(
        f"nm -u {filename} (checking allowed functions: {allowed_display})"
    )

    if shutil.which("cc") is None or shutil.which("nm") is None:
        console.print("[yellow]cc/nm not found (skipping)[/yellow]")
        print()
        return True

    obj_fd, obj_path = tempfile.mkstemp(suffix=".o")
    os.close(obj_fd)

    try:
        # -x c forces C regardless of extension: a no-op for .c files, but
        # needed for a header-only exercise's .h file, since `cc -c foo.h`
        # doesn't reliably produce an object nm can parse. Forcing -x c also
        # means cc can't bail out early on a non-C name/extension the way
        # norminette does - it actually opens and reads the file's content,
        # which blocks forever if that content is a FIFO with no writer (a
        # real, valid solution technique for e.g. shell00's "make cat print
        # a fixed string" exercise) - so this specific subprocess call needs
        # its own timeout, independent of the outer except below.
        try:
            compile_result = subprocess.run(
                ["cc", "-x", "c"] + (extra_flags or []) + ["-c", file_path, "-o", obj_path],
                capture_output=True,
                text=True,
                timeout=5,
            )
        except subprocess.TimeoutExpired:
            return True

        if compile_result.returncode != 0:
            # The real compile step (with the harness) already reports this.
            return True

        nm_result = subprocess.run(
            ["nm", "-u", obj_path], capture_output=True, text=True, timeout=5
        )

        # GNU nm (Linux) prints undefined symbols as "<padding> U name", not
        # just the bare name the way macOS/LLVM nm's -u output does - taking
        # the last whitespace-separated token handles both (and is a no-op
        # for the bare-name case).
        used = set()
        for line in nm_result.stdout.splitlines():
            parts = line.split()
            if parts:
                used.add(parts[-1].lstrip("_"))

        sibling_defined = set()
        directory = os.path.dirname(file_path) or "."
        for entry in os.listdir(directory):
            if not entry.endswith(".c"):
                continue
            sibling_path = os.path.join(directory, entry)
            if os.path.abspath(sibling_path) == os.path.abspath(file_path):
                continue
            sibling_defined |= get_defined_functions(sibling_path)

        allowed_set = set(allowed) | COMPILER_ARTIFACTS | sibling_defined
        forbidden = sorted(used - allowed_set)

        if forbidden:
            console.print(f"[deep_pink2]{filename}: Error![/deep_pink2]")
            for fn in forbidden:
                console.print(
                    f"[deep_pink2]Error: forbidden function used: {fn}()"
                    f"[/deep_pink2]",
                    highlight=False,
                )
            print()
            return False

        console.print(f"[sea_green2]{filename}: OK![/sea_green2]")
        print()
        return True

    except Exception as e:
        console.print(f"[red]System Error: {e}[/red]")
        return True

    finally:
        if os.path.exists(obj_path):
            os.remove(obj_path)
