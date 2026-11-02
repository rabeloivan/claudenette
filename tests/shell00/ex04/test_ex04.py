import os
import shutil
import tempfile

from utils.ui import (
    display_str,
    print_exercise_result,
    print_test_fail,
    print_test_pass,
)

from ...shell_utils import run_sh


def _build_fixture(scratch):
    # A mix of dotfiles (must be excluded) and non-dotfiles, with distinct,
    # explicitly-set mtimes (10s apart - well outside filesystem mtime
    # granularity) so sort order is unambiguous.
    entries = [
        ("oldest.txt", "file"),
        ("adir", "dir"),
        (".hidden", "file"),
        ("newer.txt", "file"),
        ("bdir", "dir"),
        ("newest.txt", "file"),
    ]
    base = 1_700_000_000
    for offset, (name, kind) in enumerate(entries):
        path = os.path.join(scratch, name)
        if kind == "dir":
            os.mkdir(path)
        else:
            open(path, "w").close()
        t = base + offset * 10
        os.utime(path, (t, t))
    return entries


def _expected_midls(scratch, entries):
    # Newest-first, matching bare `ls -t` semantics - the subject says only
    # "sorted by modification date" with no explicit direction, so this is
    # a judgment call (documented here, not silently assumed) rather than
    # something the subject pins down exactly.
    visible = [(name, kind) for name, kind in entries if not name.startswith(".")]
    visible.sort(key=lambda e: os.path.getmtime(os.path.join(scratch, e[0])), reverse=True)
    return ", ".join(name + "/" if kind == "dir" else name for name, kind in visible)


def run_shell00_ex04(student_file):
    # main.py passes the mapping key as-is (relative to wherever it was
    # launched from) - once run_sh below switches the subprocess's cwd to
    # the fixture dir, that relative path would resolve against the wrong
    # directory unless resolved to absolute first. Kept separate from
    # student_file itself, which print_exercise_result below still needs
    # in its original relative form for a short "exNN/name" label.
    abs_file = os.path.abspath(student_file)
    i = 0
    passed = 0

    def check(condition, description, expected=None, actual=None, show_value=None):
        nonlocal i, passed
        i += 1
        if condition:
            if show_value is not None:
                print_test_pass(i, f"{description} {display_str(show_value)} as expected")
            else:
                print_test_pass(i, f"{description} as expected")
            passed += 1
        else:
            print_test_fail(
                i, f"{description} not as expected", expected=expected, actual=actual
            )

    scratch = tempfile.mkdtemp(prefix="claudenette_shell00_ex04_")
    try:
        entries = _build_fixture(scratch)
        expected = _expected_midls(scratch, entries)

        actual, err, code = run_sh(abs_file, cwd=scratch)
        actual_stripped = actual.rstrip("\n")
        check(
            actual_stripped == expected,
            "output (mtime-sorted, dotfile-excluded listing)",
            expected=expected,
            actual=actual_stripped,
            show_value=actual_stripped,
        )
    finally:
        shutil.rmtree(scratch, ignore_errors=True)

    print_exercise_result(student_file, passed, i)
    return passed == i
