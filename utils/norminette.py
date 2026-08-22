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


def check_norminette(file_path, extra_rules=None):
    filename = os.path.basename(file_path)

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
        try:
            result = subprocess.run(cmd_list, capture_output=True, text=True, timeout=5)
        except subprocess.TimeoutExpired:
            console.print("[yellow]Norminette timed out on this file (skipping)[/yellow]")
            print()
            return True

        if result.returncode != 0 and "No module named norminette" in result.stderr:
            raise Exception("Norminette module not found")

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

    except Exception:
        console.print("[yellow]Norminette not found (skipping)[/yellow]")
        print()
        return True
