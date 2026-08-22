import os

from utils.compiler import compile_source
from utils.runner import run_test_case
from utils.ui import (
    print_command_execution,
    print_exercise_result,
    print_test_fail,
    print_test_pass,
)


def expected_factorial(nb):
    if nb < 0:
        return 0
    result = 1
    for i in range(2, nb + 1):
        result *= i
    return result


def run_C05_ex00(student_file):
    test_dir = os.path.dirname(os.path.abspath(__file__))
    harness_path = os.path.join(test_dir, "ex00_harness.c")
    exe_path = "./iterative_factorial"

    if not compile_source([student_file, harness_path], exe_path):
        return False

    print_command_execution(exe_path)

    test_cases = [0, 1, 2, 3, 5, 10, 12, -1, -5, -2147483648]

    passed_count = 0
    total_count = len(test_cases)

    for i, nb in enumerate(test_cases, 1):
        expected = expected_factorial(nb)
        actual, err, code = run_test_case(exe_path, input_data=str(nb))
        desc = f"ft_iterative_factorial(nb={nb})"

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

    print_exercise_result("ex00/ft_iterative_factorial.c", passed_count, total_count)

    if os.path.exists(exe_path):
        os.remove(exe_path)

    return passed_count == total_count
