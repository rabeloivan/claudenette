import glob
import os

from utils.compiler import compile_source
from utils.functions import check_allowed_functions
from utils.runner import run_test_case
from utils.ui import (
    print_command_execution,
    print_exercise_result,
    print_test_fail,
    print_test_pass,
)

from ..skyscraper import is_valid_solution, parse_grid, wire

# (clues, valid) - "valid" clue sets are checked by verifying the program's
# own output satisfies every constraint (Latin square + all 16 visibility
# clues), not by exact-match against one specific grid: the subject only
# requires "the first solution you encounter", and clue sets can have more
# than one valid solution, so a compliant solver using a different search
# order may legitimately produce a different (but equally valid) grid.
VALID_CASES = [
    [4, 3, 2, 1, 1, 2, 2, 2, 4, 3, 2, 1, 1, 2, 2, 2],
    [2, 2, 1, 4, 2, 2, 4, 1, 2, 2, 1, 3, 2, 3, 2, 1],
    [1, 2, 3, 2, 3, 1, 2, 3, 1, 2, 3, 2, 3, 1, 2, 3],
    [2, 1, 2, 3, 3, 2, 2, 1, 2, 1, 2, 3, 3, 2, 2, 1],
]

# Well-formatted (16 digits, each 1-4) but no grid can satisfy these
# clues simultaneously - confirmed via exhaustive search, not guessed.
UNSOLVABLE_CASE = [1, 3, 2, 1, 1, 2, 2, 2, 4, 3, 2, 1, 1, 2, 2, 2]

# Bonus: "you may try to handle other map sizes (up to 9x9)". The subject
# gives no separate invocation convention for a non-4x4 size - the
# mandatory format already infers N purely from the clue count (16 = 4*4),
# so the only spec-consistent way to invoke a bonus NxN case is the same
# single-quoted-argv-string format with 4*N numbers, letting the student's
# own program infer N the same way it must already infer 4. A judgment
# call, documented rather than silently assumed, since the subject's bonus
# mention gives no worked example to confirm against. Each clue set comes
# from an NxN grid where row r is a cyclic shift ((r+c) % n + 1 for c in
# range(n)) - computed via skyscraper.py's own n-parameterized
# solve()/compute_clues() (already fully generic, no changes needed there)
# and confirmed valid via is_valid_solution before being hardcoded here.
# This specific structure isn't incidental: a first pass using clues from a
# randomly shuffled NxN grid took over 15s to solve at 7x7 even against a
# scratch reference with real row/column incremental pruning (a naive
# backtracking search's runtime is highly instance-dependent at this size,
# not just a function of N) - the subject states no performance
# requirement for the bonus, so picking clues this constraining (a top
# clue of N pins that entire column immediately) keeps the check testing
# "does it handle bigger N correctly" without accidentally penalizing a
# correct-but-not-heavily-optimized bonus attempt with a needlessly hard
# search instance. Verified by satisfying every clue, not exact-match,
# same reasoning as the mandatory VALID_CASES above (the subject only ever
# requires "the first solution you encounter").
BONUS_CASES = [
    (5, [5, 4, 3, 2, 1, 1, 2, 2, 2, 2, 5, 4, 3, 2, 1, 1, 2, 2, 2, 2]),
    (7, [7, 6, 5, 4, 3, 2, 1, 1, 2, 2, 2, 2, 2, 2, 7, 6, 5, 4, 3, 2, 1, 1, 2, 2, 2, 2, 2, 2]),
    (
        9,
        [
            9, 8, 7, 6, 5, 4, 3, 2, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2,
            9, 8, 7, 6, 5, 4, 3, 2, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2,
        ],
    ),
]

# (description, argv list) - each must produce exactly "Error\n".
ERROR_CASES = [
    ("no arguments", []),
    ("two separate argv words instead of one", ["4 3 2 1 1 2 2 2", "4 3 2 1 1 2 2 2"]),
    ("15 numbers instead of 16", "4 3 2 1 1 2 2 2 4 3 2 1 1 2 2"),
    ("17 numbers instead of 16", "4 3 2 1 1 2 2 2 4 3 2 1 1 2 2 2 1"),
    ("digit 0 (out of 1-4 range)", "0 3 2 1 1 2 2 2 4 3 2 1 1 2 2 2"),
    ("digit 5 (out of 1-4 range)", "5 3 2 1 1 2 2 2 4 3 2 1 1 2 2 2"),
    ("non-numeric characters", "a 3 2 1 1 2 2 2 4 3 2 1 1 2 2 2"),
]


