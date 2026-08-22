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

BINARY = "ft_display_file"


def run_C10_ex00(student_file):
    student_dir = os.path.dirname(student_file)

    checks_ok = check_all_c_files(student_dir, ["close", "open", "read", "write"])

    build_result, binary_path = build_via_makefile(student_dir, BINARY)
    if not os.path.exists(binary_path):
        print_test_fail(
            1,
            f"`make` did not produce {BINARY} "
            f"(stderr: {display_str(build_result.stderr)})",
        )
        print_exercise_result("ex00/display_file", 0, 1)
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

    actual, err, code = run_test_case(binary_path, input_data="", args=[])
    check(
        err == "File name missing.\n",
        "no arguments: stderr",
        expected="File name missing.\n",
        actual=err,
        show_value=err,
    )

    actual, err, code = run_test_case(binary_path, input_data="", args=["a", "b"])
    check(
        err == "Too many arguments.\n",
        "two arguments: stderr",
        expected="Too many arguments.\n",
        actual=err,
        show_value=err,
    )

    actual, err, code = run_test_case(
        binary_path, input_data="", args=["/nonexistent/path/claudenette_test.txt"]
    )
    check(
        err == "Cannot read file.\n",
        "nonexistent file: stderr",
        expected="Cannot read file.\n",
        actual=err,
        show_value=err,
    )

    contents = [
        b"hello world\n",
        b"",
        bytes(range(256)) * 4,
        ("x" * 50000).encode(),
    ]

    with tempfile.TemporaryDirectory() as tmpdir:
        for i, content in enumerate(contents):
            path = os.path.join(tmpdir, f"file{i}.txt")
            with open(path, "wb") as f:
                f.write(content)

            actual, err, code = run_test_case(binary_path, input_data="", args=[path])
            expected = content.decode("latin-1")
            check(
                actual == expected,
                f"a {len(content)}-byte file's content on stdout",
                expected=expected,
                actual=actual,
                show_value=actual,
            )

    print_exercise_result("ex00/display_file", passed_count, total_count)

    cleanup_build(student_dir, BINARY)

    return passed_count == total_count and checks_ok
