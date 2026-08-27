import glob
import os
import re

INT_MIN = -2147483648
INT_MAX = 2147483647

from utils.compiler import compile_source
from utils.functions import check_allowed_functions
from utils.norminette import check_norminette
from utils.runner import run_test_case
from utils.ui import (
    display_str,
    print_command_execution,
    print_exercise_result,
    print_rush00_summary,
    print_test_fail,
    print_test_pass,
)

TEST_DIR = os.path.dirname(os.path.abspath(__file__))
HARNESS = os.path.join(TEST_DIR, "rush_harness.c")

# Each of the five subject versions (assigned per-team via a login-derived
# modulo, so a local run can't know in advance which one applies - see
# run_C_rush00 below, which tests whichever rush0X.c file(s) actually exist).
# (top_left, top_right), (bottom_left, bottom_right), fill char, middle char.
VARIANTS = {
    0: {"top": ("o", "o"), "bottom": ("o", "o"), "fill": "-", "mid": "|"},
    1: {"top": ("/", "\\"), "bottom": ("\\", "/"), "fill": "*", "mid": "*"},
    2: {"top": ("A", "A"), "bottom": ("C", "C"), "fill": "B", "mid": "B"},
    3: {"top": ("A", "C"), "bottom": ("A", "C"), "fill": "B", "mid": "B"},
    4: {"top": ("A", "C"), "bottom": ("C", "A"), "fill": "B", "mid": "B"},
}


def expected_rush(variant, width, height):
    # Undefined by the subject for non-positive dimensions - caller falls
    # back to a robustness-only check (no crash/hang) instead of an exact
    # output comparison.
    if width <= 0 or height <= 0:
        return None
    v = VARIANTS[variant]
    lines = []
    for i in range(height):
        if i == 0:
            left, right, infill = v["top"][0], v["top"][1], v["fill"]
        elif i == height - 1:
            left, right, infill = v["bottom"][0], v["bottom"][1], v["fill"]
        else:
            left = right = v["mid"]
            infill = " "
        if width == 1:
            lines.append(left)
        else:
            lines.append(left + infill * (width - 2) + right)
    # Every row is newline-terminated, including the last - the subject's
    # own terminal transcripts show the shape immediately followed by the
    # next shell prompt on its own line.
    return "\n".join(lines) + "\n"


def discover_variants(student_dir):
    found = []
    for path in sorted(glob.glob(os.path.join(student_dir, "rush0*.c"))):
        match = re.fullmatch(r"rush0([0-4])\.c", os.path.basename(path))
        if match:
            found.append((int(match.group(1)), path))
    return found


def check_main_compiles(main_c, student_file, a_variant_file):
    # main.c's own content is irrelevant to functional grading (the subject
    # says the defense swaps in its own main() to call rush()), but it's
    # still a required turn-in file subject to the same "must compile or
    # score 0" gate - and its compilability doesn't depend on which variant
    # it's paired with, so this only needs to run once, not per-variant.
    if not os.path.exists(main_c):
        print_test_fail(1, "main.c is missing from ex00/ (required turn-in file)")
        return False
    norm_ok = check_norminette(main_c)
    fn_ok = check_allowed_functions(main_c, ["write"])
    exe_path = "./rush_ownmain"
    compiled = compile_source(
        [main_c, student_file, a_variant_file], exe_path,
        flags=["-Wall", "-Wextra", "-Werror"],
    )
    if os.path.exists(exe_path):
        os.remove(exe_path)
    ok = norm_ok and fn_ok and compiled
    if ok:
        print_test_pass(1, "main.c compiles cleanly with ft_putchar.c and a rush0X.c")
    else:
        print_test_fail(1, "main.c has a norm, allowed-function, or compile problem")
    return ok


