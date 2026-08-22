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


def expected_non_printable(s):
    result = []
    for c in s:
        code = ord(c)
        if 0x20 <= code <= 0x7E:
            result.append(c)
        else:
            result.append(f"\\{code:02x}")
    return "".join(result)


def run_C02_ex11(student_file):
    test_dir = os.path.dirname(os.path.abspath(__file__))
    harness_path = os.path.join(test_dir, "ex11_harness.c")
    exe_path = "./putstr_non_printable"

    if not compile_source([student_file, harness_path], exe_path):
        return False

    print_command_execution(exe_path)

    test_cases = [
        "",
        "Hello\nHow are you?",
        "hello world",
        "\t\n\x1f\x7f",
        "tab\tnewline\n",
        "\x01\x02\x03",
        chr(0x80) + chr(0xFF),
        "x" * 200,
    ]

    passed_count = 0
    total_count = len(test_cases)

    for i, s in enumerate(test_cases, 1):
        expected = expected_non_printable(s)
        actual, err, code = run_test_case(exe_path, input_data=s)
        desc = f"ft_putstr_non_printable(str={display_str(s)})"

        if actual == expected:
            print_test_pass(i, f"{desc}: output {display_str(actual)} as expected")
            passed_count += 1
        else:
            print_test_fail(
                i, f"{desc}: output not as expected", expected=expected, actual=actual
            )

    print_exercise_result("ex11/ft_putstr_non_printable.c", passed_count, total_count)

    if os.path.exists(exe_path):
        os.remove(exe_path)

    return passed_count == total_count
