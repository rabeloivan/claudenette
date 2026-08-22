import glob
import os
import shutil
import subprocess
import tempfile

from utils.functions import check_allowed_functions
from utils.runner import run_test_case
from utils.ui import (
    display_str,
    print_command_execution,
    print_exercise_result,
    print_test_fail,
    print_test_pass,
)

from ..bsq_solver import solve_map

ALLOWED = ["open", "close", "read", "write", "malloc", "free", "exit"]


def _grid_map(rows, cols, empty_c, obstacle_c, full_c, is_obstacle):
    # Builds a well-formed map string from a per-cell predicate, for maps too
    # large/regular to spell out as a literal - used by the eval-sheet-scale
    # Feature Test cases below (Test 04 onward).
    header = f"{rows}{empty_c}{obstacle_c}{full_c}\n"
    body = "\n".join(
        "".join(obstacle_c if is_obstacle(r, c) else empty_c for c in range(cols))
        for r in range(rows)
    )
    return header + body + "\n"


def _two_block_map(rows, cols, block_size, block_a, block_b):
    # A grid that's all-obstacle except for two disjoint block_size x
    # block_size empty squares - guarantees exactly two, equally-sized
    # candidate solutions so a passing test genuinely exercises the
    # topmost-then-leftmost tie-break, not just "find the biggest".
    ar, ac = block_a
    br, bc = block_b

    def is_obstacle(r, c):
        in_a = ar <= r < ar + block_size and ac <= c < ac + block_size
        in_b = br <= r < br + block_size and bc <= c < bc + block_size
        return not (in_a or in_b)

    return _grid_map(rows, cols, ".", "o", "x", is_obstacle)


# (label, map text) - all expected to solve() to a real grid (not "map error").
VALID_MAPS = {
    "subject's own worked example": (
        "9.ox\n"
        "...........................\n"
        "....o......................\n"
        "............o..............\n"
        "...........................\n"
        "....o......................\n"
        "...............o...........\n"
        "...........................\n"
        "......o..............o.....\n"
        "..o.......o................\n"
    ),
    "1x1 single empty cell": "1.ox\n.\n",
    "all-obstacle (no square to draw)": "3.ox\nooo\nooo\nooo\n",
    "single row": "1.ox\n........\n",
    "single column": "4.ox\n.\n.\n.\n.\n",
    "empty char is a space": "3 ox\n   \n o \n   \n",
    "full char is a digit (last-3-chars parsing trap)": "3.o5\n...\n.o.\n...\n",
    "obstacle char is a digit": "3.5x\n...\n.5.\n...\n",
    "empty char is a digit adjacent to the count (front-scan parsing trap)": (
        "25ox\n55\n5o\n"
    ),
    "random 8x10, sparse": (
        "8.ox\n"
        "..........\n"
        "..o.......\n"
        "..........\n"
        "......o...\n"
        "..........\n"
        "..........\n"
        ".o........\n"
        "..........\n"
    ),

    # --- Mirrors the "Feature Tests" (Test 00-Test 10) from bsq's defense
    # evaluation sheet - Test 00 is already covered above by "1x1 single
    # empty cell".
    "eval sheet Test 01: 1x1 map that cannot be filled": "1.ox\no\n",
    "eval sheet Test 02: 5x5 map": _grid_map(
        5, 5, ".", "o", "x", lambda r, c: (r, c) in {(0, 4), (2, 2), (4, 0)}
    ),
    "eval sheet Test 03: 8x8 chessboard (tie-break must pick topmost, then leftmost)": (
        _grid_map(8, 8, ".", "o", "x", lambda r, c: (r + c) % 2 == 0)
    ),
    "eval sheet Test 04: 10x10 map": _grid_map(
        10, 10, ".", "o", "x", lambda r, c: (r * 3 + c * 5) % 11 == 0
    ),
    "eval sheet Test 05: 10x10 map with non-default special characters (digits)": (
        _grid_map(10, 10, "1", "2", "3", lambda r, c: (r * 3 + c * 5) % 11 == 0)
    ),
    "eval sheet Test 06: non-square 150x100 map": _grid_map(
        100, 150, ".", "o", "x", lambda r, c: (r * 7 + c * 13) % 23 == 0
    ),
    "eval sheet Test 07: empty 100x100 map": _grid_map(
        100, 100, ".", "o", "x", lambda r, c: False
    ),
    "eval sheet Test 08: 100x100 map with obstacles": _grid_map(
        100, 100, ".", "o", "x", lambda r, c: (r * 7 + c * 13) % 23 == 0
    ),
    "eval sheet Test 09: 100x100 with two equal-size (6x6) solutions, topmost-leftmost wins": (
        _two_block_map(100, 100, 6, (10, 10), (60, 60))
    ),
    "eval sheet Test 10: 1000x1000 map": _grid_map(
        1000, 1000, ".", "o", "x", lambda r, c: (r * 31 + c * 17) % 97 == 0
    ),
}

