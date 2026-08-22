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


def expected_strlcat(dest_initial, src, size):
    dst_len = len(dest_initial)
    total = dst_len + len(src)
    available = size - dst_len - 1
    copy_len = min(len(src), available)
    result = dest_initial + src[:copy_len] + "\x00"
    dump = result + "\xff" * (DUMP_LEN - len(result))
    return total, dump


def run_C03_ex05(student_file):
    test_dir = os.path.dirname(os.path.abspath(__file__))
    harness_path = os.path.join(test_dir, "ex05_harness.c")
    exe_path = "./strlcat"

    if not compile_source([student_file, harness_path], exe_path):
        return False

    print_command_execution(exe_path)

    test_cases = [
        ("Hello", ", World!", 20),
        ("Hello", ", World!", 10),
        ("Hello", ", World!", 6),
        ("", "abc", 10),
        ("abc", "", 10),
        ("a" * 20, "b" * 20, 100),
        ("a" * 20, "b" * 50, 30),
    ]

    passed_count = 0
    total_count = len(test_cases)

    for i, (dest_initial, src, size) in enumerate(test_cases, 1):
        expected_len, expected_dump = expected_strlcat(dest_initial, src, size)
        input_str = f"{size}\n{len(dest_initial)}\n{dest_initial}{src}"
        actual, err, code = run_test_case(exe_path, input_data=input_str)
        desc = (
            f"ft_strlcat(dest={display_str(dest_initial)}, src={display_str(src)}, "
            f"size={size})"
        )

        ret_str = actual[:10]
        dump = actual[10:]
        try:
            ret_val = int(ret_str)
        except ValueError:
            ret_val = None

        ret_ok = ret_val == expected_len
        dump_ok = dump == expected_dump

        if ret_ok and dump_ok:
            print_test_pass(
                i, f"{desc}: return value and appended/bounded dest as expected"
            )
            passed_count += 1
        elif not ret_ok:
            print_test_fail(
                i,
                f"{desc}: return value not as expected (should always be "
                "strlen(initial dest) + strlen(src), regardless of truncation)",
                expected=expected_len,
                actual=ret_val,
            )
        else:
            print_test_fail(
                i,
                f"{desc}: content not as expected (or wrote outside the first "
                f"{size} bytes)",
                expected=expected_dump,
                actual=dump,
            )

    print_exercise_result("ex05/ft_strlcat.c", passed_count, total_count)

    if os.path.exists(exe_path):
        os.remove(exe_path)

    return passed_count == total_count
