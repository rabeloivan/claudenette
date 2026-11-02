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
    # The GOT itself, not a function. Under gcc's default PIE on x86_64,
    # taking the address of a function defined in another file - C11 ex05's
    # `ops[0] = op_add;`, the whole point of a function-pointer day - loads
    # it through the GOT (op_add@GOTPCREL), and the assembler then lists
    # _GLOBAL_OFFSET_TABLE_ as undefined. do-op solutions built that way
    # were FORBIDDEN FN on Linux only; the audit's amd64 logs already had
    # it, masked by the NORM ERR its Makefile key reported then.
    "GLOBAL_OFFSET_TABLE_",
}

# A list of the functions called that could not be made is not an empty one:
# a timeout or an unexpected error fails the check, saying so, where it used
# to print "System Error" and pass - a hung nm scored OK and PASSED. As with
# norminette's, the limit is generous because a spurious timeout is now a
# false FORBIDDEN FN rather than a false pass.
CHECK_TIMEOUT = 30


def _could_not_check(filename, reason):
    console.print(f"[deep_pink2]{filename}: Error![/deep_pink2]")
    console.print(
        f"[deep_pink2]the functions this file calls could not be listed "
        f"({reason}), so none is assumed allowed[/deep_pink2]",
        highlight=False,
    )
    print()
    return False


# A libc header can redirect a standard function to an internal symbol, so the
# name nm reports is not the name the student wrote. glibc's <libgen.h> - the
# header basename(3) names - does `#define basename __xpg_basename` (POSIX's
# version, as opposed to the GNU one in <string.h>), so a call to basename,
# allowed outright by C10 ex01-ex03, left `xpg_basename` once stripped and was
# reported as a forbidden function on Linux, where 42 grades, while macOS's
# plain `_basename` passed. Mapped back before the allowed-list comparison, so
# the call is judged as the function actually called. Keys and values are
# written without leading underscores, like COMPILER_ARTIFACTS.
SYMBOL_ALIASES = {
    "xpg_basename": "basename",
}


# get_defined_functions() compiles the file it is given, and the sibling scan
# below calls it once per sibling per graded key. That is quadratic in the
# number of .c files sharing a directory: fine for a Piscine exercise
# directory holding one or two, but libft turns in 43 flat files at the
# repository root, which without this cache is ~1,850 compilations for a
# single run. Keyed on (path, mtime, flags) so an edited file is re-read.
_DEFINED_CACHE = {}


def get_defined_functions(file_path, extra_flags=None):
    # Function names `file_path` defines with external linkage - used so a
    # multi-file exercise's cross-file helper calls (e.g. ft_convert_base.c
    # calling into ft_convert_base2.c) aren't mistaken for forbidden calls
    # when the caller is compiled alone and can't see the definition.
    if shutil.which("cc") is None or shutil.which("nm") is None:
        return set()

    try:
        cache_key = (
            os.path.abspath(file_path),
            os.path.getmtime(file_path),
            tuple(extra_flags or ()),
        )
    except OSError:
        cache_key = None
    if cache_key is not None and cache_key in _DEFINED_CACHE:
        return _DEFINED_CACHE[cache_key]

    defined = _defined_functions_uncached(file_path, extra_flags)
    if cache_key is not None:
        _DEFINED_CACHE[cache_key] = defined
    return defined


def _defined_functions_uncached(file_path, extra_flags=None):
    obj_fd, obj_path = tempfile.mkstemp(suffix=".o")
    os.close(obj_fd)

    try:
        compile_result = subprocess.run(
            ["cc", "-x", "c"] + (extra_flags or []) + ["-c", file_path, "-o", obj_path],
            capture_output=True,
            text=True,
            timeout=CHECK_TIMEOUT,
        )

        if compile_result.returncode != 0:
            return set()

        nm_result = subprocess.run(
            ["nm", obj_path], capture_output=True, text=True, timeout=CHECK_TIMEOUT
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


def check_allowed_functions(file_path, allowed, extra_flags=None, strict_symbols=None):
    # strict_symbols: names to check even though they appear in
    # COMPILER_ARTIFACTS. That exclusion list exists because the compiler can
    # emit calls to memcpy/memset/memmove/bzero that the student never wrote -
    # true for every Piscine exercise, where those are libc functions nobody
    # is asked to implement. libft asks for exactly those four as mandatory
    # deliverables, so there the blanket exclusion hides the one thing the
    # check is for: an ft_memset whose body is `return (memset(s, c, n));`
    # would pass silently. Safe to re-enable per exercise because claudenette
    # compiles at -O0, where the loop-idiom recognition that would synthesise
    # such a call from a hand-written byte loop is off.
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
        # its own timeout, independent of the outer except below. (Such a file
        # no longer gets here: main.py checks only .c/.h and directory keys,
        # and the shell modules skip this check altogether.)
        try:
            compile_result = subprocess.run(
                ["cc", "-x", "c"] + (extra_flags or []) + ["-c", file_path, "-o", obj_path],
                capture_output=True,
                text=True,
                timeout=CHECK_TIMEOUT,
            )
        except subprocess.TimeoutExpired:
            return _could_not_check(filename, f"cc gave no answer within {CHECK_TIMEOUT}s")

        if compile_result.returncode != 0:
            # The real compile step (with the harness) already reports this.
            return True

        try:
            nm_result = subprocess.run(
                ["nm", "-u", obj_path],
                capture_output=True,
                text=True,
                timeout=CHECK_TIMEOUT,
            )
        except subprocess.TimeoutExpired:
            return _could_not_check(filename, f"nm gave no answer within {CHECK_TIMEOUT}s")
        if nm_result.returncode != 0:
            return _could_not_check(
                filename, f"nm failed: {nm_result.stderr.strip() or nm_result.returncode}"
            )

        # GNU nm (Linux) prints undefined symbols as "<padding> U name", not
        # just the bare name the way macOS/LLVM nm's -u output does - taking
        # the last whitespace-separated token handles both (and is a no-op
        # for the bare-name case).
        used = set()
        for line in nm_result.stdout.splitlines():
            parts = line.split()
            if parts:
                name = parts[-1].lstrip("_")
                used.add(SYMBOL_ALIASES.get(name, name))

        sibling_defined = set()
        directory = os.path.dirname(file_path) or "."
        for entry in os.listdir(directory):
            if not entry.endswith(".c"):
                continue
            sibling_path = os.path.join(directory, entry)
            if os.path.abspath(sibling_path) == os.path.abspath(file_path):
                continue
            sibling_defined |= get_defined_functions(sibling_path)

        artifacts = COMPILER_ARTIFACTS - set(strict_symbols or ())
        allowed_set = set(allowed) | artifacts | sibling_defined
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
        return _could_not_check(filename, f"{type(e).__name__}: {e}")

    finally:
        if os.path.exists(obj_path):
            os.remove(obj_path)
