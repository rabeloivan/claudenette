from ..harness_runner import run_harness_cases

FUNCTION = "ft_strncmp"


def run_libft_ft_strncmp(student_file):
    # Only the sign is compared - see the harness for why.
    cases = [
        (["abc", "abc", "3"], None, "0", "equal strings"),
        (["abc", "abd", "3"], None, "-", "s1 smaller at the last compared byte"),
        (["abd", "abc", "3"], None, "+", "s1 greater at the last compared byte"),
        (["abc", "abd", "2"], None, "0",
         "n stops the comparison before the difference"),
        (["abc", "abcdef", "6"], None, "-",
         "a prefix is smaller than the longer string"),
        (["abcdef", "abc", "6"], None, "+",
         "comparison stops at s2's terminator rather than running past it"),
        (["abc", "abc", "0"], None, "0", "n of 0 always compares equal"),
        (["\x80", "\x01", "1"], None, "+",
         "bytes compare as unsigned char, so 0x80 is greater than 0x01"),
        (["", "", "5"], None, "0", "two empty strings compare equal"),
        (["", "a", "1"], None, "-", "the empty string is smaller"),
    ]
    return run_harness_cases(student_file, FUNCTION, FUNCTION, cases)
