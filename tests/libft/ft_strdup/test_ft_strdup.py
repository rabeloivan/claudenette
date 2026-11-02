from ..harness_runner import run_harness_cases, run_allocation_cases

FUNCTION = "ft_strdup"

CASES = [
    ("hello world", "a plain string"),
    ("", "the empty string"),
    ("x" * 300, "a 300-byte string"),
    ("tabs\tand\nnewlines", "embedded control characters"),
]


def run_libft_ft_strdup(student_file):
    cases = [
        ([text], None, text, f"ft_strdup of {description}")
        for text, description in CASES
    ]
    behavior_ok = run_harness_cases(
        student_file, FUNCTION, FUNCTION, cases, with_free_tracker=True
    )
    allocation_ok = run_allocation_cases(student_file, FUNCTION)
    return behavior_ok and allocation_ok
