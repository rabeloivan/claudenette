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


def run_C07_ex00(student_file):
    test_dir = os.path.dirname(os.path.abspath(__file__))
    harness_path = os.path.join(test_dir, "ex00_harness.c")
    exe_path = "./strdup"

    if not compile_source([student_file, harness_path], exe_path):
        return False

    print_command_execution(exe_path)

    test_cases = [
        "",
        "hello",
        "Hello, World!",
        "a",
        "42 is the answer",
        "x" * 400,
    ]

    passed_count = 0
    total_count = len(test_cases)

    for i, s in enumerate(test_cases, 1):
        actual, err, code = run_test_case(exe_path, input_data=s)
        desc = f"ft_strdup(src={display_str(s)})"

        marker = actual[:1]
        content = actual[1:]

        if marker == "S":
            print_test_fail(
                i, f"{desc}: returned the SAME pointer as src (no allocation happened)"
            )
        elif marker != "D":
            print_test_fail(i, f"{desc}: returned NULL", expected=s, actual="NULL")
        elif content == s:
            print_test_pass(i, f"{desc}: new allocation content as expected")
            passed_count += 1
        else:
            print_test_fail(
                i,
                f"{desc}: new allocation content not as expected",
                expected=s,
                actual=content,
            )

    print_exercise_result("ex00/ft_strdup.c", passed_count, total_count)

    if os.path.exists(exe_path):
        os.remove(exe_path)

    return passed_count == total_count
