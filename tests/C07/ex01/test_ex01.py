import os

from utils.compiler import compile_source
from utils.runner import run_test_case
from utils.ui import (
    print_command_execution,
    print_exercise_result,
    print_test_fail,
    print_test_pass,
)


def run_C07_ex01(student_file):
    test_dir = os.path.dirname(os.path.abspath(__file__))
    harness_path = os.path.join(test_dir, "ex01_harness.c")
    exe_path = "./range"

    if not compile_source([student_file, harness_path], exe_path):
        return False

    print_command_execution(exe_path)

    test_cases = [
        (0, 5),
        (5, 10),
        (-3, 3),
        (5, 5),
        (10, 5),
        (0, 1),
        (-5, -2),
    ]

    passed_count = 0
    total_count = len(test_cases)

    for i, (mn, mx) in enumerate(test_cases, 1):
        expected = list(range(mn, mx)) if mn < mx else None
        input_str = f"{mn}\n{mx}"
        actual, err, code = run_test_case(exe_path, input_data=input_str)
        desc = f"ft_range(min={mn}, max={mx})"

        if expected is None:
            if actual == "N":
                print_test_pass(i, f"{desc}: returned NULL as expected")
                passed_count += 1
            else:
                print_test_fail(
                    i, f"{desc}: did not return NULL", expected="NULL", actual=actual
                )
            continue

        if not actual.startswith("A"):
            print_test_fail(
                i, f"{desc}: returned NULL", expected=expected, actual="NULL"
            )
            continue

        body = actual[1:]
        try:
            actual_vals = [int(x) for x in body.split(",")] if body else []
        except ValueError:
            actual_vals = None

        if actual_vals == expected:
            print_test_pass(i, f"{desc}: returned array {actual_vals} as expected")
            passed_count += 1
        else:
            print_test_fail(
                i,
                f"{desc}: returned array not as expected",
                expected=expected,
                actual=body,
            )

    print_exercise_result("ex01/ft_range.c", passed_count, total_count)

    if os.path.exists(exe_path):
        os.remove(exe_path)

    return passed_count == total_count
