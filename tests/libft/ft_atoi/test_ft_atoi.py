from ..harness_runner import run_harness_cases

FUNCTION = "ft_atoi"

# The man page's grammar: optional whitespace, then an optional single sign,
# then digits, stopping at the first non-digit. Values outside int range are
# undefined behaviour in atoi(3) and are deliberately NOT tested - requiring a
# particular wrap or clamp would fail submissions the subject does not.
CASES = [
    ("0", 0, "zero"),
    ("42", 42, "a plain number"),
    ("-42", -42, "a negative number"),
    ("+42", 42, "an explicit plus sign"),
    ("   42", 42, "leading spaces"),
    ("\t\n\v\f\r 42", 42, "the full set of leading whitespace"),
    ("42abc", 42, "digits followed by junk"),
    ("abc42", 0, "junk before any digit yields 0"),
    ("", 0, "the empty string"),
    ("   ", 0, "whitespace only"),
    ("-", 0, "a lone sign"),
    ("+-42", 0, "two signs are not accepted"),
    ("--42", 0, "two minus signs are not accepted"),
    ("4 2", 4, "a space stops the parse"),
    ("2147483647", 2147483647, "INT_MAX"),
    ("-2147483648", -2147483648, "INT_MIN"),
    ("007", 7, "leading zeros"),
    ("-0", 0, "negative zero prints as 0"),
    (" +7", 7, "whitespace then a sign"),
    ("+ 7", 0, "a space between sign and digits stops the parse"),
]


def run_libft_ft_atoi(student_file):
    cases = [
        ([text], None, str(value), f"ft_atoi of {description}")
        for text, value, description in CASES
    ]
    return run_harness_cases(student_file, FUNCTION, FUNCTION, cases)