# (label, map text) - all expected to produce exactly "map error\n".
ERROR_MAPS = {
    "first line too short": "ox\n",
    "only 2 distinct special chars": "3.o.\n...\n...\n...\n",
    "non-digit count prefix": "a.ox\n...\n",
    "zero line count": "0.ox\n",
    "inconsistent line widths": "2.ox\n...\n..\n",
    "wrong body line count (too few)": "3.ox\n..\n..\n",
    "wrong body line count (too many)": "2.ox\n..\n..\n..\n",
    "unrecognized character in body": "2.ox\n.z\n..\n",
    # A pre-existing "full" character in the *input* body (e.g. hand-edited
    # into a generated map with vim) must be rejected, not silently treated
    # as if it were just another obstacle - the subject says the body is
    # made of "empty" and "obstacle" characters only; "full" is output-only.
    "full character already present in body": "3.ox\n.x.\n...\no..\n",
    "a body line with zero cells": "1.ox\n\n",
}


def build_in_scratch(student_dir):
    scratch = tempfile.mkdtemp(prefix="claudenette_bsq_")
    for name in os.listdir(student_dir):
        src = os.path.join(student_dir, name)
        dst = os.path.join(scratch, name)
        if os.path.isdir(src):
            shutil.copytree(src, dst)
        else:
            shutil.copy(src, dst)
    result = subprocess.run(
        ["make"], cwd=scratch, capture_output=True, text=True, timeout=30
    )
    return scratch, result, os.path.join(scratch, "bsq")


