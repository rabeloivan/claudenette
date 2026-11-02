from ..harness_runner import run_harness_cases, run_allocation_cases

FUNCTION = "ft_strjoin"

CASES = [
    ("hello ", "world", "two non-empty strings"),
    ("", "world", "an empty prefix"),
    ("hello", "", "an empty suffix"),
    ("", "", "two empty strings"),
    ("a" * 100, "b" * 100, "a 200-byte result"),
    ("tab\t", "\nnewline", "embedded control characters"),
]


def run_libft_ft_strjoin(student_file):
    cases = [
        ([s1, s2], None, "[" + s1 + s2 + "]", f"ft_strjoin of {description}")
        for s1, s2, description in CASES
    ]
    behavior_ok = run_harness_cases(
        student_file, FUNCTION, FUNCTION, cases, with_free_tracker=True
    )
    allocation_ok = run_allocation_cases(student_file, FUNCTION)
    return behavior_ok and allocation_ok
