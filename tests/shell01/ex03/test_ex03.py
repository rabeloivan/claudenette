import os
import shutil
import tempfile

from utils.ui import (
    print_exercise_result,
    print_test_fail,
    print_test_pass,
)

from ...shell_utils import run_sh


def _build_fixture(scratch):
    os.makedirs(os.path.join(scratch, "sub", "deeper"))
    os.makedirs(os.path.join(scratch, "empty_dir"))
    files = ["a.txt", "sub/b.txt", "sub/deeper/c.txt", "sub/deeper/d.txt"]
    for rel in files:
        with open(os.path.join(scratch, rel), "w") as f:
            f.write("x\n")
    # A symlink - the subject says "regular files and directories"
    # specifically, which excludes symlinks. A `find . | wc -l`-style
    # implementation (every directory entry, not just regular
    # files/dirs) would include this and over-count by one.
    os.symlink(os.path.join(scratch, "a.txt"), os.path.join(scratch, "link_to_a"))
    # "." itself + 3 dirs (sub, sub/deeper, empty_dir) + 4 files = 8
    # (the symlink above is deliberately excluded from this count)
    return 1 + 3 + len(files)


def run_shell01_ex03(student_file):
    abs_file = os.path.abspath(student_file)
    i = 0
    passed = 0

    def check(condition, description, expected=None, actual=None, show_value=None):
        nonlocal i, passed
        i += 1
        if condition:
            if show_value is not None:
                print_test_pass(i, f"{description} {show_value} as expected")
            else:
                print_test_pass(i, f"{description} as expected")
            passed += 1
        else:
            print_test_fail(
                i, f"{description} not as expected", expected=expected, actual=actual
            )

    scratch = tempfile.mkdtemp(prefix="claudenette_shell01_ex03_")
    try:
        expected_count = _build_fixture(scratch)

        actual, err, code = run_sh(abs_file, cwd=scratch)
        # .strip(), not just .rstrip("\n"): BSD wc (macOS) right-justifies
        # its count in a padded field ("       8"), unlike GNU wc (real 42
        # campus Linux) piped from a single stream, which prints the bare
        # number - confirmed by Ivan running the identical script on both.
        # The padding is a local-machine tool-formatting artifact having
        # nothing to do with whether the student's script is correct.
        actual_stripped = actual.strip()

        check(
            actual_stripped == str(expected_count),
            "count (every file/dir plus '.' itself)",
            expected=str(expected_count),
            actual=actual_stripped,
            show_value=actual_stripped,
        )
    finally:
        shutil.rmtree(scratch, ignore_errors=True)

    print_exercise_result(student_file, passed, i)
    return passed == i
