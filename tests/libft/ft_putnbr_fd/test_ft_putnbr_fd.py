from ..harness_runner import run_harness_cases

FUNCTION = "ft_putnbr_fd"

CASES = [
    ("0", "0", "zero"),
    ("42", "42", "a positive number"),
    ("-42", "-42", "a negative number"),
    ("2147483647", "2147483647", "INT_MAX"),
    # INT_MIN is the classic failure: negating it overflows, so an
    # implementation that does n = -n before printing produces garbage.
    ("-2147483648", "-2147483648", "INT_MIN, which cannot be negated"),
    ("-1", "-1", "a single negative digit"),
    ("10", "10", "a number ending in zero"),
]


def run_libft_ft_putnbr_fd(student_file):
    cases = [
        ([value, "1"], None, expected, f"ft_putnbr_fd of {description}")
        for value, expected, description in CASES
    ]
    # Staying off stdout is half of it - see ft_putstr_fd's case.
    cases.append((["42", "2"], None, "[]", "fd 2: the number on stderr, nothing on stdout",
                  "42"))
    return run_harness_cases(student_file, FUNCTION, FUNCTION, cases)