def run_C_rush01(student_dir):
    # student_dir is "ex00" itself (the directory), not a file inside it -
    # "Files to turn in: All the necessary files (*.c)" gives no fixed
    # filename to key the mapping off. main.py's automatic norminette
    # pre-check already recurses correctly over a directory path (verified
    # empirically); check_allowed_functions does not (a directory can't be
    # compiled with cc -c, so it silently vacuous-passes) - so every
    # discovered file is checked manually here instead.
    c_files = sorted(glob.glob(os.path.join(student_dir, "*.c")))

    if not c_files:
        print_test_fail(1, "no .c files found in ex00/")
        print_exercise_result("ex00/*.c", 0, 1)
        return False

    fn_ok = True
    for f in c_files:
        fn_ok = check_allowed_functions(f, ["write", "malloc", "free"]) and fn_ok

    exe_path = "./rush01"
    # Matches the subject's own exact compile invocation:
    # cc -Wall -Wextra -Werror -o rush01 *.c
    compiled = compile_source(
        c_files, exe_path, flags=["-Wall", "-Wextra", "-Werror"]
    )
    if not compiled:
        print_exercise_result("ex00/*.c", 0, 1)
        return False

    print_command_execution(f'{exe_path} "<16 clues>"')

    passed_count = 0
    total_count = len(VALID_CASES) + 1 + len(ERROR_CASES)
    i = 0

    for clues in VALID_CASES:
        i += 1
        actual, err, code = run_test_case(exe_path, args=[wire(clues)])
        desc = f"rush01({wire(clues)})"
        grid = parse_grid(actual)
        if grid is not None and is_valid_solution(grid, clues):
            print_test_pass(i, f"{desc}: grid satisfies every clue")
            passed_count += 1
        else:
            print_test_fail(
                i, f"{desc}: not a valid solution", expected="a grid satisfying every clue", actual=actual
            )

    i += 1
    actual, err, code = run_test_case(exe_path, args=[wire(UNSOLVABLE_CASE)])
    desc = f"rush01({wire(UNSOLVABLE_CASE)}) [unsolvable]"
    if actual == "Error\n":
        print_test_pass(i, f"{desc}: reports Error as expected")
        passed_count += 1
    else:
        print_test_fail(i, f"{desc}: output not as expected", expected="Error\n", actual=actual)

    for label, args in ERROR_CASES:
        i += 1
        arg_list = args if isinstance(args, list) else [args]
        actual, err, code = run_test_case(exe_path, args=arg_list)
        desc = f"rush01 with {label}"
        if actual == "Error\n":
            print_test_pass(i, f"{desc}: reports Error as expected")
            passed_count += 1
        else:
            print_test_fail(i, f"{desc}: output not as expected", expected="Error\n", actual=actual)

    print_exercise_result("ex00/*.c", passed_count, total_count)

    # Bonus is entirely separate from the mandatory score above and from
    # this function's return value: the subject only ever says a failed
    # *mandatory* case zeroes a working bonus ("if a bonus works but the
    # mandatory one fails the tests, you will receive a score of 0"), never
    # the reverse - so a broken or unattempted bonus must not cost the
    # exercise its mandatory OK. bonus_passed/bonus_total are tracked and
    # reported on their own print_exercise_result line and never touch
    # passed_count/total_count.
    bonus_passed = 0
    bonus_total = len(BONUS_CASES)
    j = 0
    for n, clues in BONUS_CASES:
        j += 1
        actual, err, code = run_test_case(exe_path, args=[wire(clues)], timeout=10)
        desc = f"[BONUS {n}x{n}] rush01({wire(clues)})"
        grid = parse_grid(actual)
        if grid is not None and is_valid_solution(grid, clues, n=n):
            print_test_pass(j, f"{desc}: grid satisfies every clue")
            bonus_passed += 1
        else:
            print_test_fail(
                j,
                f"{desc}: not a valid solution",
                expected=f"a {n}x{n} grid satisfying every clue",
                actual=actual,
            )
    print_exercise_result("ex00/*.c [bonus: other map sizes]", bonus_passed, bonus_total)

    if os.path.exists(exe_path):
        os.remove(exe_path)

    return passed_count == total_count and fn_ok
