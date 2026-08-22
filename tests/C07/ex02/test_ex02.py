import os

from utils.compiler import compile_source
from utils.runner import run_test_case
from utils.ui import (
    print_command_execution,
    print_exercise_result,
    print_test_fail,
    print_test_pass,
)


def run_C07_ex02(student_file):
    test_dir = os.path.dirname(os.path.abspath(__file__))
    harness_path = os.path.join(test_dir, "ex02_harness.c")
    exe_path = "./ultimate_range"

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
    ]

    passed_count = 0
    total_count = len(test_cases)

    for i, (mn, mx) in enumerate(test_cases, 1):
        expected_vals = list(range(mn, mx)) if mn < mx else []
        expected_ret = len(expected_vals)
        input_str = f"{mn}\n{mx}"
        actual, err, code = run_test_case(exe_path, input_data=input_str)
        desc = f"ft_ultimate_range(range, min={mn}, max={mx})"

        if "|" not in actual:
            print_test_fail(i, f"{desc}: produced unparseable output", actual=actual)
            continue

        ret_part, _, rest = actual.partition("|")
        try:
            actual_ret = int(ret_part)
        except ValueError:
            actual_ret = None

        if rest == "U":
            print_test_fail(
                i,
                f"{desc}: *range was left untouched",
                expected="NULL" if expected_ret == 0 else "a new allocation",
                actual="untouched",
            )
            continue

        if expected_ret == 0:
            if actual_ret == 0 and rest == "N":
                print_test_pass(i, f"{desc}: return value and *range == NULL as expected")
                passed_count += 1
            else:
                print_test_fail(
                    i,
                    f"{desc}: return value / *range not as expected",
                    expected="0 with *range == NULL",
                    actual=f"{actual_ret} with range-marker {rest!r}",
                )
            continue

        if not rest.startswith("A"):
            print_test_fail(
                i,
                f"{desc}: *range == NULL, expected a valid allocation",
                expected=expected_ret,
                actual=actual_ret,
            )
            continue

        body = rest[1:]
        try:
            actual_vals = [int(x) for x in body.split(",")] if body else []
        except ValueError:
            actual_vals = None

        if actual_ret == expected_ret and actual_vals == expected_vals:
            print_test_pass(i, f"{desc}: return value and *range {actual_vals} as expected")
            passed_count += 1
        else:
            print_test_fail(
                i,
                f"{desc}: return value / *range not as expected",
                expected=f"{expected_ret} with *range == {expected_vals}",
                actual=f"{actual_ret} with *range == {body}",
            )

    print_exercise_result("ex02/ft_ultimate_range.c", passed_count, total_count)

    if os.path.exists(exe_path):
        os.remove(exe_path)

    return passed_count == total_count
