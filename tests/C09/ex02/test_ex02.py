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


def expected_split(s, charset):
    result = []
    current = []
    for c in s:
        if c in charset:
            if current:
                result.append("".join(current))
                current = []
        else:
            current.append(c)
    if current:
        result.append("".join(current))
    return result


def run_C09_ex02(student_file):
    test_dir = os.path.dirname(os.path.abspath(__file__))
    harness_path = os.path.join(test_dir, "ex02_harness.c")
    exe_path = "./split"

    if not compile_source([student_file, harness_path], exe_path):
        return False

    print_command_execution(exe_path)

    test_cases = [
        ("hello world foo", " "),
        ("a,b,,c", ","),
        (",,,", ","),
        ("", " "),
        ("hello", ""),
        ("  hello  ", " "),
        ("a.b,c;d", ".,;"),
        ("single", "xyz"),
        ("42 is the answer", " "),
    ]

    passed_count = 0
    total_count = len(test_cases)

    for i, (s, charset) in enumerate(test_cases, 1):
        expected = expected_split(s, charset)
        input_str = f"{len(s)}\n{s}{charset}"
        actual, err, code = run_test_case(exe_path, input_data=input_str)
        desc = f"ft_split(str={display_str(s)}, charset={display_str(charset)})"

        if not actual.startswith("A"):
            print_test_fail(
                i, f"{desc}: returned NULL", expected=expected, actual="NULL"
            )
            continue

        content = actual[1:]
        actual_tokens = content.split("\x01") if content else []

        if actual_tokens == expected:
            print_test_pass(i, f"{desc}: returned array {actual_tokens} as expected")
            passed_count += 1
        else:
            print_test_fail(
                i,
                f"{desc}: returned array not as expected",
                expected=expected,
                actual=actual_tokens,
            )

    print_exercise_result("ex02/ft_split.c", passed_count, total_count)

    if os.path.exists(exe_path):
        os.remove(exe_path)

    return passed_count == total_count
