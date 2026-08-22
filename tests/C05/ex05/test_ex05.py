import os

from utils.compiler import compile_source
from utils.runner import run_test_case
from utils.ui import (
    print_command_execution,
    print_exercise_result,
    print_test_fail,
    print_test_pass,
)


def expected_sqrt(nb):
    if nb < 0:
        return 0
    r = int(nb**0.5)
    while r * r > nb:
        r -= 1
    while (r + 1) * (r + 1) <= nb:
        r += 1
    if r * r == nb:
        return r
    return 0


def run_C05_ex05(student_file):
    test_dir = os.path.dirname(os.path.abspath(__file__))
    harness_path = os.path.join(test_dir, "ex05_harness.c")
    exe_path = "./sqrt"

    if not compile_source([student_file, harness_path], exe_path):
        return False

    print_command_execution(exe_path)

    test_cases = [0, 1, 4, 9, 100, 2, 10, 3, -4, -1, 2147395600, 2147483647]

    passed_count = 0
    total_count = len(test_cases)

    for i, nb in enumerate(test_cases, 1):
        expected = expected_sqrt(nb)
        actual, err, code = run_test_case(exe_path, input_data=str(nb))
        desc = f"ft_sqrt(nb={nb})"

        try:
            actual_val = int(actual)
        except ValueError:
            actual_val = None

        if actual_val == expected:
            print_test_pass(i, f"{desc}: returned {actual_val} as expected")
            passed_count += 1
        else:
            print_test_fail(
                i,
                f"{desc}: returned value not as expected",
                expected=expected,
                actual=actual_val,
            )

    print_exercise_result("ex05/ft_sqrt.c", passed_count, total_count)

    if os.path.exists(exe_path):
        os.remove(exe_path)

    return passed_count == total_count
