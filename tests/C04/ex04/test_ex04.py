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


def is_valid_base(base):
    if len(base) < 2:
        return False
    if len(set(base)) != len(base):
        return False
    if "+" in base or "-" in base:
        return False
    return True


def expected_putnbr_base(nbr, base):
    if not is_valid_base(base):
        return ""
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


def run_C04_ex04(student_file):
    test_dir = os.path.dirname(os.path.abspath(__file__))
    harness_path = os.path.join(test_dir, "ex04_harness.c")
    exe_path = "./putnbr_base"

    if not compile_source([student_file, harness_path], exe_path):
        return False

    print_command_execution(exe_path)

    test_cases = [
        (42, "0123456789"),
        (-42, "0123456789"),
        (0, "0123456789"),
        (10, "01"),
        (255, "0123456789ABCDEF"),
        (8, "poneyvif"),
        (-2147483648, "0123456789"),
        (2147483647, "0123456789"),
        (5, ""),
        (5, "0"),
        (5, "00"),
        (5, "0+23456789"),
        (5, "0-23456789"),
    ]

    passed_count = 0
    total_count = len(test_cases)

    for i, (nbr, base) in enumerate(test_cases, 1):
        expected = expected_putnbr_base(nbr, base)
        input_str = f"{nbr}\n{len(base)}\n{base}"
        actual, err, code = run_test_case(exe_path, input_data=input_str)
        desc = f"ft_putnbr_base(nbr={nbr}, base={display_str(base)})"

        if actual == expected:
            print_test_pass(i, f"{desc}: output {display_str(actual)} as expected")
            passed_count += 1
        else:
            print_test_fail(
                i,
                f"{desc}: output not as expected",
                expected=expected or "(nothing)",
                actual=actual or "(nothing)",
            )

    print_exercise_result("ex04/ft_putnbr_base.c", passed_count, total_count)

    if os.path.exists(exe_path):
        os.remove(exe_path)

    return passed_count == total_count
