import os
import tempfile

from utils.runner import run_test_case
from utils.ui import (
    display_str,
    print_command_execution,
    print_exercise_result,
    print_test_fail,
    print_test_pass,
)

from ..build_utils import build_via_makefile, check_all_c_files, cleanup_build

BINARY = "ft_tail"


def run_C10_ex02(student_file):
    student_dir = os.path.dirname(student_file)

    checks_ok = check_all_c_files(
        student_dir,
        ["close", "open", "read", "write", "malloc", "free", "strerror", "basename"],
    )

    build_result, binary_path = build_via_makefile(student_dir, BINARY)
    if not os.path.exists(binary_path):
        print_test_fail(
            1,
            f"`make` did not produce {BINARY} "
            f"(stderr: {display_str(build_result.stderr)})",
        )
        print_exercise_result("ex02/tail", 0, 1)
        cleanup_build(student_dir, BINARY)
        return False

    print_command_execution(binary_path)

    passed_count = 0
    total_count = 0

    def check(condition, description, expected=None, actual=None, show_value=None):
        nonlocal passed_count, total_count
        total_count += 1
        if condition:
            if show_value is not None:
                print_test_pass(total_count, f"{description} {display_str(show_value)} as expected")
            else:
                print_test_pass(total_count, f"{description} as expected")
            passed_count += 1
        else:
            print_test_fail(
                total_count, f"{description} not as expected", expected=expected, actual=actual
            )

    content = ("".join(f"line{i}\n" for i in range(1000))).encode()

    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, "test.txt")
        with open(path, "wb") as f:
            f.write(content)

        test_cases = [
            (10, content[-10:]),
            (1, content[-1:]),
            (0, b""),
            (len(content), content),
            (len(content) + 500, content),
        ]

        for n, expected in test_cases:
            actual, err, code = run_test_case(binary_path, input_data="", args=["-c", str(n), path])
            check(
                actual == expected.decode("latin-1"),
                f"tail -c {n} on a {len(content)}-byte file returns the last {min(n, len(content))} bytes",
                expected=expected.decode("latin-1"),
                actual=actual,
                show_value=actual,
            )

    print_exercise_result("ex02/tail", passed_count, total_count)

    cleanup_build(student_dir, BINARY)

    return passed_count == total_count and checks_ok
