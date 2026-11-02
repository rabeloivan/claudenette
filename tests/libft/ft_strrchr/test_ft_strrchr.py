from ..harness_runner import run_harness_cases

FUNCTION = "ft_strrchr"

S = "Hello, World!"


def run_libft_ft_strrchr(student_file):
    cases = [
        ([S, "108"], None, "10", "returns the LAST 'l', not the first"),
        ([S, "111"], None, "8", "returns the last 'o'"),
        ([S, "72"], None, "0", "a character occurring only at index 0"),
        ([S, "0"], None, str(len(S)),
         "searching for '\\0' returns a pointer to the terminator"),
        ([S, "122"], None, "NULL", "a character that is absent returns NULL"),
        ([S, "364"], None, "10", "c is converted to char (364 & 0xff is 'l')"),
        (["", "0"], None, "0", "the empty string still has a terminator to find"),
    ]
    return run_harness_cases(student_file, FUNCTION, FUNCTION, cases)
