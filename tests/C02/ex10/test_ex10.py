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


def expected_dump_and_len(src, size):
    true_len = len(src)
    if size == 0:
        copied = ""
    else:
        copy_len = min(true_len, size - 1)
        copied = src[:copy_len] + "\x00"
    dump = copied + "\xff" * (DUMP_LEN - len(copied))
    return true_len, dump


def run_C02_ex10(student_file):
    test_dir = os.path.dirname(os.path.abspath(__file__))
    harness_path = os.path.join(test_dir, "ex10_harness.c")
    exe_path = "./strlcpy"

    if not compile_source([student_file, harness_path], exe_path):
        return False

    print_command_execution(exe_path)

    test_cases = [
        ("hello", 10),
        ("hello", 6),
        ("hello", 5),
        ("hello", 3),
        ("hello", 1),
        ("hello", 0),
        ("", 5),
        ("", 0),
        ("a" * 100, 50),
        ("a" * 20, 200),
    ]

    passed_count = 0
    total_count = len(test_cases)

    for i, (src, size) in enumerate(test_cases, 1):
        expected_len, expected_dump = expected_dump_and_len(src, size)
        input_str = f"{size}\n{src}"
        actual, err, code = run_test_case(exe_path, input_data=input_str)
        desc = f"ft_strlcpy(dest, src={display_str(src)}, size={size})"

        ret_str = actual[:10]
        dump = actual[10:]
        try:
            ret_val = int(ret_str)
        except ValueError:
            ret_val = None

        ret_ok = ret_val == expected_len
        dump_ok = dump == expected_dump

        if ret_ok and dump_ok:
            print_test_pass(i, f"{desc}: return value and bounded copy as expected")
            passed_count += 1
        elif not ret_ok:
            print_test_fail(
                i,
                f"{desc}: return value not as expected (should always be strlen(src), "
                "regardless of truncation)",
                expected=expected_len,
                actual=ret_val,
            )
        else:
            print_test_fail(
                i,
                f"{desc}: first {size} bytes of dest not as expected (or wrote outside them)",
                expected=expected_dump[:size],
                actual=dump[:size],
            )

    print_exercise_result("ex10/ft_strlcpy.c", passed_count, total_count)

    if os.path.exists(exe_path):
        os.remove(exe_path)

    return passed_count == total_count
