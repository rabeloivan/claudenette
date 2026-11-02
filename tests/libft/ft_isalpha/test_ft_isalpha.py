from ..harness_runner import run_harness_cases

FUNCTION = "ft_isalpha"


def _expected(start, end):
    # A-Z and a-z only; the digits, punctuation and control
#   characters in between must all classify as 0.
    #
    # The subject requires exactly 1 or 0 rather than any non-zero value, so
    # the harness prints the returned int itself and substitutes '?' for
    # anything else - which never matches the string built here.
    return "".join("1" if (65 <= c <= 90) or (97 <= c <= 122) else "0" for c in range(start, end + 1))


def run_libft_ft_isalpha(student_file):
    cases = [
        (
            ["0", "127"],
            None,
            _expected(0, 127),
            "every code point 0..127 classified",
        ),
        # The rest of the domain ctype(3) gives these functions: "an unsigned
        # char or the value of EOF". Nothing past 127 is a letter, digit or
        # printable in the C locale, and EOF is none of them - where a lookup
        # table indexed by c, or a bound on one side only, goes wrong.
        (
            ["-1", "255"],
            None,
            _expected(-1, 255),
            "EOF and 128..255 classified as nothing",
        ),
    ]
    return run_harness_cases(student_file, FUNCTION, FUNCTION, cases)
