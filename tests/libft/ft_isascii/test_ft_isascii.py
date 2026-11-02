from ..harness_runner import run_harness_cases

FUNCTION = "ft_isascii"


def _expected(start, end):
    # unlike the others this one is defined for every int, so the
#   range deliberately runs outside 0-127 in both directions - that is the
#   entire behaviour being tested.
    #
    # The subject requires exactly 1 or 0 rather than any non-zero value, so
    # the harness prints the returned int itself and substitutes '?' for
    # anything else - which never matches the string built here.
    return "".join("1" if 0 <= c <= 127 else "0" for c in range(start, end + 1))


def run_libft_ft_isascii(student_file):
    cases = [
        (
            ["-20", "300"],
            None,
            _expected(-20, 300),
            "every code point -20..300 classified",
        ),
    ]
    return run_harness_cases(student_file, FUNCTION, FUNCTION, cases)
