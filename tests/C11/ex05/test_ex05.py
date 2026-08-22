import glob
import os
import subprocess

from utils.functions import check_allowed_functions
from utils.norminette import check_norminette
from utils.runner import run_test_case
from utils.ui import (
    display_str,
    print_command_execution,
    print_exercise_result,
    print_test_fail,
    print_test_pass,
)

WHITESPACE = (" ", "\t", "\n", "\v", "\f", "\r")
BINARY = "do-op"


def parse_value(s):
    i = 0
    n = len(s)
    while i < n and s[i] in WHITESPACE:
        i += 1
    neg = False
    while i < n and s[i] in ("+", "-"):
        if s[i] == "-":
            neg = not neg
        i += 1
    value = 0
    while i < n and s[i].isdigit():
        value = value * 10 + int(s[i])
        i += 1
    return -value if neg else value


def expected_do_op(v1_str, op, v2_str):
    if op not in ("+", "-", "*", "/", "%"):
        return "0\n"
    v1 = parse_value(v1_str)
    v2 = parse_value(v2_str)
    if op == "+":
        return f"{v1 + v2}\n"
    if op == "-":
        return f"{v1 - v2}\n"
    if op == "*":
        return f"{v1 * v2}\n"
    if op == "/":
        if v2 == 0:
            return "Stop : division by zero\n"
        result = abs(v1) // abs(v2)
        if (v1 < 0) != (v2 < 0):
            result = -result
        return f"{result}\n"
    if v2 == 0:
        return "Stop : modulo by zero\n"
    result = abs(v1) % abs(v2)
    if v1 < 0:
        result = -result
    return f"{result}\n"


def run_C11_ex05(student_file):
    student_dir = os.path.dirname(student_file)

    c_files = sorted(glob.glob(os.path.join(student_dir, "*.c")))
    checks_ok = bool(c_files) and all(
        check_norminette(path) and check_allowed_functions(path, ["write"])
        for path in c_files
    )

    print_command_execution("make")
    try:
        build_result = subprocess.run(
            ["make"], cwd=student_dir, capture_output=True, text=True, timeout=30
        )
    except subprocess.TimeoutExpired:
        build_result = None

    binary_path = os.path.join(student_dir, BINARY)
    if build_result is None or not os.path.exists(binary_path):
        stderr = build_result.stderr if build_result else "TIMEOUT"
        print_test_fail(1, f"`make` did not produce {BINARY} (stderr: {display_str(stderr)})")
        print_exercise_result("ex05/do-op", 0, 1)
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

    invalid_argc_cases = [[], ["1"], ["1", "+"], ["1", "+", "1", "1"]]
    for args in invalid_argc_cases:
        actual, err, code = run_test_case(binary_path, input_data="", args=args)
        check(
            actual == "" and err == "",
            f"do-op with {len(args)} argument(s) (invalid count): no output",
            expected="",
            actual=actual,
        )

    op_cases = [
        ("1", "+", "1"),
        ("42amis", "-", "--+-20toto12"),
        ("1", "p", "1"),
        ("1", "+", "toto3"),
        ("toto3", "+", "4"),
        ("foo", "plus", "bar"),
        ("25", "/", "0"),
        ("25", "%", "0"),
        ("5", "*", "6"),
        ("10", "-", "3"),
        ("+5", "+", "-3"),
        ("10", "+x", "5"),
        ("-7", "/", "2"),
        ("-7", "%", "2"),
    ]

    for v1, op, v2 in op_cases:
        expected = expected_do_op(v1, op, v2)
        actual, err, code = run_test_case(binary_path, input_data="", args=[v1, op, v2])
        desc = f"do-op {display_str(v1)} {display_str(op)} {display_str(v2)}"
        check(
            actual == expected,
            f"{desc}: output",
            expected=expected,
            actual=actual,
            show_value=actual,
        )

    print_exercise_result("ex05/do-op", passed_count, total_count)

    subprocess.run(["make", "fclean"], cwd=student_dir, capture_output=True, timeout=30)
    if os.path.exists(binary_path):
        os.remove(binary_path)
    for name in os.listdir(student_dir):
        if name.endswith(".o"):
            os.remove(os.path.join(student_dir, name))

    return passed_count == total_count and checks_ok
