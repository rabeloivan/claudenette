import os

from utils.compiler import compile_source
from utils.runner import run_test_case
from utils.ui import (
    print_command_execution,
    print_exercise_result,
    print_test_fail,
    print_test_pass,
)


def run_C08_ex05(student_file):
    test_dir = os.path.dirname(os.path.abspath(__file__))
    harness_path = os.path.join(test_dir, "ex05_harness.c")
    exe_path = "./show_tab"

    flags = ["-Wall", "-Wextra", "-Werror", "-I", test_dir]
    if not compile_source([student_file, harness_path], exe_path, flags=flags):
        return False

    print_command_execution(exe_path)

    expected = "hello\n5\nhello\n" + "abc\n3\nXYZ\n" + "hi\n99\nhi\n"
    actual, err, code = run_test_case(exe_path, input_data="")
    desc = "ft_show_tab() over a 3-element table (str/size/copy per line)"

    passed = actual == expected
    if passed:
        print_test_pass(1, f"{desc}: output as expected")
    else:
        print_test_fail(
            1, f"{desc}: output not as expected", expected=expected, actual=actual
        )

    print_exercise_result("ex05/ft_show_tab.c", 1 if passed else 0, 1)

    if os.path.exists(exe_path):
        os.remove(exe_path)

    return passed
