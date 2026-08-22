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


def expected_dump(dest_initial, src, nb):
    copy_len = min(len(src), nb)
    result = dest_initial + src[:copy_len] + "\x00"
    return result + "\xff" * (DUMP_LEN - len(result))


def run_C03_ex03(student_file):
    test_dir = os.path.dirname(os.path.abspath(__file__))
    harness_path = os.path.join(test_dir, "ex03_harness.c")
    exe_path = "./strncat"

    if not compile_source([student_file, harness_path], exe_path):
        return False

    print_command_execution(exe_path)

    test_cases = [
        ("Hello", ", World!", 100),
        ("Hello", ", World!", 3),
        ("Hello", ", World!", 0),
        ("", "abc", 2),
        ("abc", "", 5),
        ("a" * 20, "b" * 50, 25),
    ]

    passed_count = 0
    total_count = len(test_cases)

    for i, (dest_initial, src, nb) in enumerate(test_cases, 1):
        expected = expected_dump(dest_initial, src, nb)
        input_str = f"{nb}\n{len(dest_initial)}\n{dest_initial}{src}"
        actual, err, code = run_test_case(exe_path, input_data=input_str)
        desc = (
            f"ft_strncat(dest={display_str(dest_initial)}, src={display_str(src)}, "
            f"nb={nb})"
        )

        marker = actual[0] if actual else ""
        dump = actual[1:]
        ptr_ok = marker == "1"

        if ptr_ok and dump == expected:
            print_test_pass(
                i, f"{desc}: return value and NUL-terminated append as expected"
            )
            passed_count += 1
        elif not ptr_ok:
            print_test_fail(i, f"{desc}: did not return dest (return value mismatch)")
        else:
            print_test_fail(
                i,
                f"{desc}: content not as expected (always NUL-terminate right after "
                "the copied bytes - unlike strncpy, never pad to nb)",
                expected=expected,
                actual=dump,
            )

    print_exercise_result("ex03/ft_strncat.c", passed_count, total_count)

    if os.path.exists(exe_path):
        os.remove(exe_path)

    return passed_count == total_count
