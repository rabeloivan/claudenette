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
    sh_files = ["find_sh.sh", "file1.sh", "sub/file2.sh", "sub/deeper/file3.sh"]
    non_sh_files = ["readme.txt", "sub/notme.c", "notashell.shx"]
    for rel in sh_files + non_sh_files:
        with open(os.path.join(scratch, rel), "w") as f:
            f.write("x\n")
    # A directory (not a file) whose own name ends in .sh - the subject
    # says "searches for all files ending with .sh", so a `find` without
    # `-type f` that also matches directories must not report this one.
    os.mkdir(os.path.join(scratch, "dir_trap.sh"))
    return sh_files


def run_shell01_ex02(student_file):
    # Absolute path for the subprocess (cwd= below would otherwise resolve
    # a relative student_file against the fixture dir, not main.py's own
    # cwd) - kept separate from student_file itself, which main.py's
    # print_exercise_result below still needs in its original relative
    # form for a short "exNN/name" label, not a long absolute path.
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

    scratch = tempfile.mkdtemp(prefix="claudenette_shell01_ex02_")
    try:
        sh_files = _build_fixture(scratch)
        # Basenames without the .sh extension - order isn't specified by
        # the subject, so this is compared as a multiset, not a sequence.
        expected = sorted(os.path.basename(f)[:-3] for f in sh_files)

        actual, err, code = run_sh(abs_file, cwd=scratch)
        actual_names = sorted(line for line in actual.splitlines() if line)

        check(
            actual_names == expected,
            "listed .sh basenames (extension stripped)",
            expected=expected,
            actual=actual_names,
            show_value=actual_names,
        )
        check(
            not any(name.endswith(".sh") for name in actual_names),
            "no entry still has the .sh extension attached",
        )
        check(
            "dir_trap" not in actual_names,
            "a directory named dir_trap.sh (not a file) was not listed",
        )
    finally:
        shutil.rmtree(scratch, ignore_errors=True)

    print_exercise_result(student_file, passed, i)
    return passed == i
