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

WHITESPACE = (" ", "\t", "\n", "\v", "\f", "\r")


def expected_atoi(s):
    i = 0
    n = len(s)
    while i < n and s[i] in WHITESPACE:
        i += 1
    neg = False
    while i < n and s[i] in ("+", "-"):
        if s[i] == "-":
            neg = not neg
        i += 1
    value = 0
    while i < n and "0" <= s[i] <= "9":
        value = value * 10 + (ord(s[i]) - ord("0"))
        i += 1
    return -value if neg else value


def run_C04_ex03(student_file):
    test_dir = os.path.dirname(os.path.abspath(__file__))
    harness_path = os.path.join(test_dir, "ex03_harness.c")
    exe_path = "./atoi"

    if not compile_source([student_file, harness_path], exe_path):
        return False

    print_command_execution(exe_path)

    test_cases = [
        "42",
        "-42",
        "  42",
        "\t\n  123",
        "+42",
        "--5",
        "---5",
        "+-+-5",
        "-+-5",
        "abc",
        "",
        "   ",
        "0",
        "007",
        "2147483647",
        "-2147483647",
        "42abc",
        " - 42",
        " ---+--+1234ab567",
    ]

    passed_count = 0
    total_count = len(test_cases)

    for i, s in enumerate(test_cases, 1):
        expected = expected_atoi(s)
        actual, err, code = run_test_case(exe_path, input_data=s)
        desc = f"ft_atoi(str={display_str(s)})"

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

    print_exercise_result("ex03/ft_atoi.c", passed_count, total_count)

    if os.path.exists(exe_path):
        os.remove(exe_path)

    return passed_count == total_count
