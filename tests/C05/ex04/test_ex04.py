import os

from utils.compiler import compile_source
from utils.runner import run_test_case
from utils.ui import (
    print_command_execution,
    print_exercise_result,
    print_test_fail,
    print_test_pass,
)


def expected_fibonacci(index):
    if index < 0:
        return -1
    a, b = 0, 1
    for _ in range(index):
        a, b = b, a + b
    return a


def run_C05_ex04(student_file):
    test_dir = os.path.dirname(os.path.abspath(__file__))
    harness_path = os.path.join(test_dir, "ex04_harness.c")
    exe_path = "./fibonacci"

    if not compile_source([student_file, harness_path], exe_path):
        return False

    print_command_execution(exe_path)

    test_cases = [-1, -100, 0, 1, 2, 3, 4, 5, 10, 20, 30]

    passed_count = 0
    total_count = len(test_cases)

    for i, index in enumerate(test_cases, 1):
        expected = expected_fibonacci(index)
        actual, err, code = run_test_case(exe_path, input_data=str(index))
        desc = f"ft_fibonacci(index={index})"

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

    print_exercise_result("ex04/ft_fibonacci.c", passed_count, total_count)

    if os.path.exists(exe_path):
        os.remove(exe_path)

    return passed_count == total_count
