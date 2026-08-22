import os

from utils.ui import display_str, print_exercise_result, print_test_fail, print_test_pass

# The exact filename from the subject, transcribed character-by-character
# (join, not a literal, to avoid any Python-string-escaping ambiguity):
# " \ ? $ * ' M a R V i N ' * $ ? \ "
FILENAME = "".join(
    ['"', "\\", "?", "$", "*", "'", "M", "a", "R", "V", "i", "N", "'", "*", "$", "?", "\\", '"']
)


def run_shell01_ex05(student_file):
    # student_file is the full path (main.py's mapping key is "ex05/" +
    # FILENAME directly, same convention as every other exercise) - Python
    # dict keys/os.path calls handle the unusual characters natively, no
    # special-casing needed anywhere.
    i = 0
    passed = 0

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

    exists = os.path.exists(student_file) and not os.path.isdir(student_file)
    check(exists, f"a file named exactly {display_str(FILENAME)} exists")

    if exists:
        with open(student_file, "rb") as f:
            content = f.read()
        # "Create a file containing only '42', and nothing else" - read
        # literally as exactly those 2 bytes, no trailing newline. A
        # judgment call (the subject never mentions a newline either way),
        # documented rather than silently assumed.
        check(
            content == b"42",
            "content (exactly '42' and nothing else)",
            expected="42",
            actual=content.decode("latin-1"),
        )

    print_exercise_result(student_file, passed, i)
    return passed == i
