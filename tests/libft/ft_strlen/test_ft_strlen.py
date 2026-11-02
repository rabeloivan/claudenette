from ..harness_runner import run_harness_cases
from utils.ui import display_str

FUNCTION = "ft_strlen"

CASES = [
    ("", "the empty string"),
    ("a", "a single character"),
    ("hello world", "a plain string"),
    ("   ", "only spaces"),
    ("\t\n\r", "whitespace control characters"),
    ("x" * 4096, "a 4096-byte string"),
    ("caf\xe9 na\xefve", "bytes above 0x7f, counted as bytes not characters"),
]


def run_libft_ft_strlen(student_file):
    # Length is measured in BYTES, not Python characters: argv reaches the
    # process UTF-8 encoded, so "café" is 5 bytes and ft_strlen must say 5.
    # Counting len(text) here instead would fail a correct implementation on
    # the non-ASCII case.
    cases = [
        (
            [text],
            None,
            str(len(text.encode("utf-8"))),
            f"ft_strlen({display_str(text, limit=32)})",
        )
        for text, description in CASES
    ]
    return run_harness_cases(student_file, FUNCTION, FUNCTION, cases)
