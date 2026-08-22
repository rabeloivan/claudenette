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

DUMP_LEN = 512


def expected_dump(src):
    copied = src + "\x00"
    return copied + "\xff" * (DUMP_LEN - len(copied))


def run_C02_ex00(student_file):
    test_dir = os.path.dirname(os.path.abspath(__file__))
    harness_path = os.path.join(test_dir, "ex00_harness.c")
    exe_path = "./strcpy"

    if not compile_source([student_file, harness_path], exe_path):
        return False

    print_command_execution(exe_path)

    test_cases = [
        "",
        "a",
        "hello",
        "Hello, World!",
        "line1\nline2\ttab",
        " leading and trailing space ",
        "a" * 400,
    ]

    passed_count = 0
    total_count = len(test_cases)

    for i, src in enumerate(test_cases, 1):
        expected = expected_dump(src)
        actual, err, code = run_test_case(exe_path, input_data=src)
        desc = f"ft_strcpy(dest, src={display_str(src)})"

        marker = actual[0] if actual else ""
        dump = actual[1:]
        ptr_ok = marker == "1"
        content_ok = dump == expected

        if ptr_ok and content_ok:
            print_test_pass(i, f"{desc}: return value and copy as expected")
            passed_count += 1
        elif not ptr_ok:
            print_test_fail(i, f"{desc}: did not return dest (return value mismatch)")
        else:
            print_test_fail(
                i, f"{desc}: copy not as expected", expected=expected, actual=dump
            )

    print_exercise_result("ex00/ft_strcpy.c", passed_count, total_count)

    if os.path.exists(exe_path):
        os.remove(exe_path)

    return passed_count == total_count
