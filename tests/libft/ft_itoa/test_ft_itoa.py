from ..harness_runner import run_harness_cases, run_allocation_cases

FUNCTION = "ft_itoa"

VALUES = [
    (0, "zero, which needs a digit of its own"),
    (1, "a single digit"),
    (-1, "a single negative digit"),
    (42, "a positive number"),
    (-42, "a negative number"),
    (10, "a number ending in zero"),
    (100000, "a six-digit number"),
    (2147483647, "INT_MAX"),
    # Negating INT_MIN overflows, so an implementation that starts with
    # n = -n produces garbage here. It is also the only value whose digit
    # count differs from that of its absolute value's naive computation.
    (-2147483648, "INT_MIN, which cannot be negated"),
]


def run_libft_ft_itoa(student_file):
    cases = [
        ([str(value)], None, str(value), f"ft_itoa of {description}")
        for value, description in VALUES
    ]
    behavior_ok = run_harness_cases(
        student_file, FUNCTION, FUNCTION, cases, with_free_tracker=True
    )
    allocation_ok = run_allocation_cases(student_file, FUNCTION)
    return behavior_ok and allocation_ok
