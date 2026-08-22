import os

from utils.compiler import compile_source
from utils.runner import run_test_case
from utils.ui import (
    display_str,
    print_command_execution,
    print_exercise_result,
    print_test_fail,
    print_test_pass,
)


def expected_is_uppercase(s):
    if len(s) == 0:
        return 1
    for c in s:
        if not ("A" <= c <= "Z"):
            return 0
    return 1


def run_C02_ex05(student_file):
    test_dir = os.path.dirname(os.path.abspath(__file__))
    harness_path = os.path.join(test_dir, "ex05_harness.c")
    exe_path = "./str_is_uppercase"

    if not compile_source([student_file, harness_path], exe_path):
        return False

    print_command_execution(exe_path)

    test_cases = [
        "",
        "HELLO",
        "hello",
        "Hello",
        "HELLO1",
        "HELLO WORLD",
        "HELLO!",
        "ABCXYZ",
        "\t",
        "A" * 2000,
    ]

    passed_count = 0
    total_count = len(test_cases)

    for i, s in enumerate(test_cases, 1):
        expected = expected_is_uppercase(s)
        actual, err, code = run_test_case(exe_path, input_data=s)
        desc = f"ft_str_is_uppercase(str={display_str(s)})"

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
                actual=actual,
            )

    print_exercise_result("ex05/ft_str_is_uppercase.c", passed_count, total_count)

    if os.path.exists(exe_path):
        os.remove(exe_path)

    return passed_count == total_count
