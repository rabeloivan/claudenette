import glob
import os
import shutil
import subprocess
import tempfile

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

# "Error\n"/"Dict Error\n" are fixed sentinels a check's own description
# already names ("reports Error"/"reports Dict Error") - showing the
# literal string back would just repeat the description, not add data.
_BOILERPLATE_VALUES = ("Error\n", "Dict Error\n")

from ..numbers import (
    default_dictionary,
    dictionary_to_file_content,
    number_to_words,
    placeholder_dictionary,
)

BINARY = "rush-02"
ALLOWED_FNS = ["write", "malloc", "free", "open", "read", "close"]

# Numbers spanning every scale the default dictionary covers, plus the
# subject's own worked examples (42, 0, 100000). 4294967295/4294967296
# straddle UINT_MAX (4294967295) specifically, since the subject requires
# "numbers beyond the range of unsigned int" - a plain unsigned int
# accumulator would silently wrap exactly at that boundary.
NUMBER_CASES = [
    0, 1, 9, 13, 19, 20, 42, 99, 100, 300, 142, 999,
    1000, 2500, 100000, 999999,
    1000000, 4294967295, 4294967296,
    5000000000, 123456789012, 1000000000000,
]

# Each must produce exactly "Error\n" - no partial output, no other text.
ERROR_CASES = [
    ("negative number", "-5"),
    ("decimal (subject's own example)", "10.4"),
    ("non-numeric", "abc"),
    ("empty string", ""),
]


def _write_dict(path, dictionary):
    with open(path, "w") as f:
        f.write(dictionary_to_file_content(dictionary))


