import os

from utils.compiler import compile_source
from utils.runner import run_test_case
from utils.ui import (
    print_command_execution,
    print_exercise_result,
    print_test_fail,
    print_test_pass,
)


def expected_power(nb, power):
    if power < 0:
        return 0
    result = 1
    for _ in range(power):
        result *= nb
    return result


def run_C05_ex02(student_file):
    test_dir = os.path.dirname(os.path.abspath(__file__))
    harness_path = os.path.join(test_dir, "ex02_harness.c")
    exe_path = "./iterative_power"

    if not compile_source([student_file, harness_path], exe_path):
        return False

    print_command_execution(exe_path)

    test_cases = [
        (2, 10),
        (3, 4),
        (5, 0),
        (0, 0),
        (0, 5),
        (-2, 3),
        (-2, 4),
        (1, 100),
        (10, -3),
        (2, -1),
        (7, 3),
    ]

    passed_count = 0
    total_count = len(test_cases)

    for i, (nb, power) in enumerate(test_cases, 1):
        expected = expected_power(nb, power)
        input_str = f"{nb}\n{power}"
        actual, err, code = run_test_case(exe_path, input_data=input_str)
        desc = f"ft_iterative_power(nb={nb}, power={power})"

        try:
            actual_val = int(actual)
        except ValueError:
            actual_val = None

        if actual_val == expected:
            print_test_pass(i, f"{desc}: returned {actual_val} as expected")
            passed_count += 1
        else:
            print_test_fail(
                i,
                f"{desc}: returned value not as expected",
                expected=expected,
                actual=actual_val,
            )

    print_exercise_result("ex02/ft_iterative_power.c", passed_count, total_count)

    if os.path.exists(exe_path):
        os.remove(exe_path)

    return passed_count == total_count
