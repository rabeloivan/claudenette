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


def expected_cmp_sign(s1, s2):
    n = min(len(s1), len(s2))
    for i in range(n):
        if s1[i] != s2[i]:
            return sign(ord(s1[i]) - ord(s2[i]))
    return sign(len(s1) - len(s2))


def run_C03_ex00(student_file):
    test_dir = os.path.dirname(os.path.abspath(__file__))
    harness_path = os.path.join(test_dir, "ex00_harness.c")
    exe_path = "./strcmp"

    if not compile_source([student_file, harness_path], exe_path):
        return False

    print_command_execution(exe_path)

    test_cases = [
        ("hello", "hello"),
        ("abc", "abd"),
        ("abd", "abc"),
        ("abc", "abcdef"),
        ("abcdef", "abc"),
        ("", ""),
        ("", "a"),
        ("a", ""),
        ("ABC", "abc"),
        ("Hello World", "Hello World"),
        ("a" * 500, "a" * 500),
        ("a" * 500 + "b", "a" * 500 + "c"),
    ]

    passed_count = 0
    total_count = len(test_cases)

    for i, (s1, s2) in enumerate(test_cases, 1):
        expected_sign = expected_cmp_sign(s1, s2)
        input_str = f"{len(s1)}\n{s1}{s2}"
        actual, err, code = run_test_case(exe_path, input_data=input_str)
        desc = f"ft_strcmp(s1={display_str(s1)}, s2={display_str(s2)})"

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

    print_exercise_result("ex00/ft_strcmp.c", passed_count, total_count)

    if os.path.exists(exe_path):
        os.remove(exe_path)

    return passed_count == total_count
