from ..harness_runner import run_harness_cases, run_allocation_cases

FUNCTION = "ft_strtrim"

CASES = [
    ("   hello   ", " ", "spaces at both ends"),
    ("xxhelloxx", "x", "a single-character set"),
    ("\t\n hello \n\t", " \t\n", "a multi-character set"),
    ("hello", " ", "nothing to trim"),
    ("aaa", "a", "everything trimmed away"),
    ("", "abc", "an empty string"),
    ("hello", "", "an empty set trims nothing"),
    ("abcHELLOabc", "cba", "set members in any order"),
    ("  hello world  ", " ", "inner spaces are preserved"),
    ("xhellox", "y", "a set that matches nothing"),
]


def _trimmed(s, chars):
    return s.strip(chars) if chars else s


def run_libft_ft_strtrim(student_file):
    cases = [
        ([s1, cset], None, "[" + _trimmed(s1, cset) + "]",
         f"ft_strtrim with {description}")
        for s1, cset, description in CASES
    ]
    behavior_ok = run_harness_cases(
        student_file, FUNCTION, FUNCTION, cases, with_free_tracker=True
    )
    allocation_ok = run_allocation_cases(student_file, FUNCTION)
    return behavior_ok and allocation_ok
