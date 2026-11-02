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

from ..build_utils import (
    build_via_makefile,
    check_all_c_files,
    check_makefile_rules,
    cleanup_build,
)

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

        # "performs the same function as the system's cat": a file that cannot
        # be read adds nothing to stdout and makes the exit status non-zero
        # (">0", cat(1)), while every other file is still printed; stderr gets
        # "cat: name: reason" - the same line from BSD and GNU cat, and what
        # the subject's strerror and basename are for. Only the program-name
        # part is left free, since argv[0] and its basename are both fair.
        missing_path = os.path.join(tmpdir, "does_not_exist.txt")
        actual, err, code = run_test_case(
            binary_path, input_data="", args=[a_path, missing_path, b_path]
        )
        expected_concat = (a_content + b_content).decode("latin-1")
        check(
            actual == expected_concat,
            "a missing file in the middle: the files around it printed, nothing else",
            expected=expected_concat,
            actual=actual,
        )
        check(
            "does_not_exist.txt: No such file or directory\n" in err,
            "a missing file: stderr names it and says why",
            expected="...does_not_exist.txt: No such file or directory\n",
            actual=err,
        )
        check(code > 0, "a missing file: non-zero exit status", expected="> 0", actual=code)

        actual, err, code = run_test_case(binary_path, input_data="", args=[tmpdir])
        dir_line = f"{os.path.basename(tmpdir)}: Is a directory\n"
        check(
            dir_line in err and code > 0,
            "a directory argument: named on stderr with 'Is a directory', non-zero exit",
            expected=f"exit > 0, stderr containing '{dir_line}'",
            actual=f"exit {code}, stderr '{err}'",
        )

        # "-" is stdin, in its place among the files - and, every file being
        # readable, the run is a success: exit 0 and nothing on stderr.
        actual, err, code = run_test_case(
            binary_path, input_data="from stdin\n", args=[a_path, "-", b_path]
        )
        expected_dash = (a_content + b"from stdin\n" + b_content).decode("latin-1")
        check(
            actual == expected_dash,
            "`-` among the files reads stdin at that position",
            expected=expected_dash,
            actual=actual,
        )
        check(
            code == 0 and err == "",
            "`-` among readable files: exit 0, nothing on stderr",
            expected="exit 0, empty stderr",
            actual=f"exit {code}, stderr '{err}'",
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

    # The subject requires a Makefile with all/clean/fclean, but everything
    # above only ever invoked the default target - see check_makefile_rules.
    # Run last: it ends on fclean, which removes the binary the cases needed.
    for rule_ok, rule_desc, rule_exp, rule_act in check_makefile_rules(student_dir, BINARY):
        check(rule_ok, rule_desc, expected=rule_exp, actual=rule_act)

    print_exercise_result("ex01/cat", passed_count, total_count)

    cleanup_build(student_dir, BINARY)

    return passed_count == total_count and checks_ok
