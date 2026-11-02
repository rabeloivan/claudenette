import os
import subprocess

from rich.console import Console

from utils.ui import print_command_execution
from utils.reporting import current_group, record_problem

console = Console()

# Added to every harness build on top of the flags a test asks for (35 tests
# pass their own list), and left out of the printed command, which only
# summarises what the student would type.
#
# -fsigned-char: 42 grades on x86_64, where plain char is signed - as it is
# on macOS arm64. On arm64 Linux (Docker on Apple Silicon, ARM machines) char
# is unsigned, and a comparison through plain char such as
# `(int)(char)a[i] - (int)(char)b[i]` passes the 0x80-vs-0x01 case it fails
# on the real machines: two known-bad libft fixtures scored OK that way.
HARNESS_FLAGS = ["-fsigned-char"]

# -ftrivial-auto-var-init=pattern fills every uninitialised local with 0xAA
# bytes - the stack counterpart of free_tracker's poisoned malloc. Without
# it a local the student forgot to set usually held a lucky value: ft_atoi
# with `sign = 1;` deleted scored 20/20. Added only where the compiler knows
# the flag (clang, gcc >= 12; the Ubuntu 22.04 image's gcc 11 does not), so
# it is probed once. A variable whose correct start is non-zero - a flag
# meant to begin at 1 - can still pass by luck; catching those would take a
# second build with =zero, deliberately not paid for.
_STACK_INIT_FLAG = "-ftrivial-auto-var-init=pattern"
_stack_init_supported = []


def _harness_flags():
    if not _stack_init_supported:
        try:
            probe = subprocess.run(
                ["cc", _STACK_INIT_FLAG, "-x", "c", "-c", "-", "-o", os.devnull],
                input="int\tg_probe;\n",
                capture_output=True,
                text=True,
                timeout=30,
            )
            _stack_init_supported.append(probe.returncode == 0)
        except (OSError, subprocess.SubprocessError):
            _stack_init_supported.append(False)
    return HARNESS_FLAGS + ([_STACK_INIT_FLAG] if _stack_init_supported[0] else [])


def compile_source(source_files, output_name, flags=None):
    if flags is None:
        flags = ["-Wall", "-Wextra", "-Werror"]

    command = ["cc"] + flags + _harness_flags() + source_files + ["-o", output_name]
    student_file = os.path.basename(source_files[0])
    flags_str = " ".join(flags)
    # The displayed command is a readable summary, not a reproduction - it
    # already names only the first source, omitting the harness and any
    # reference objects. An output path is shortened to its basename only when
    # it is absolute: the Piscine modules build into the cwd and "-o ./strlen"
    # says something useful about where the artefact lands, while libft builds
    # into a temp directory whose /var/folders/... path is pure noise.
    display_output = (
        os.path.basename(output_name) if os.path.isabs(output_name) else output_name
    )
    display_cmd = f"cc {flags_str} {student_file} -o {display_output}"

    group = current_group()
    announce = group is None or group.compilations == 0
    if group is not None:
        group.compilations += 1
    if announce:
        print_command_execution(display_cmd)

    try:
        result = subprocess.run(command, capture_output=True, text=True)

        if result.returncode != 0:
            if not announce:
                console.print("[deep_pink2]Compilation failed for additional checks:[/deep_pink2]")
            console.print("[deep_pink2]cc: ERROR[/deep_pink2]")
            clean_err = result.stderr.replace(source_files[0], student_file)
            record_problem('compile', clean_err.strip() or 'Compiler exited without a diagnostic.')
            console.print(clean_err.strip(), style='deep_pink2', markup=False, highlight=False)
            print()
            return False
        else:
            if announce:
                console.print("[sea_green2]cc: OK![/sea_green2]")
                print()
            return True

    except Exception as e:
        record_problem('compile', f'Could not run the compiler: {e}')
        console.print(f"[red]System Error: {e}[/red]")
        return False
