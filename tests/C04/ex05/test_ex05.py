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


def is_valid_base(base):
    if len(base) < 2:
        return False
    if len(set(base)) != len(base):
        return False
    if "+" in base or "-" in base:
        return False
    if any(c in WHITESPACE for c in base):
        return False
    return True


def expected_atoi_base(s, base):
    if not is_valid_base(base):
        return 0
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
    while i < n and s[i] in base:
        value = value * len(base) + base.index(s[i])
        i += 1
    return -value if neg else value


def run_C04_ex05(student_file):
    test_dir = os.path.dirname(os.path.abspath(__file__))
    harness_path = os.path.join(test_dir, "ex05_harness.c")
    exe_path = "./atoi_base"

    if not compile_source([student_file, harness_path], exe_path):
        return False

    print_command_execution(exe_path)

    test_cases = [
        ("42", "0123456789"),
        ("-42", "0123456789"),
        ("1010", "01"),
        ("FF", "0123456789ABCDEF"),
        ("ff", "0123456789ABCDEF"),
        ("op", "poneyvif"),
        ("  42", "0123456789"),
        ("--5", "0123456789"),
        ("", "0123456789"),
        ("abc", "0123456789"),
        ("42", "0"),
        ("42", ""),
        ("42", "001223344"),
        ("42", "01234567+9"),
        ("5", "0123 56789"),
    ]

    passed_count = 0
    total_count = len(test_cases)

    for i, (s, base) in enumerate(test_cases, 1):
        expected = expected_atoi_base(s, base)
        input_str = f"{len(base)}\n{base}{s}"
        actual, err, code = run_test_case(exe_path, input_data=input_str)
        desc = f"ft_atoi_base(str={display_str(s)}, base={display_str(base)})"

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

    print_exercise_result("ex05/ft_atoi_base.c", passed_count, total_count)

    if os.path.exists(exe_path):
        os.remove(exe_path)

    return passed_count == total_count
