from ..harness_runner import run_harness_cases

FUNCTION = "ft_memcmp"


def run_libft_ft_memcmp(student_file):
    # Only the sign is compared - see the harness for why the magnitude is not.
    cases = [
        (["0"], None, "0", "identical buffers compare equal"),
        (["1"], None, "+", "s1 greater at the first differing byte"),
        (["2"], None, "-", "s1 smaller at the first differing byte"),
        (["3"], None, "+",
         "0x80 vs 0x01 - bytes compare as unsigned char, so this is positive"),
        (["4"], None, "-", "a difference in the final byte is still found"),
        (["5"], None, "0", "n of 0 compares equal"),
        (["6"], None, "0", "n of 0 compares equal even when byte 0 differs"),
    ]
    return run_harness_cases(student_file, FUNCTION, FUNCTION, cases)
