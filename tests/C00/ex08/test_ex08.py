import os
from itertools import combinations

from utils.compiler import compile_source
from utils.runner import run_test_case
from utils.ui import (
    print_command_execution,
    print_exercise_result,
    print_test_fail,
    print_test_pass,
)


DIGIT_WORDS = ["one", "two", "three", "four", "five", "six", "seven", "eight", "nine"]


def generate_combn_output(n):
    combos = combinations(range(10), n)
    formatted_list = ["".join(map(str, c)) for c in combos]
    return ", ".join(formatted_list)


def run_C00_ex08(student_file):
    test_dir = os.path.dirname(os.path.abspath(__file__))
    harness_path = os.path.join(test_dir, "ex08_harness.c")
    exe_path = "./print_combn"

    if not compile_source([student_file, harness_path], exe_path):
        return False

    print_command_execution(exe_path)

    test_cases = [1, 2, 3, 4, 5, 6, 7, 8, 9]
    passed_count = 0
    total_count = len(test_cases)

    for i, n in enumerate(test_cases, 1):
        expected = generate_combn_output(n)
        actual, err, code = run_test_case(exe_path, input_data=str(n))
        desc = f"ft_print_combn(n={n})"

        if actual == expected:
            # The combination list itself grows too large to read past a
            # handful of digits (n=9 alone is 10 entries), so every case
            # uses the same general phrasing rather than dumping it only
            # once it gets long - consistent wording across the whole set
            # beats switching styles partway through.
            word = DIGIT_WORDS[n - 1]
            plural = "digit" if n == 1 else "digits"
            print_test_pass(
                i,
                f"{desc}: output all unique combinations of {word} {plural} "
                "as expected",
            )
            passed_count += 1
        else:
            print_test_fail(
                i, f"{desc}: output not as expected", expected=expected, actual=actual
            )

    print_exercise_result("ex08/ft_print_combn.c", passed_count, total_count)

    if os.path.exists(exe_path):
        os.remove(exe_path)

    return passed_count == total_count