def run_variant(student_file, variant, variant_file):
    filename = os.path.basename(variant_file)
    norm_ok = check_norminette(variant_file)
    fn_ok = check_allowed_functions(variant_file, ["write"])

    exe_path = f"./rush_{variant}"
    compiled = compile_source(
        [HARNESS, student_file, variant_file], exe_path,
        flags=["-Wall", "-Wextra", "-Werror"],
    )
    if not compiled:
        print_exercise_result(f"ex00/{filename}", 0, 1)
        return False

    print_command_execution(f"{exe_path} <x> <y>")

    shape_cases = [(5, 3), (5, 1), (1, 1), (1, 5), (4, 4), (10, 1), (1, 10), (7, 7)]
    # Never specified by the subject what a non-positive or extreme
    # dimension should print - only that rush() "must never crash or enter
    # an infinite loop" - so these are checked for robustness only, not
    # exact output. INT_MIN/INT_MAX specifically: a guard against one
    # extreme (e.g. an abs()-style negation that only overflows at
    # INT_MIN) does not imply a guard against the other exists too - a real
    # submission passed 100% on automated moulinette but scored 0 from
    # human evaluators for guarding only INT_MIN, not INT_MAX, so both
    # boundaries are tested explicitly and independently, not just a small
    # representative negative number.
    robustness_cases = [
        (0, 5), (5, 0), (0, 0), (-3, 5), (5, -3),
        (INT_MIN, 5), (5, INT_MIN), (INT_MIN, INT_MIN),
        (INT_MAX, 5), (5, INT_MAX), (INT_MAX, INT_MAX),
    ]

    passed_count = 0
    total_count = len(shape_cases) + len(robustness_cases)

    for i, (w, h) in enumerate(shape_cases, 1):
        expected = expected_rush(variant, w, h)
        actual, err, code = run_test_case(exe_path, args=[str(w), str(h)])
        desc = f"rush({w}, {h}) [rush0{variant}]"
        if actual == expected:
            print_test_pass(i, f"{desc}: shape {display_str(actual)} as expected")
            passed_count += 1
        else:
            print_test_fail(i, f"{desc}: shape not as expected", expected=expected, actual=actual)

    for j, (w, h) in enumerate(robustness_cases, len(shape_cases) + 1):
        actual, err, code = run_test_case(exe_path, args=[str(w), str(h)], timeout=2)
        desc = f"rush({w}, {h}) [rush0{variant}, edge-value dimension]"
        if err == "TIMEOUT":
            print_test_fail(j, f"{desc} hung (timed out) - must never enter an infinite loop")
        elif code < 0:
            print_test_fail(j, f"{desc} crashed (signal {-code})")
        else:
            print_test_pass(j, f"{desc} did not crash or hang (exit {code})")
            passed_count += 1

    print_exercise_result(f"ex00/{filename}", passed_count, total_count)

    if os.path.exists(exe_path):
        os.remove(exe_path)

    return passed_count == total_count and norm_ok and fn_ok


def compute_rush00_score(variant_results):
    # Real grading anchors "the actual exercise" at whichever variant a
    # team was actually assigned, then walks onward through the others in
    # order - "if you don't get the actual exercise, the next one won't
    # be corrected." A local tester can't know which variant is really
    # assigned (see discover_variants above), so the best available proxy
    # is: whichever variant the student attempted *first* (lowest number
    # among the files they actually submitted) stands in for "their own
    # question," and each subsequent *attempted* variant either extends
    # the streak (correct) or ends it (wrong) - a variant that was never
    # submitted at all is simply skipped, not treated as a failure, since
    # nothing was there to grade. This is what makes "submit only your
    # one assigned variant and get it right -> 100" hold regardless of
    # which numeric variant that happens to be, while still matching
    # "the next one won't be corrected" once a genuinely wrong attempt is
    # hit. Streak maxes out at 5 (every variant attempted and correct),
    # so 100 + (streak - 1) * 6.25 naturally tops out at exactly 125.
    streak = 0
    for _, passed in variant_results:
        if not passed:
            break
        streak += 1
    if streak == 0:
        return 0
    return int(100 + (streak - 1) * 6.25)


def run_C_rush00(student_file, precheck_ok=True):
    # precheck_ok is main.py's norminette + allowed-functions verdict. rush00
    # is the one project that prints its own Result/Final score/Status block
    # instead of main.py's generic one, so unless that verdict reaches here
    # it gets computed and then silently discarded - a norm or forbidden-
    # function violation in ft_putchar.c would show "125% PASSED". When the
    # precheck failed we still run every variant (diagnostics are useful
    # either way, matching main.py's priority-not-short-circuit rule), but
    # we suppress our own summary so main.py's generic one - which reports
    # the real NORM ERR / FORBIDDEN FN status - is what the student sees.
    student_dir = os.path.dirname(student_file)
    main_c = os.path.join(student_dir, "main.c")
    variants = discover_variants(student_dir)

    if not variants:
        print_test_fail(
            1, "no rush0X.c file found in ex00/ (expected one of rush00.c..rush04.c)"
        )
        print_exercise_result("ex00/rush0X.c", 0, 1)
        if precheck_ok:
            print_rush00_summary([], 0)
        return False

    main_ok = check_main_compiles(main_c, student_file, variants[0][1])
    print()

    variant_results = []
    for variant, variant_file in variants:
        passed = run_variant(student_file, variant, variant_file)
        variant_results.append((variant, passed))
        print()

    # main.c not compiling is a hard, unconditional "doesn't compile ->
    # score 0" gate (a required turn-in file regardless of which variant),
    # so it zeroes the score even if every discovered variant is itself
    # functionally correct - but each variant's own true pass/fail is
    # still shown above and in the Result line either way, since that's
    # still useful diagnostic information on its own.
    score = compute_rush00_score(variant_results) if main_ok else 0
    if precheck_ok:
        print_rush00_summary(variant_results, score)

    return score > 0
