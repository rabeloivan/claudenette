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


def sign(n):
    return (n > 0) - (n < 0)


def expected_ncmp_sign(s1, s2, n):
    limit = min(len(s1), len(s2), n)
    for i in range(limit):
        if s1[i] != s2[i]:
            return sign(ord(s1[i]) - ord(s2[i]))
    if limit >= n:
        return 0
    return sign(len(s1) - len(s2))


def run_C03_ex01(student_file):
    test_dir = os.path.dirname(os.path.abspath(__file__))
    harness_path = os.path.join(test_dir, "ex01_harness.c")
    exe_path = "./strncmp"

    if not compile_source([student_file, harness_path], exe_path):
        return False

    print_command_execution(exe_path)

    test_cases = [
        ("hello", "help", 3),
        ("hello", "help", 4),
        ("hello", "hello", 0),
        ("hello", "world", 0),
        ("hello", "hello world", 5),
        ("hello", "hello world", 100),
        ("abc", "abd", 2),
        ("abc", "abd", 3),
        ("", "", 5),
        ("a" * 500, "a" * 500, 1000),
        ("a" * 500 + "x", "a" * 500 + "y", 501),
    ]

    passed_count = 0
    total_count = len(test_cases)

    for i, (s1, s2, n) in enumerate(test_cases, 1):
        expected_sign = expected_ncmp_sign(s1, s2, n)
        input_str = f"{n}\n{len(s1)}\n{s1}{s2}"
        actual, err, code = run_test_case(exe_path, input_data=input_str)
        desc = f"ft_strncmp(s1={display_str(s1)}, s2={display_str(s2)}, n={n})"

        try:
            actual_val = int(actual)
            actual_sign = sign(actual_val)
        except ValueError:
            actual_val = None
            actual_sign = None

        sign_word = {1: "positive", 0: "zero", -1: "negative"}
        if actual_sign == expected_sign:
            print_test_pass(
                i, f"{desc}: returned value's sign ({sign_word[actual_sign]}) as expected"
            )
            passed_count += 1
        else:
            print_test_fail(
                i,
                f"{desc}: returned value's sign not as expected",
                expected=sign_word.get(expected_sign, expected_sign),
                actual=actual_val,
            )

    print_exercise_result("ex01/ft_strncmp.c", passed_count, total_count)

    if os.path.exists(exe_path):
        os.remove(exe_path)

    return passed_count == total_count
