import os
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

BINARY = "ft_tail"


def real_tail(args, cwd):
    result = subprocess.run(["tail"] + args, capture_output=True, cwd=cwd, timeout=10)
    return result.stdout.decode("latin-1")


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

        # 7 and 1000 do not divide the file's 7890 bytes. Of the others, 10, 1
        # and 7890 all do, and 0 or an n past the end never fill a buffer, so
        # a circular buffer always finished exactly on a wrap, with nothing
        # after the wrap point to print - deleting the write that prints it
        # went unnoticed.
        test_cases = [
            (10, content[-10:]),
            (1, content[-1:]),
            (0, b""),
            (7, content[-7:]),
            (1000, content[-1000:]),
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

        # "performs the same function as the system command tail" - with
        # several files that means a "==> name <==" header before each, and a
        # file that cannot be opened named on stderr, with a non-zero exit,
        # the others still printed. BSD and GNU tail write byte-identical
        # stdout for these, so the real one is the oracle. Their error lines
        # differ - GNU says "cannot open 'name' for reading: reason" where BSD
        # says "name: reason" - so only a line naming the file is required.
        #
        # Relative names, run from tmpdir: the headers carry the name exactly
        # as given, and a temp path in them would bury any failure. The
        # binary's own path must then be absolute, or it would resolve
        # against tmpdir too.
        exe = os.path.abspath(binary_path)
        with open(os.path.join(tmpdir, "other.txt"), "wb") as f:
            f.write(b"abc\ndef\n")

        args = ["-c", "5", "test.txt", "other.txt"]
        expected = real_tail(args, tmpdir)
        actual, err, code = run_test_case(exe, input_data="", args=args, cwd=tmpdir)
        check(
            actual == expected,
            "tail -c 5 on two files: a `==> name <==` header before each",
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

        args = ["-c", "5", "test.txt", "missing.txt", "other.txt"]
        expected = real_tail(args, tmpdir)
        actual, err, code = run_test_case(exe, input_data="", args=args, cwd=tmpdir)
        check(
            actual == expected,
            "a missing file between two others: both others still printed",
            expected=expected,
            actual=actual,
            show_value=actual,
        )
        check(
            "missing.txt" in err and err.endswith("\n") and code > 0,
            "a missing file: named on stderr, non-zero exit",
            expected="a line naming 'missing.txt' on stderr, exit > 0",
            actual=f"exit {code}, stderr '{err}'",
        )

    # The subject requires a Makefile with all/clean/fclean, but everything
    # above only ever invoked the default target - see check_makefile_rules.
    # Run last: it ends on fclean, which removes the binary the cases needed.
    for rule_ok, rule_desc, rule_exp, rule_act in check_makefile_rules(student_dir, BINARY):
        check(rule_ok, rule_desc, expected=rule_exp, actual=rule_act)

    print_exercise_result("ex02/tail", passed_count, total_count)

    cleanup_build(student_dir, BINARY)

    return passed_count == total_count and checks_ok