def run_C_bsq(student_dir):
    if not os.path.exists(os.path.join(student_dir, "Makefile")):
        print_test_fail(1, "no Makefile found at the project root")
        print_exercise_result("*.c", 0, 1)
        return False

    c_files = sorted(glob.glob(os.path.join(student_dir, "*.c")))
    fn_ok = True
    for f in c_files:
        fn_ok = check_allowed_functions(f, ALLOWED) and fn_ok

    scratch, result, exe_path = build_in_scratch(student_dir)

    i = 0
    passed_count = 0

    def check(condition, description, expected=None, actual=None, show_value=None):
        nonlocal i, passed_count
        i += 1
        if condition:
            if show_value is not None:
                print_test_pass(i, f"{description} {display_str(show_value)} as expected")
            else:
                print_test_pass(i, f"{description} as expected")
            passed_count += 1
        else:
            print_test_fail(
                i, f"{description} not as expected", expected=expected, actual=actual
            )

    check(
        result.returncode == 0,
        "`make`: exit status",
        expected="0 (success)",
        actual=result.returncode,
    )
    check(os.path.exists(exe_path), "`make`: bsq binary produced")

    if not os.path.exists(exe_path):
        print_exercise_result("*.c", passed_count, i)
        shutil.rmtree(scratch, ignore_errors=True)
        return False

    print_command_execution(f"{exe_path} <mapfile>")

    # "Must not relink": a second `make` with nothing changed must not
    # re-run the final link step - checked in a filename-agnostic way
    # (student source layout is unknown) via the binary's own mtime rather
    # than parsing compiler-invocation text.
    mtime_before = os.path.getmtime(exe_path)
    subprocess.run(["make"], cwd=scratch, capture_output=True, text=True, timeout=30)
    mtime_after = os.path.getmtime(exe_path)
    check(
        mtime_before == mtime_after,
        "a second `make` (nothing changed): binary not relinked",
        expected=f"mtime unchanged ({mtime_before})",
        actual=mtime_after,
    )

    map_file = os.path.join(scratch, "map.txt")

    for n, (label, map_text) in enumerate(VALID_MAPS.items(), 1):
        expected = solve_map(map_text)
        with open(map_file, "w") as f:
            f.write(map_text)
        actual, err, code = run_test_case(exe_path, args=[map_file])
        check(
            actual == expected,
            f"valid map [{label}]: biggest square",
            expected=expected,
            actual=actual,
            show_value=actual,
        )

    # stdin must behave identically to a file argument for the same map.
    example = VALID_MAPS["subject's own worked example"]
    expected = solve_map(example)
    actual, err, code = run_test_case(exe_path, input_data=example)
    check(
        actual == expected,
        "reading a map from stdin (no file argument): output",
        expected=expected,
        actual=actual,
    )

    error_example = ERROR_MAPS["zero line count"]
    actual, err, code = run_test_case(exe_path, input_data=error_example)
    check(
        actual == "map error\n",
        "reading an invalid map from stdin (no file argument): output",
        expected="map error\n",
        actual=actual,
    )

    # Multiple file arguments: blank line between outputs/errors.
    map_a = os.path.join(scratch, "map_a.txt")
    map_b = os.path.join(scratch, "map_b.txt")
    with open(map_a, "w") as f:
        f.write(VALID_MAPS["1x1 single empty cell"])
    with open(map_b, "w") as f:
        f.write(ERROR_MAPS["zero line count"])
    expected_multi = solve_map(VALID_MAPS["1x1 single empty cell"]) + "\n" + "map error\n"
    actual, err, code = run_test_case(exe_path, args=[map_a, map_b])
    check(
        actual == expected_multi,
        "two file arguments: outputs separated by a blank line",
        expected=expected_multi,
        actual=actual,
    )

    # "1 to n files as parameters" - re-confirm with n=3, not just n=2, mixing
    # a second valid map back in after an error to check state doesn't leak
    # between files.
    map_c = os.path.join(scratch, "map_c.txt")
    with open(map_c, "w") as f:
        f.write(VALID_MAPS["single row"])
    expected_three = (
        solve_map(VALID_MAPS["1x1 single empty cell"])
        + "\n"
        + "map error\n"
        + "\n"
        + solve_map(VALID_MAPS["single row"])
    )
    actual, err, code = run_test_case(exe_path, args=[map_a, map_b, map_c])
    check(
        actual == expected_three,
        "three file arguments (1 to n): blank-line-separated outputs/errors",
        expected=expected_three,
        actual=actual,
    )

    for label, map_text in ERROR_MAPS.items():
        with open(map_file, "w") as f:
            f.write(map_text)
        actual, err, code = run_test_case(exe_path, args=[map_file])
        check(
            actual == "map error\n",
            f"invalid map [{label}]: output",
            expected="map error\n",
            actual=actual,
        )

    actual, err, code = run_test_case(
        exe_path, args=[os.path.join(scratch, "does_not_exist.txt")]
    )
    check(
        actual == "map error\n",
        "a nonexistent file argument: output",
        expected="map error\n",
        actual=actual,
    )

    print_exercise_result("*.c", passed_count, i)

    shutil.rmtree(scratch, ignore_errors=True)

    return passed_count == i and fn_ok
