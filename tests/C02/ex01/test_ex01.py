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


def expected_dump(src, n):
    copy_len = min(len(src), n)
    copied = src[:copy_len]
    if len(copied) < n:
        copied += "\x00" * (n - len(copied))
    return copied + "\xff" * (DUMP_LEN - len(copied))


def run_C02_ex01(student_file):
    test_dir = os.path.dirname(os.path.abspath(__file__))
    harness_path = os.path.join(test_dir, "ex01_harness.c")
    exe_path = "./strncpy"

    if not compile_source([student_file, harness_path], exe_path):
        return False

    print_command_execution(exe_path)

    test_cases = [
        ("hello", 10),
        ("hello", 5),
        ("hello", 3),
        ("hello", 0),
        ("", 5),
        ("", 0),
        ("hi", 2),
        ("a" * 100, 50),
        ("a" * 20, 100),
    ]

    passed_count = 0
    total_count = len(test_cases)

    for i, (src, n) in enumerate(test_cases, 1):
        expected = expected_dump(src, n)
        input_str = f"{n}\n{src}"
        actual, err, code = run_test_case(exe_path, input_data=input_str)
        desc = f"ft_strncpy(dest, src={display_str(src)}, n={n})"

        marker = actual[0] if actual else ""
        dump = actual[1:]
        ptr_ok = marker == "1"
        content_ok = dump == expected

        if ptr_ok and content_ok:
            print_test_pass(i, f"{desc}: return value and copy/pad as expected")
            passed_count += 1
        elif not ptr_ok:
            print_test_fail(i, f"{desc}: did not return dest (return value mismatch)")
        else:
            print_test_fail(
                i,
                f"{desc}: first {n} bytes of dest not as expected (or wrote outside them)",
                expected=expected[:n],
                actual=dump[:n],
            )

    print_exercise_result("ex01/ft_strncpy.c", passed_count, total_count)

    if os.path.exists(exe_path):
        os.remove(exe_path)

    return passed_count == total_count
