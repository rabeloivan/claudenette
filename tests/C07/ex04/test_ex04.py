import os

from utils.compiler import compile_source
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


def is_valid_base(base):
    if len(base) < 2:
        return False
    if len(set(base)) != len(base):
        return False
    if "+" in base or "-" in base:
        return False
    if any(c in WHITESPACE for c in base):
        return False
    return True


def parse_atoi_base(s, base):
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
    while i < n and s[i] in base:
        value = value * len(base) + base.index(s[i])
        i += 1
    return -value if neg else value


def format_putnbr_base(nbr, base):
    base_len = len(base)
    neg = nbr < 0
    mag = -nbr if neg else nbr
    if mag == 0:
        digits = base[0]
    else:
        digits = ""
        m = mag
        while m > 0:
            digits = base[m % base_len] + digits
            m //= base_len
    return ("-" if neg else "") + digits


def expected_convert_base(nbr, base_from, base_to):
    if not is_valid_base(base_from) or not is_valid_base(base_to):
        return None
    value = parse_atoi_base(nbr, base_from)
    return format_putnbr_base(value, base_to)


def run_C07_ex04(student_file):
    test_dir = os.path.dirname(os.path.abspath(__file__))
    harness_path = os.path.join(test_dir, "ex04_harness.c")
    exe_path = "./convert_base"

    second_file = os.path.join(os.path.dirname(student_file), "ft_convert_base2.c")
    if not os.path.exists(second_file):
        print()
        print_test_fail(
            1,
            "ft_convert_base2.c not found next to "
            f"{os.path.basename(student_file)} (this exercise must be turned in as "
            "two files)",
        )
        print_exercise_result("ex04/ft_convert_base.c", 0, 1)
        return False

    norm_ok_2 = check_norminette(second_file)
    allowed_ok_2 = check_allowed_functions(second_file, ["malloc", "free"])

    if not compile_source([student_file, second_file, harness_path], exe_path):
        return False

    print_command_execution(exe_path)

    test_cases = [
        ("42", "0123456789", "0123456789"),
        ("1010", "01", "0123456789"),
        ("10", "0123456789", "01"),
        ("FF", "0123456789ABCDEF", "0123456789"),
        ("-42", "0123456789", "0123456789"),
        ("--42", "0123456789", "0123456789"),
        ("  42", "0123456789", "0123456789"),
        ("0", "0123456789", "0123456789"),
        ("2147483647", "0123456789", "0123456789ABCDEF"),
        ("-2147483647", "0123456789", "0123456789ABCDEF"),
        ("101", "01", "poneyvif"),
        ("42", "0", "0123456789"),
        ("42", "0123456789", ""),
        ("5", "0123 56789", "0123456789"),
        ("5", "0123456789", "0123 56789"),
    ]

    passed_count = 0
    total_count = len(test_cases)

    for i, (nbr, base_from, base_to) in enumerate(test_cases, 1):
        expected = expected_convert_base(nbr, base_from, base_to)
        input_str = f"{len(nbr)}\n{len(base_from)}\n{nbr}{base_from}{base_to}"
        actual, err, code = run_test_case(exe_path, input_data=input_str)
        desc = (
            f"ft_convert_base(nbr={display_str(nbr)}, base_from={display_str(base_from)}, "
            f"base_to={display_str(base_to)})"
        )

        if expected is None:
            if actual == "N":
                print_test_pass(i, f"{desc}: returned NULL as expected")
                passed_count += 1
            else:
                print_test_fail(
                    i, f"{desc}: did not return NULL", expected="NULL", actual=actual
                )
            continue

        if actual.startswith("A") and actual[1:] == expected:
            print_test_pass(i, f"{desc}: returned {display_str(expected)} as expected")
            passed_count += 1
        else:
            got = actual[1:] if actual.startswith("A") else "NULL"
            print_test_fail(
                i,
                f"{desc}: returned value not as expected",
                expected=expected,
                actual=got,
            )

    print_exercise_result("ex04/ft_convert_base.c", passed_count, total_count)

    if os.path.exists(exe_path):
        os.remove(exe_path)

    return passed_count == total_count and norm_ok_2 and allowed_ok_2
