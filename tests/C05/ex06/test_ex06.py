import os

from utils.compiler import compile_source
from utils.runner import run_test_case
from utils.ui import (
    print_command_execution,
    print_exercise_result,
    print_test_fail,
    print_test_pass,
)


def expected_is_prime(nb):
    if nb < 2:
        return 0
    i = 2
    while i * i <= nb:
        if nb % i == 0:
            return 0
        i += 1
    return 1


def run_C05_ex06(student_file):
    test_dir = os.path.dirname(os.path.abspath(__file__))
    harness_path = os.path.join(test_dir, "ex06_harness.c")
    exe_path = "./is_prime"

    if not compile_source([student_file, harness_path], exe_path):
        return False

    print_command_execution(exe_path)

    test_cases = [0, 1, 2, 3, 4, 17, 25, 97, 100, -7, 7919, 2147483647]

    passed_count = 0
    total_count = len(test_cases)

    for i, nb in enumerate(test_cases, 1):
        expected = expected_is_prime(nb)
        actual, err, code = run_test_case(exe_path, input_data=str(nb))
        desc = f"ft_is_prime(nb={nb})"

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

    print_exercise_result("ex06/ft_is_prime.c", passed_count, total_count)

    if os.path.exists(exe_path):
        os.remove(exe_path)

    return passed_count == total_count
