import fnmatch
import os

from rich.console import Console

from utils.ui import print_command_execution

console = Console()

_CHECKED = {}


def check_no_extra_files(directory, allowed, turn_in_files=None, recursive=False):
    # allowed: exact filenames and/or glob patterns (e.g. "*.c"). Every
    # entry actually a subject's own "you must not leave any additional
    # files" rule (present in every C0X/rush/bsq/shell subject's own
    # Instructions chapter, and explicitly the *first* preliminary check
    # on bsq's real defense evaluation sheet, ahead of norm/compile) - this
    # was never enforced anywhere in the pipeline before.
    if not os.path.isdir(directory):
        return True

    # Every Piscine key checks its own exercise directory, so each check is
    # distinct and prints once. libft's 45 keys all share the repository root
    # AND the same allowed list, which meant running - and printing - the
    # identical 9-entry check 45 times per run. Cached on (directory, allowed)
    # so it reports once and every later key reuses the verdict; the cache is
    # per-process, so a fresh run always re-checks. Recursive and shallow checks
    # are distinct: an accepted source directory can contain unexpected files.
    cache_key = (os.path.abspath(directory), tuple(allowed), recursive)
    if cache_key in _CHECKED:
        return _CHECKED[cache_key]

    if recursive:
        entries = []
        for current, dirs, files in os.walk(directory):
            entries.extend(os.path.relpath(os.path.join(current, name), directory)
                           for name in dirs + files)
            if os.path.abspath(current) == os.path.abspath(directory) and '.git' in allowed:
                dirs[:] = [name for name in dirs if name != '.git']
        entries.sort()
    else:
        entries = sorted(os.listdir(directory))
    label = 'turn-in' if turn_in_files is not None else 'allowed'
    allowed_display = ", ".join(turn_in_files if turn_in_files is not None else allowed)
    print_command_execution(f"checking for extra files ({label}: {allowed_display})")

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
        _CHECKED[cache_key] = False
        return False

    console.print("[sea_green2]OK![/sea_green2]")
    print()
    _CHECKED[cache_key] = True
    return True
