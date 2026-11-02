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

from ..build_utils import (
    build_via_makefile,
    check_all_c_files,
    check_makefile_rules,
    cleanup_build,
)

BINARY = "ft_hexdump"


def real_hexdump(paths, cwd=None):
    result = subprocess.run(
        ["hexdump", "-C"] + paths, capture_output=True, cwd=cwd, timeout=5
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
        # Should be unreachable: this exercise declares requires_tools:
        # ["hexdump"] so preflight() refuses the run first. Kept as a backstop
        # for anyone calling run_C10_ex03 directly, and it RAISES rather than
        # reporting a failed test - a missing tool on the grader's machine is
        # not the student being wrong, and main.py surfaces an exception as
        # CRASH ("a bug in claudenette, not necessarily your submission")
        # rather than as KO.
        cleanup_build(student_dir, BINARY)
        raise RuntimeError(
            "system `hexdump` not found - this exercise is graded against its "
            "output, so it cannot be graded here. Install it (Debian/Ubuntu: "
            "bsdextrautils; macOS: it ships with the base system)."
        )

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
        # Two identical rows print one '*' whether or not the implementation
        # remembers it already printed one, so only a longer run shows a '*'
        # repeated per row; and a second run shows whether the state is reset
        # when a different row ends the first.
        "four identical rows (one '*' for the whole run)": b"A" * 16 * 4 + b"BBBBBB",
        "two separate repeated runs": b"A" * 48 + b"B" * 16 + b"C" * 48 + b"end",
        "ends inside a repeated run": b"Z" * 48,
        "non_printable_bytes": bytes([0, 1, 2, 0x1F, 0x7F, 0x80, 0xFF]) + b"hello",
        "larger_file (~3KB)": (bytes(range(256)) * 12),
    }

    with tempfile.TemporaryDirectory() as tmpdir:
        for label, content in contents.items():
            path = os.path.join(tmpdir, "test.bin")
            with open(path, "wb") as f:
                f.write(content)

            expected = real_hexdump([path])
            actual, err, code = run_test_case(binary_path, input_data="", args=["-C", path])
            check(
                actual == expected,
                f"{label} ({len(content)} bytes): output matches real `hexdump -C`",
                expected=expected,
                actual=actual,
                show_value=actual,
            )

        # "performs the same function as the system's hexdump" - which reads
        # several files as ONE stream: the offset carries on, and a row is
        # filled across the boundary rather than cut short at the end of each
        # file. A file that cannot be opened is skipped, with a non-zero exit
        # and "hexdump: name: reason" on stderr. BSD and GNU hexdump agree
        # byte for byte on all of it but the program name, which is left
        # free (argv[0] or its basename). Relative names, run from tmpdir,
        # so a failure shows no temp path - and so the binary's own path must
        # be absolute, or it would resolve against tmpdir too.
        exe = os.path.abspath(binary_path)
        with open(os.path.join(tmpdir, "one.bin"), "wb") as f:
            f.write(b"hello")
        with open(os.path.join(tmpdir, "two.bin"), "wb") as f:
            f.write(bytes(range(40)))

        args = ["-C", "one.bin", "two.bin"]
        expected = real_hexdump(args[1:], tmpdir)
        actual, err, code = run_test_case(exe, input_data="", args=args, cwd=tmpdir)
        check(
            actual == expected,
            "two files, a row spanning the boundary: output matches real `hexdump -C`",
            expected=expected,
            actual=actual,
            show_value=actual,
        )
        check(
            code == 0 and err == "",
            "two readable files: exit 0, nothing on stderr",
            expected="exit 0, empty stderr",
            actual=f"exit {code}, stderr '{err}'",
        )

        args = ["-C", "one.bin", "missing.bin", "two.bin"]
        expected = real_hexdump(args[1:], tmpdir)
        actual, err, code = run_test_case(exe, input_data="", args=args, cwd=tmpdir)
        check(
            actual == expected,
            "a missing file between two others: output matches real `hexdump -C`",
            expected=expected,
            actual=actual,
            show_value=actual,
        )
        check(
            "missing.bin: No such file or directory\n" in err and code > 0,
            "a missing file: named on stderr with the reason, non-zero exit",
            expected="exit > 0, stderr containing 'missing.bin: No such file or directory\n'",
            actual=f"exit {code}, stderr '{err}'",
        )

    # The subject requires a Makefile with all/clean/fclean, but everything
    # above only ever invoked the default target - see check_makefile_rules.
    # Run last: it ends on fclean, which removes the binary the cases needed.
    for rule_ok, rule_desc, rule_exp, rule_act in check_makefile_rules(student_dir, BINARY):
        check(rule_ok, rule_desc, expected=rule_exp, actual=rule_act)

    print_exercise_result("ex03/hexdump", passed_count, total_count)

    cleanup_build(student_dir, BINARY)

    return passed_count == total_count and checks_ok
