from ..harness_runner import run_harness_cases

FUNCTION = "ft_memchr"


def run_libft_ft_memchr(student_file):
    # Buffer is 10 41 00 42 41 aa 41 ff.
    cases = [
        (["0"], None, "3", "a byte present once"),
        (["1"], None, "2", "searching for 0x00, which must be found not stopped at"),
        (["2"], None, "1", "returns the FIRST match, not a later one"),
        (["3"], None, "NULL", "a match beyond n is not found"),
        (["4"], None, "NULL", "a byte that is absent returns NULL"),
        (["5"], None, "5", "a byte above 0x7f, compared as unsigned char"),
        (["6"], None, "1", "c is converted to unsigned char (0x341 matches 0x41)"),
        (["7"], None, "NULL", "n of 0 always returns NULL"),
    ]
    return run_harness_cases(student_file, FUNCTION, FUNCTION, cases)
