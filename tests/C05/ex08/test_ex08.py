import os

from utils.compiler import compile_source
from utils.runner import run_test_case
from utils.ui import (
    print_command_execution,
    print_exercise_result,
    print_test_fail,
    print_test_pass,
)

N = 10
EXPECTED_COUNT = 724


def solve_n_queens(n):
    solutions = []
    cols = [-1] * n

    def backtrack(col):
        if col == n:
            solutions.append("".join(str(r) for r in cols))
            return
        for row in range(n):
            ok = True
            for prev_col in range(col):
                prev_row = cols[prev_col]
                if prev_row == row or abs(prev_row - row) == abs(prev_col - col):
                    ok = False
                    break
            if ok:
                cols[col] = row
                backtrack(col + 1)
        cols[col] = -1

    backtrack(0)
    return solutions


def run_C05_ex08(student_file):
    test_dir = os.path.dirname(os.path.abspath(__file__))
    harness_path = os.path.join(test_dir, "ex08_harness.c")
    exe_path = "./ten_queens_puzzle"

    if not compile_source([student_file, harness_path], exe_path):
        return False

    print_command_execution(exe_path)

    expected_solutions = set(solve_n_queens(N))

    actual, err, code = run_test_case(exe_path, input_data="", timeout=15)

    parts = actual.rsplit("|", 1)
    if len(parts) != 2:
        print_test_fail(
            1, "ft_ten_queens_puzzle(): produced unparseable output", actual=actual
        )
        print_exercise_result("ex08/ft_ten_queens_puzzle.c", 0, 1)
        if os.path.exists(exe_path):
            os.remove(exe_path)
        return False

    solutions_text, count_text = parts
    try:
        count = int(count_text)
    except ValueError:
        count = None

    lines = solutions_text.split("\n")
    if lines and lines[-1] == "":
        lines = lines[:-1]

    actual_solutions = set(lines)
    count_ok = count == EXPECTED_COUNT
    no_dupes = len(lines) == len(actual_solutions)
    solutions_ok = actual_solutions == expected_solutions
    passed = count_ok and no_dupes and solutions_ok

    if passed:
        print_test_pass(
            1, f"ft_ten_queens_puzzle(): all {EXPECTED_COUNT} solutions as expected"
        )
    else:
        missing = expected_solutions - actual_solutions
        extra = actual_solutions - expected_solutions
        detail = []
        if not count_ok:
            detail.append("return value not as expected")
        if not no_dupes:
            detail.append(
                f"{len(lines) - len(actual_solutions)} duplicate solution line(s)"
            )
        if missing:
            detail.append(
                f"missing {len(missing)} valid solution(s), e.g. {sorted(missing)[:3]}"
            )
        if extra:
            detail.append(
                f"{len(extra)} invalid/non-solution line(s), e.g. {sorted(extra)[:3]}"
            )
        print_test_fail(
            1,
            "ft_ten_queens_puzzle(): " + "; ".join(detail),
            expected=EXPECTED_COUNT if not count_ok else None,
            actual=count if not count_ok else None,
        )

    print_exercise_result("ex08/ft_ten_queens_puzzle.c", 1 if passed else 0, 1)

    if os.path.exists(exe_path):
        os.remove(exe_path)

    return passed
