from ..harness_runner import run_harness_cases

FUNCTION = "ft_tolower"


def _expected(start, end):
    # Only 'A'-'Z' shift; everything else, including the '[' / '`' characters
    # that sit immediately outside the two case ranges, is returned unchanged.
    return ",".join(
        str(c + 32 if 65 <= c <= 90 else c) for c in range(start, end + 1)
    )


def run_libft_ft_tolower(student_file):
    cases = [
        (["0", "127"], None, _expected(0, 127), "every code point 0..127 converted"),
        # The rest of ctype(3)'s domain, returned unchanged: EOF must come
        # back as EOF, and 128..255 as themselves - not narrowed through a
        # char into negatives, or through an unsigned char, which makes EOF
        # 255.
        (["-1", "255"], None, _expected(-1, 255), "EOF and 128..255 returned unchanged"),
    ]
    return run_harness_cases(student_file, FUNCTION, FUNCTION, cases)
