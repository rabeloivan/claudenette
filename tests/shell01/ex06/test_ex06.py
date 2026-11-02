import os
import shutil
import subprocess
import tempfile

from utils.ui import print_exercise_result, print_test_fail, print_test_pass

from ...shell_utils import run_sh


def run_shell01_ex06(student_file):
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

    scratch = tempfile.mkdtemp(prefix="claudenette_shell01_ex06_")
    try:
        for n in range(6):
            with open(f"{scratch}/file{n}.txt", "w") as f:
                f.write("x\n")

        real_ls = subprocess.run(
            ["ls", "-l"], cwd=scratch, capture_output=True, text=True, timeout=5
        ).stdout.splitlines()
        # "Every second line, starting from the first" - 1st, 3rd, 5th...,
        # i.e. even 0-indexed positions.
        expected = "\n".join(real_ls[0::2]) + "\n"

        actual, err, code = run_sh(abs_file, cwd=scratch)

        check(
            actual == expected,
            "output (real `ls -l`'s odd-numbered lines only)",
            expected=expected,
            actual=actual,
        )
    finally:
        shutil.rmtree(scratch, ignore_errors=True)

    print_exercise_result(student_file, passed, i)
    return passed == i
