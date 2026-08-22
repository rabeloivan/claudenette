import os
import shutil
import subprocess
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

BINARY = "ft_hexdump"


def real_hexdump(path):
    result = subprocess.run(
        ["hexdump", "-C", path], capture_output=True, timeout=5
    )
    return result.stdout.decode("latin-1")


def run_C10_ex03(student_file):
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
        print_exercise_result("ex03/hexdump", 0, 1)
        cleanup_build(student_dir, BINARY)
        return False

    if shutil.which("hexdump") is None:
        print_test_fail(1, "system `hexdump` not found - can't build an expected-output oracle")
        print_exercise_result("ex03/hexdump", 0, 1)
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

    contents = {
        "empty": b"",
        "one_byte": b"A",
        "exactly_16": b"0123456789ABCDEF",
        "partial_last_line": b"0123456789ABCDEF0123456789ABCDEF01234",
        "repeated_rows (tests the '*' collapsing)": b"A" * 16 * 2 + b"BBBBBB",
        "non_printable_bytes": bytes([0, 1, 2, 0x1F, 0x7F, 0x80, 0xFF]) + b"hello",
        "larger_file (~3KB)": (bytes(range(256)) * 12),
    }

    with tempfile.TemporaryDirectory() as tmpdir:
        for label, content in contents.items():
            path = os.path.join(tmpdir, "test.bin")
            with open(path, "wb") as f:
                f.write(content)

            expected = real_hexdump(path)
            actual, err, code = run_test_case(binary_path, input_data="", args=["-C", path])
            check(
                actual == expected,
                f"{label} ({len(content)} bytes): output matches real `hexdump -C`",
                expected=expected,
                actual=actual,
                show_value=actual,
            )

    print_exercise_result("ex03/hexdump", passed_count, total_count)

    cleanup_build(student_dir, BINARY)

    return passed_count == total_count and checks_ok
