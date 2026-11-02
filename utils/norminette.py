import os
import re
import shutil
import subprocess
import sys

from rich.console import Console

from utils.ui import print_command_execution

console = Console()


def strip_ansi(text):
    ansi_escape = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")
    return ansi_escape.sub("", text)


# A norm that could not be checked is not a norm that passed: a timeout or an
# unexpected error fails the file, saying so, where it used to print a yellow
# "skipping" and pass it - a hung norminette scored OK and PASSED. The limit
# is generous because failing closed makes a spurious timeout a false
# NORM ERR: norminette takes well under a second per file natively, but
# several times that under the Docker image's amd64 emulation, running four
# mutants at once. Only an absent norminette still skips - see the end of
# _run_norminette.
NORMINETTE_TIMEOUT = 30


def _could_not_check(filename, reason):
    console.print(f"[deep_pink2]{filename}: Error![/deep_pink2]")
    console.print(
        f"[deep_pink2]norminette could not check this file ({reason}), so it is "
        "not assumed to pass[/deep_pink2]",
        highlight=False,
    )
    print()
    return False


# One verdict per file and rule set per run. Every Piscine key has a
# directory of its own, but libft's 45 keys share one, so a header turned in
# there (main.turned_in_headers) would otherwise be re-checked, and its result
# re-printed, once per key. Keyed on mtime so an edited file is re-read.
_CHECKED = {}


def check_norminette(file_path, extra_rules=None):
    try:
        cache_key = (
            os.path.abspath(file_path),
            os.path.getmtime(file_path),
            tuple(extra_rules or ()),
        )
    except OSError:
        cache_key = None
    if cache_key is not None and cache_key in _CHECKED:
        return _CHECKED[cache_key]
    verdict = _run_norminette(file_path, extra_rules)
    if cache_key is not None:
        _CHECKED[cache_key] = verdict
    return verdict


def _run_norminette(file_path, extra_rules=None):
    filename = os.path.basename(file_path)

    # norminette only checks C: on any other file it prints "is not valid C
    # or C header file", and whether it then exits 0 (3.3.59) or 1 (3.3.60)
    # depends on the version installed. main.py no longer passes such files,
    # so this is a backstop - a file with no norm has none to break.
    if os.path.isfile(file_path) and not file_path.endswith((".c", ".h")):
        return True

    rule_args = []
    for rule in ["CheckForbiddenSourceHeader"] + list(extra_rules or []):
        rule_args += ["-R", rule]
    rule_display = " ".join(rule_args)

    if shutil.which("norminette") is not None:
        cmd_list = ["norminette"] + rule_args + [file_path]
        display_cmd = f"norminette {rule_display} {filename}"
    else:
        cmd_list = [sys.executable, "-m", "norminette"] + rule_args + [file_path]
        display_cmd = f"python -m norminette {rule_display} {filename}"

    print_command_execution(display_cmd)

    try:
        result = subprocess.run(
            cmd_list, capture_output=True, text=True, timeout=NORMINETTE_TIMEOUT
        )
    except subprocess.TimeoutExpired:
        return _could_not_check(filename, f"no answer within {NORMINETTE_TIMEOUT}s")
    except OSError as e:
        return _could_not_check(filename, str(e))

    # Absent altogether: preflight() refuses such a run before any file is
    # checked, unless --skip-norm was given - and then the norm checks that
    # tests run themselves (C10's check_all_c_files, rush02's sources) must
    # skip too, which is what this is for.
    if result.returncode != 0 and "No module named norminette" in result.stderr:
        console.print("[yellow]Norminette not found (skipping)[/yellow]")
        print()
        return True

    try:
        raw_output = result.stdout.strip()
        clean_output = strip_ansi(raw_output)

        if "Error!" in clean_output or result.returncode != 0:
            console.print(f"[deep_pink2]{filename}: Error![/deep_pink2]")
            lines = clean_output.split("\n")

            for line in lines:
                if "Error:" in line:
                    clean_line = line.replace(file_path, filename).strip()
                    console.print(
                        f"[deep_pink2]{clean_line}[/deep_pink2]", highlight=False
                    )

            print()
            return False
        else:
            console.print(f"[sea_green2]{filename}: OK![/sea_green2]")
            print()
            return True

    except Exception as e:
        return _could_not_check(filename, f"{type(e).__name__}: {e}")
