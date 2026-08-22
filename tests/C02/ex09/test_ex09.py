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


def _is_alnum_ascii(c):
    return ("a" <= c <= "z") or ("A" <= c <= "Z") or ("0" <= c <= "9")


def _is_alpha_ascii(c):
    return ("a" <= c <= "z") or ("A" <= c <= "Z")


def expected_capitalize(s):
    result = []
    prev_alnum = False
    for c in s:
        alnum = _is_alnum_ascii(c)
        if alnum and not prev_alnum and _is_alpha_ascii(c):
            result.append(c.upper())
        elif alnum and _is_alpha_ascii(c):
            result.append(c.lower())
        else:
            result.append(c)
        prev_alnum = alnum
    return "".join(result)


def run_C02_ex09(student_file):
    test_dir = os.path.dirname(os.path.abspath(__file__))
    harness_path = os.path.join(test_dir, "ex09_harness.c")
    exe_path = "./strcapitalize"

    if not compile_source([student_file, harness_path], exe_path):
        return False

    print_command_execution(exe_path)

    test_cases = [
        "",
        "hi, how are you? 42words forty-two; fifty+and+one",
        "hello world",
        "HELLO WORLD",
        "  leading spaces",
        "already Capitalized Text",
        "!!!",
        "a",
        "a b c",
    ]

    passed_count = 0
    total_count = len(test_cases)

    for i, s in enumerate(test_cases, 1):
        expected = expected_capitalize(s)
        actual, err, code = run_test_case(exe_path, input_data=s)
        desc = f"ft_strcapitalize(str={display_str(s)})"

        marker = actual[0] if actual else ""
        content = actual[1:]
        ptr_ok = marker == "1"

        if ptr_ok and content == expected:
            print_test_pass(
                i, f"{desc}: return value and content {display_str(content)} as expected"
            )
            passed_count += 1
        elif not ptr_ok:
            print_test_fail(i, f"{desc}: did not return str (return value mismatch)")
        else:
            print_test_fail(
                i, f"{desc}: content not as expected", expected=expected, actual=content
            )

    print_exercise_result("ex09/ft_strcapitalize.c", passed_count, total_count)

    if os.path.exists(exe_path):
        os.remove(exe_path)

    return passed_count == total_count
