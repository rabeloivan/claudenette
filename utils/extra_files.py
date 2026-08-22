import fnmatch
import os

from rich.console import Console

from utils.ui import print_command_execution

console = Console()


def check_no_extra_files(directory, allowed):
    # allowed: exact filenames and/or glob patterns (e.g. "*.c"). Every
    # entry actually a subject's own "you must not leave any additional
    # files" rule (present in every C0X/rush/bsq/shell subject's own
    # Instructions chapter, and explicitly the *first* preliminary check
    # on bsq's real defense evaluation sheet, ahead of norm/compile) - this
    # was never enforced anywhere in the pipeline before.
    if not os.path.isdir(directory):
        return True

    entries = sorted(os.listdir(directory))
    allowed_display = ", ".join(allowed)
    print_command_execution(f"checking for extra files (allowed: {allowed_display})")

    extra = [
        name
        for name in entries
        if not any(fnmatch.fnmatch(name, pattern) for pattern in allowed)
    ]

    if extra:
        console.print("[deep_pink2]Error![/deep_pink2]")
        for name in extra:
            console.print(
                f"[deep_pink2]Error: unexpected file or directory: {name}[/deep_pink2]",
                highlight=False,
            )
        print()
        return False

    console.print("[sea_green2]OK![/sea_green2]")
    print()
    return True
