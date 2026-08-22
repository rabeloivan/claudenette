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


def run_C03_ex04(student_file):
    test_dir = os.path.dirname(os.path.abspath(__file__))
    harness_path = os.path.join(test_dir, "ex04_harness.c")
    exe_path = "./strstr"

    if not compile_source([student_file, harness_path], exe_path):
        return False

    print_command_execution(exe_path)

    test_cases = [
        ("hello world", "world"),
        ("hello world", "hello"),
        ("hello world", "xyz"),
        ("hello world", ""),
        ("", "abc"),
        ("", ""),
        ("aaaa", "aa"),
        ("ababab", "abab"),
        ("hello world", "hello world"),
        ("Hello World", "world"),
        ("abc" * 100 + "needle" + "def" * 100, "needle"),
    ]

    passed_count = 0
    total_count = len(test_cases)

    for i, (haystack, needle) in enumerate(test_cases, 1):
        expected_offset = haystack.find(needle)
        input_str = f"{len(needle)}\n{needle}{haystack}"
        actual, err, code = run_test_case(exe_path, input_data=input_str)
        desc = f"ft_strstr(str={display_str(haystack)}, to_find={display_str(needle)})"

        try:
            actual_offset = int(actual)
        except ValueError:
            actual_offset = None

        if actual_offset == expected_offset:
            print_test_pass(i, f"{desc}: returned offset {actual_offset} as expected")
            passed_count += 1
        else:
            print_test_fail(
                i,
                f"{desc}: returned offset not as expected (-1 means NULL/not found)",
                expected=expected_offset,
                actual=actual_offset,
            )

    print_exercise_result("ex04/ft_strstr.c", passed_count, total_count)

    if os.path.exists(exe_path):
        os.remove(exe_path)

    return passed_count == total_count