def run_rush02_ex00(student_file):
    # student_file is "ex00/Makefile" - "Files to turn in: Makefile and all
    # the necessary files" gives no fixed name for the .c/.h sources, only
    # the Makefile and the resulting binary name (rush-02) are pinned down
    # by the subject - the same shape as C11's do-op, inlined directly here
    # since (like do-op) this is the only own-Makefile exercise in this
    # project, not a whole day repeating the pattern.
    student_dir = os.path.dirname(student_file)

    c_files = sorted(glob.glob(os.path.join(student_dir, "*.c")))
    checks_ok = bool(c_files) and all(
        check_norminette(path) and check_allowed_functions(path, ALLOWED_FNS)
        for path in c_files
    )

    print_command_execution("make fclean && make")
    try:
        subprocess.run(
            ["make", "fclean"], cwd=student_dir, capture_output=True, timeout=30
        )
        build_result = subprocess.run(
            ["make"], cwd=student_dir, capture_output=True, text=True, timeout=30
        )
    except subprocess.TimeoutExpired:
        build_result = None

    binary_path = os.path.abspath(os.path.join(student_dir, BINARY))
    if build_result is None or not os.path.exists(binary_path):
        stderr = build_result.stderr if build_result else "TIMEOUT"
        print_test_fail(1, f"`make` did not produce {BINARY} (stderr: {display_str(stderr)})")
        print_exercise_result("ex00/Makefile", 0, 1)
        return False

    print_command_execution(f"{binary_path} <dict> <number>")

    passed_count = 0
    total_count = 0

    def check(condition, description, expected=None, actual=None):
        nonlocal passed_count, total_count
        total_count += 1
        if condition:
            if expected is not None and expected not in _BOILERPLATE_VALUES:
                print_test_pass(total_count, f"{description} {display_str(expected)} as expected")
            else:
                print_test_pass(total_count, f"{description} as expected")
            passed_count += 1
        else:
            print_test_fail(
                total_count, f"{description} not as expected", expected=expected, actual=actual
            )

    fixture_dir = tempfile.mkdtemp(prefix="claudenette_rush02_")
    try:
        base_dict = default_dictionary()
        default_dict_path = os.path.join(fixture_dir, "default.dict")
        _write_dict(default_dict_path, base_dict)

        override_dict = dict(base_dict)
        override_dict[20] = "hey everybody !"
        override_dict_path = os.path.join(fixture_dir, "override.dict")
        _write_dict(override_dict_path, override_dict)

        missing_million_dict = dict(base_dict)
        del missing_million_dict[1000000]
        missing_million_path = os.path.join(fixture_dir, "missing_million.dict")
        _write_dict(missing_million_path, missing_million_dict)

        malformed_path = os.path.join(fixture_dir, "malformed.dict")
        with open(malformed_path, "w") as f:
            f.write("0 : zero\nNOTANUMBER : oops\n1 : one\n")

        # Same entries as the default dictionary, but reordered and with
        # blank lines interspersed - both explicitly allowed by the
        # subject ("entries can be stored in any order", "there can be
        # empty lines"), so a parser that assumes a fixed layout must
        # still get this right.
        shuffled_items = list(base_dict.items())
        shuffled_items = shuffled_items[1::2] + shuffled_items[0::2]
        shuffled_lines = []
        for i, (k, v) in enumerate(shuffled_items):
            shuffled_lines.append(f"{k} : {v}")
            if i % 4 == 0:
                shuffled_lines.append("")
        shuffled_path = os.path.join(fixture_dir, "shuffled.dict")
        with open(shuffled_path, "w") as f:
            f.write("\n".join(shuffled_lines) + "\n")

        # Deliberately over-padded whitespace around one value, mirroring
        # the subject's own worked example exactly ("20   :      hey
        # everybody ! " in the dict -> "hey everybody !" in the output,
        # both the internal double-space before "hey" and the single
        # trailing space after "!" trimmed) - "You will trim the spaces
        # before and after the values" is a stated requirement, not just
        # a side effect of this test's other, cleanly-formatted fixtures.
        whitespace_dict_path = os.path.join(fixture_dir, "whitespace.dict")
        with open(whitespace_dict_path, "w") as f:
            f.write("20   :      hey everybody ! \n")

        # --- functional: 2-argument form (own dictionary, own numbers) ---
        # Testing exclusively via the 2-argument form is deliberate: the
        # real reference dictionary students are handed isn't available
        # here, so exact-output assertions are only possible against a
        # dictionary this test fully controls - the subject explicitly
        # supports this invocation ("if there are two arguments, the
        # first argument is the new reference dictionary").
        for n in NUMBER_CASES:
            expected = number_to_words(n, base_dict) + "\n"
            actual, err, code = run_test_case(binary_path, args=[default_dict_path, str(n)])
            check(actual == expected, f"rush-02 <dict> {n}: output", expected=expected, actual=actual)

        for label, num_str in ERROR_CASES:
            # Always the full 2-argument form, even for the empty-string
            # case - num_str="" is falsy in Python, and a conditional here
            # to "fall back" to a 1-argument call for it would silently
            # test argv=[dict_path] instead (the dict path itself parsed
            # as if it were the number, an unrelated invalid string that
            # happens to also produce "Error"), not the actual empty-string
            # case this is supposed to cover.
            actual, err, code = run_test_case(binary_path, args=[default_dict_path, num_str])
            check(actual == "Error\n", f"rush-02 with {label}: reports Error", expected="Error\n", actual=actual)

        actual, err, code = run_test_case(binary_path, args=[])
        check(actual == "Error\n", "rush-02 with no arguments: reports Error", expected="Error\n", actual=actual)

        # --- dictionary override (subject's own "20 -> hey everybody !") ---
        actual, err, code = run_test_case(binary_path, args=[override_dict_path, "20"])
        check(
            actual == "hey everybody !\n",
            "rush-02 <dict with 20 overridden> 20: uses the dictionary's value",
            expected="hey everybody !\n",
            actual=actual,
        )

        # --- dictionary whitespace trimming (subject's exact worked example) ---
        actual, err, code = run_test_case(binary_path, args=[whitespace_dict_path, "20"])
        check(
            actual == "hey everybody !\n",
            "rush-02 <dict value padded with extra spaces> 20: value trimmed",
            expected="hey everybody !\n",
            actual=actual,
        )

        # --- Dict Error: malformed dictionary line ---
        actual, err, code = run_test_case(binary_path, args=[malformed_path, "1"])
        check(
            actual == "Dict Error\n",
            "rush-02 <malformed dict> 1: reports Dict Error",
            expected="Dict Error\n",
            actual=actual,
        )

        # --- Dict Error: dictionary can't perform this specific conversion ---
        # Exact-match against "Dict Error\n" (not a substring/prefix check)
        # also catches a real bug found while building this test's own
        # reference: printing words incrementally as each group is
        # composed, only discovering the missing "million" key partway
        # through, left "two" already on stdout ahead of "Dict Error".
        actual, err, code = run_test_case(binary_path, args=[missing_million_path, "2500000"])
        check(
            actual == "Dict Error\n",
            "rush-02 <dict missing 'million'> 2500000 (needs it): reports Dict Error",
            expected="Dict Error\n",
            actual=actual,
        )
        # The same missing-key dictionary must still work for a number
        # that never needs that particular key - confirms the check is
        # "can this specific conversion be done", not "is the dictionary
        # smaller than the reference one".
        expected = number_to_words(42, missing_million_dict) + "\n"
        actual, err, code = run_test_case(binary_path, args=[missing_million_path, "42"])
        check(
            actual == expected,
            "rush-02 <dict missing 'million'> 42 (does not need it): still converts",
            expected=expected,
            actual=actual,
        )

        # --- dictionary parsing robustness: order and blank lines ---
        expected = number_to_words(142, base_dict) + "\n"
        actual, err, code = run_test_case(binary_path, args=[shuffled_path, "142"])
        check(
            actual == expected,
            "rush-02 <reordered dict with blank lines> 142: still converts",
            expected=expected,
            actual=actual,
        )

        # --- 1-argument form: structural only ---
        # The real default dictionary a student's own program reads with
        # no dictionary argument isn't known here (whatever file/format
        # they bundle it as), so this can only check the program doesn't
        # crash or hang - not assert a specific output.
        total_count += 1
        actual, err, code = run_test_case(binary_path, args=["42"], timeout=5)
        if err == "TIMEOUT":
            print_test_fail(total_count, "rush-02 42 (1-argument form): hung (timed out)")
        elif code < 0:
            print_test_fail(
                total_count, "rush-02 42 (1-argument form): crashed", actual=f"signal {-code}"
            )
        else:
            print_test_pass(total_count, "rush-02 42 (1-argument form): did not crash or hang")
            passed_count += 1

        # --- bonuses ---
        # Tracked entirely separately from passed_count/total_count above:
        # the subject's own rule ("if a bonus works but the mandatory one
        # fails the tests, you will receive a score of 0") only ever lets a
        # mandatory failure zero out a bonus, never the other way around -
        # a failed or unattempted bonus must not cost the mandatory score.
        #
        # Only 2 of the 3 stated bonuses are testable. "Using '-', ',',
        # 'and' to be closer to the correct written syntax" has neither an
        # invocation convention (no argument/flag distinguishes "give me
        # the refined format" from the mandatory plain one - and the
        # mandatory format must still be reachable, since a program that
        # always emits refined syntax would fail the mandatory tests
        # outright) nor an exact punctuation convention (English usage
        # genuinely disagrees on hyphen/comma/"and" placement, e.g.
        # American vs. British "one hundred (and) one"), and the subject
        # gives no worked example for it. Same class of genuine spec gap
        # as shell01's add_chelou.sh or shell00's diff - flagged here
        # rather than guessed at, not tested.
        bonus_passed = 0
        bonus_total = 0
        bj = 0

        def bonus_check(condition, description, expected=None, actual=None):
            nonlocal bonus_passed, bonus_total, bj
            bonus_total += 1
            bj += 1
            if condition:
                if expected is not None and expected not in _BOILERPLATE_VALUES:
                    print_test_pass(bj, f"[BONUS] {description} {display_str(expected)} as expected")
                else:
                    print_test_pass(bj, f"[BONUS] {description} as expected")
                bonus_passed += 1
            else:
                print_test_fail(
                    bj, f"[BONUS] {description} not as expected", expected=expected, actual=actual
                )

        # Bonus: "doing the same exercise in a different language, using
        # another dictionary which will contain the translated entries."
        # Already well-supported by the mandatory design as long as it's
        # genuinely dictionary-driven - this exercises every building
        # block via a full placeholder vocabulary (see numbers.py for why
        # it's a placeholder, not a real language), not just the single
        # overridden key the mandatory-section override test already
        # covers, so a program with some hardcoded-English fallback logic
        # beyond that one key would still be caught.
        placeholder_dict = placeholder_dictionary()
        placeholder_path = os.path.join(fixture_dir, "placeholder.dict")
        _write_dict(placeholder_path, placeholder_dict)
        for n in (0, 42, 142, 100000):
            expected = number_to_words(n, placeholder_dict) + "\n"
            actual, err, code = run_test_case(binary_path, args=[placeholder_path, str(n)])
            bonus_check(
                actual == expected,
                f"rush-02 <placeholder-language dict> {n}: translated output",
                expected=expected,
                actual=actual,
            )

        # Bonus: "Using read to read numbers from the standard input (one
        # per line) when the command line argument for the number is '-'."
        # Precisely specified, with a worked example - unlike the syntax
        # bonus above, this is fully testable. Each line is checked
        # independently (an invalid line prints its own "Error" without
        # aborting the remaining lines), matching how the mandatory
        # single-shot invocation already handles one number at a time -
        # "one per line" is the natural extension of that, not a new
        # all-or-nothing contract the subject never actually states.
        stdin_cases = [42, 0, 100000]
        stdin_input = "".join(f"{n}\n" for n in stdin_cases)
        stdin_expected = "".join(number_to_words(n, base_dict) + "\n" for n in stdin_cases)
        actual, err, code = run_test_case(
            binary_path, args=[default_dict_path, "-"], input_data=stdin_input
        )
        bonus_check(
            actual == stdin_expected,
            "rush-02 <dict> - (stdin, all valid lines): converts each in order",
            expected=stdin_expected,
            actual=actual,
        )

        mixed_input = "42\n10.4\n7\n"
        mixed_expected = "forty two\nError\nseven\n"
        actual, err, code = run_test_case(
            binary_path, args=[default_dict_path, "-"], input_data=mixed_input
        )
        bonus_check(
            actual == mixed_expected,
            "rush-02 <dict> - (stdin, one invalid line among valid ones): "
            "reports Error for just that line",
            expected=mixed_expected,
            actual=actual,
        )

        print_exercise_result("ex00/Makefile [bonus: translation, stdin]", bonus_passed, bonus_total)
    finally:
        shutil.rmtree(fixture_dir, ignore_errors=True)

    print_exercise_result("ex00/Makefile", passed_count, total_count)

    subprocess.run(["make", "fclean"], cwd=student_dir, capture_output=True, timeout=30)
    if os.path.exists(binary_path):
        os.remove(binary_path)
    for name in os.listdir(student_dir):
        if name.endswith(".o"):
            os.remove(os.path.join(student_dir, name))

    return passed_count == total_count and checks_ok
