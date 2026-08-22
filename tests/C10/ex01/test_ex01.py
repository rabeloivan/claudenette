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

BINARY = "ft_cat"


def run_C10_ex01(student_file):
    student_dir = os.path.dirname(student_file)

    checks_ok = check_all_c_files(
        student_dir, ["close", "open", "read", "write", "strerror", "basename"]
    )

    build_result, binary_path = build_via_makefile(student_dir, BINARY)
    if not os.path.exists(binary_path):
        print_test_fail(
            1,
            f"`make` did not produce {BINARY} "
            f"(stderr: {display_str(build_result.stderr)})",
        )
        print_exercise_result("ex01/cat", 0, 1)
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

    with tempfile.TemporaryDirectory() as tmpdir:
        a_path = os.path.join(tmpdir, "a.txt")
        b_path = os.path.join(tmpdir, "b.txt")
        big_path = os.path.join(tmpdir, "big.bin")
        a_content = b"hello world\n"
        b_content = b"second file\nwith two lines\n"
        big_content = bytes(range(256)) * 200  # ~51KB, well past the ~30KB cap

        with open(a_path, "wb") as f:
            f.write(a_content)
        with open(b_path, "wb") as f:
            f.write(b_content)
        with open(big_path, "wb") as f:
            f.write(big_content)

        actual, err, code = run_test_case(binary_path, input_data="", args=[a_path])
        check(
            actual == a_content.decode("latin-1"),
            "single file: stdout content",
            expected=a_content.decode("latin-1"),
            actual=actual,
            show_value=actual,
        )

        actual, err, code = run_test_case(binary_path, input_data="", args=[a_path, b_path])
        expected_concat = (a_content + b_content).decode("latin-1")
        check(
            actual == expected_concat,
            "two files: stdout concatenation, in argument order",
            expected=expected_concat,
            actual=actual,
        )

        actual, err, code = run_test_case(binary_path, input_data="", args=[big_path])
        check(
            actual == big_content.decode("latin-1"),
            f"a {len(big_content)}-byte file (well past the ~30KB buffer cap)",
            expected=big_content.decode("latin-1"),
            actual=actual,
        )

        missing_path = os.path.join(tmpdir, "does_not_exist.txt")
        actual, err, code = run_test_case(
            binary_path, input_data="", args=[a_path, missing_path, b_path]
        )
        check(
            a_content.decode("latin-1") in actual and b_content.decode("latin-1") in actual,
            "a missing file in the middle doesn't block the surrounding files",
            expected="both surrounding files' content present",
            actual=actual,
        )
        check(
            err != "",
            "a missing file produces some error indication on stderr",
            expected="non-empty stderr",
            actual=err,
        )

        stdin_text = "piped through stdin\n"
        actual, err, code = run_test_case(binary_path, input_data=stdin_text, args=[])
        check(
            actual == stdin_text,
            "no file arguments: stdin echoed back, matching real cat",
            expected=stdin_text,
            actual=actual,
            show_value=actual,
        )

    print_exercise_result("ex01/cat", passed_count, total_count)

    cleanup_build(student_dir, BINARY)

    return passed_count == total_count and checks_ok
