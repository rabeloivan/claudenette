from ..harness_runner import run_harness_cases

FUNCTION = "ft_striteri"

CASES = [
    ("hello world", "a plain lowercase string"),
    ("HELLO", "an already uppercase string"),
    ("", "the empty string"),
    ("a1b2c3", "letters interleaved with digits"),
    ("abcdefghij", "a longer run, so an off-by-one in the index shows"),
]


def _mapped(text):
    # f uppercases at even indices and lowercases at odd ones, so the expected
    # value depends on the index as well as the character.
    out = []
    for i, c in enumerate(text):
        if i % 2 == 0:
            out.append(c.upper() if "a" <= c <= "z" else c)
        else:
            out.append(c.lower() if "A" <= c <= "Z" else c)
    return "".join(out)


def run_libft_ft_striteri(student_file):
    cases = [
        ([text], None, _mapped(text), "ft_striteri over %s" % description)
        for text, description in CASES
    ]
    return run_harness_cases(
        student_file, FUNCTION, FUNCTION, cases
    )
