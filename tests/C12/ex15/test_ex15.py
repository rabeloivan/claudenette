import os

from utils.compiler import compile_source
from utils.runner import run_test_case
from utils.ui import (
    print_command_execution,
    print_exercise_result,
    print_test_fail,
    print_test_pass,
)

C12_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HARNESS_UTILS = os.path.join(C12_DIR, "harness_utils.c")


def parse_pairs(s):
    if s == "":
        return []
    pairs = []
    for item in s.split(","):
        addr, data = item.split(":")
        pairs.append((addr, int(data)))
    return pairs


def run_C12_ex15(student_file):
    test_dir = os.path.dirname(os.path.abspath(__file__))
    harness_path = os.path.join(test_dir, "ex15_harness.c")
    student_dir = os.path.dirname(student_file)
    exe_path = "./list_reverse_fun"

    flags = ["-Wall", "-Wextra", "-Werror", "-I", student_dir]
    if not compile_source(
        [student_file, harness_path, HARNESS_UTILS], exe_path, flags=flags
    ):
        return False

    print_command_execution(exe_path)

    # begin_list is `t_list *`, not `t_list **` - the caller's own pointer
    # variable can't be reseated, so the only way for the caller to observe
    # the reversal (by walking from that same original pointer afterward) is
    # for the implementation to swap .data between paired nodes in place,
    # never relink ->next. We verify both halves of that constraint: the
    # node addresses seen from the original head are unchanged (no
    # relinking), while the data at each position is reversed.
    test_cases = [
        [],
        [1],
        [1, 2],
        [1, 2, 3],
        [1, 2, 3, 4, 5],
    ]

    passed_count = 0
    total_count = len(test_cases)

    for i, tab in enumerate(test_cases, 1):
        input_str = f"{len(tab)}\n" + ",".join(str(x) for x in tab)
        actual, err, code = run_test_case(exe_path, input_data=input_str)
        desc = f"ft_list_reverse_fun(list of {tab})"

        parts = actual.split("\n", 1)
        if len(parts) != 2:
            print_test_fail(i, f"{desc}: malformed output", actual=actual)
            continue

        before = parse_pairs(parts[0])
        after = parse_pairs(parts[1])
        before_addrs = [a for a, _ in before]
        after_addrs = [a for a, _ in after]
        before_data = [d for _, d in before]
        after_data = [d for _, d in after]
        expected_data = list(reversed(before_data))

        if after_addrs == before_addrs and after_data == expected_data:
            print_test_pass(i, f"{desc}: values reversed in place, node addresses unchanged")
            passed_count += 1
        elif after_addrs != before_addrs:
            print_test_fail(
                i,
                f"{desc}: node addresses/links changed (expected data swapped in place, not relinked)",
                expected=before_addrs,
                actual=after_addrs,
            )
        else:
            print_test_fail(i, f"{desc}: data not reversed", expected=expected_data, actual=after_data)

    print_exercise_result("ex15/ft_list_reverse_fun.c", passed_count, total_count)

    if os.path.exists(exe_path):
        os.remove(exe_path)

    return passed_count == total_count
