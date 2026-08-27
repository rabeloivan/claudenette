from utils.ui import (
    print_command_execution,
    print_exercise_result,
    print_test_fail,
    print_test_pass,
)

from ...shell_utils import run_sh
from ..chelou import BASE_NBR1, BASE_NBR2, expected_output

# The subject's two worked examples, verbatim. They are graded like any other
# case AND used as a self-check on tests/shell01/chelou.py below - if a future
# edit to those base strings breaks them, this test must fail loudly rather
# than quietly grade everyone against a wrong oracle.
SUBJECT_EXAMPLES = [
    ("\\'?\"\\\"'\\", "rcrdmddd", "Salut"),
    (
        '\\"\\"!\\"\\"!\\"\\"!\\"\\"!\\"\\"!\\"\\"',
        "dcrcmcmooododmrrrmorcmcrmomo",
        "Segmentation fault",
    ),
]

# (FT_NBR1, FT_NBR2) pairs beyond the subject's own examples. The expected
# output is computed by the oracle, never hardcoded.
EXTRA_CASES = [
    ("'", "m"),                     # zero + zero
    ("\\", "r"),                    # 1 + 1
    ("!", "c"),                     # largest single digit in each base
    ("'\\", "mr"),                  # leading zeros in both
    ("!!!!", "ccc"),                # several digits, no carry tricks
    ("\\\"?!", "mrdoc"),            # every digit of each base, once
]

# Inputs the subject gives no defined output for. It never specifies an error
# message, so the only thing that can fairly be required is that the script
# doesn't print something that looks like a valid answer.
INVALID_CASES = [
    ("z", "m"),                     # character outside base 1
    ("'", "z"),                     # character outside base 2
    ("", "m"),                      # empty is not a number
    ("'", ""),
]


def run_shell01_ex08(student_file):
    i = 0
    passed = 0
    total = 0

    def check(condition, description, expected=None, actual=None):
        nonlocal i, passed
        i += 1
        if condition:
            print_test_pass(i, f"{description} as expected")
            passed += 1
        else:
            print_test_fail(
                i, f"{description} not as expected", expected=expected, actual=actual
            )

    # Guard the oracle before grading anything with it.
    for nbr1, nbr2, want in SUBJECT_EXAMPLES:
        if expected_output(nbr1, nbr2) != want:
            print_test_fail(
                1,
                "claudenette's own add_chelou oracle disagrees with the subject's "
                "worked example - this is a bug in the grader, not your script",
                expected=want,
                actual=expected_output(nbr1, nbr2),
            )
            print_exercise_result("ex08/add_chelou.sh", 0, 1)
            return False

    print_command_execution(f"sh {student_file} (with FT_NBR1/FT_NBR2 in the environment)")

    cases = [(n1, n2) for n1, n2, _ in SUBJECT_EXAMPLES] + EXTRA_CASES
    total = len(cases) + len(INVALID_CASES)

    for nbr1, nbr2 in cases:
        want = expected_output(nbr1, nbr2)
        actual, err, code = run_sh(
            student_file, env={"FT_NBR1": nbr1, "FT_NBR2": nbr2}
        )
        desc = f"FT_NBR1={nbr1!r} FT_NBR2={nbr2!r}"
        if err == "TIMEOUT":
            check(False, f"{desc}: output", expected=want, actual="TIMEOUT")
        else:
            check(actual.strip() == want, f"{desc}: output", expected=want, actual=actual.strip())

    for nbr1, nbr2 in INVALID_CASES:
        actual, err, code = run_sh(
            student_file, env={"FT_NBR1": nbr1, "FT_NBR2": nbr2}
        )
        desc = f"FT_NBR1={nbr1!r} FT_NBR2={nbr2!r} (invalid)"
        if err == "TIMEOUT":
            check(False, f"{desc}: did not hang", expected="no output", actual="TIMEOUT")
            continue
        # Any output made only of output-base digits would read as a real
        # answer; the subject defines none for invalid input, so that's the
        # one thing this must not do. Anything else (nothing, an error
        # message) is accepted - the subject never pins the wording.
        stripped = actual.strip()
        looks_like_an_answer = bool(stripped) and all(
            c in "gtaio luSnemf" for c in stripped
        )
        check(
            not looks_like_an_answer,
            f"{desc}: did not print a number",
            expected="no numeric answer",
            actual=stripped,
        )

    print_exercise_result("ex08/add_chelou.sh", passed, total)
    return passed == total
