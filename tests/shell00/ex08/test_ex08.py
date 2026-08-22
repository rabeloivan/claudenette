import os
import shutil
import tempfile

from utils.ui import print_exercise_result, print_test_fail, print_test_pass

from ...shell_utils import run_sh

MATCHING = ["foo~", "#bar#", "dir/nested~"]
NON_MATCHING = ["baz.txt", "#nomatch", "nomatch#", "keep~me.txt"]
# Directories (not files) whose own names match the ~ / #...# pattern -
# the subject says "searches for all files", so a `find` without
# `-type f` that also matches directories must leave these alone
# entirely: never displayed, never removed. Left empty specifically so
# an over-broad `-delete` would actually succeed in removing them - a
# non-empty directory would survive either way (rmdir fails on
# ENOTEMPTY), which wouldn't distinguish a correct implementation from
# a buggy one.
DIR_TRAPS = ["emptydir~", "#emptydir#"]


def _build_fixture(scratch):
    os.mkdir(os.path.join(scratch, "dir"))
    for name in MATCHING + NON_MATCHING:
        path = os.path.join(scratch, name)
        with open(path, "w") as f:
            f.write("x\n")
    for name in DIR_TRAPS:
        os.mkdir(os.path.join(scratch, name))


def run_shell00_ex08(student_file):
    abs_file = os.path.abspath(student_file)
    i = 0
    passed = 0

    def check(condition, description, expected=None, actual=None):
        nonlocal i, passed
        i += 1
        if condition:
            print_test_pass(i, f"{description} as expected")
            passed += 1
        else:
            print_test_fail(
                i, f"{description} not as expected", expected=expected, actual=actual
            )

    # "Only one command is allowed, no ';' or '&&' or other chaining
    # tricks" is a property of the submitted source text itself, not fully
    # observable from behavior - a correctly-behaving script chained with
    # `&&` would pass a purely functional test, so check the text directly.
    with open(student_file, "rb") as f:
        source = f.read().decode("latin-1")
    lines = [line for line in source.splitlines() if line.strip() and not line.strip().startswith("#")]
    check(
        len(lines) == 1, "exactly one non-comment command line", expected="1", actual=str(len(lines))
    )
    if lines:
        line = lines[0]
        check(";" not in line, "no ';' command separator")
        check("&&" not in line, "no '&&' chaining")
        check("||" not in line, "no '||' chaining")

    scratch = tempfile.mkdtemp(prefix="claudenette_shell00_ex08_")
    try:
        _build_fixture(scratch)
        actual, err, code = run_sh(abs_file, cwd=scratch)

        remaining = set()
        for root, dirs, files in os.walk(scratch):
            for name in files:
                remaining.add(os.path.relpath(os.path.join(root, name), scratch))

        for name in MATCHING:
            check(name not in remaining, f"'{name}' (matches ~ or #...#) was deleted")
            check(name in actual, f"'{name}' was displayed before deletion")
        for name in NON_MATCHING:
            check(name in remaining, f"'{name}' (does not match) was left alone")
        for name in DIR_TRAPS:
            check(
                os.path.isdir(os.path.join(scratch, name)),
                f"'{name}' (a directory, not a file) was left alone",
            )
            check(
                name not in actual, f"'{name}' (a directory) was not displayed as a match"
            )
    finally:
        shutil.rmtree(scratch, ignore_errors=True)

    print_exercise_result(student_file, passed, i)
    return passed == i
