from ..harness_runner import run_harness_cases

FUNCTION = "ft_strchr"

S = "Hello, World!"


def run_libft_ft_strchr(student_file):
    cases = [
        ([S, "72"], None, "0", "'H' at the very start"),
        ([S, "108"], None, "2", "returns the FIRST 'l', not a later one"),
        ([S, "33"], None, "12", "'!' as the last character"),
        ([S, "0"], None, str(len(S)),
         "searching for '\\0' returns a pointer to the terminator"),
        ([S, "122"], None, "NULL", "a character that is absent returns NULL"),
        ([S, "364"], None, "2",
         "c is converted to char (364 & 0xff is 'l')"),
        (["", "0"], None, "0", "the empty string still has a terminator to find"),
        (["", "97"], None, "NULL", "no match in the empty string"),
    ]
    return run_harness_cases(student_file, FUNCTION, FUNCTION, cases)
