from ..harness_runner import run_harness_cases

FUNCTION = "ft_putchar_fd"


def run_libft_ft_putchar_fd(student_file):
    cases = [
        (["A", "1"], None, "A", "a letter on stdout"),
        (["\n", "1"], None, "\n", "a newline"),
        (["0", "1"], None, "0", "a digit character, not its numeric value"),
        # Staying off stdout is half of it - see ft_putstr_fd's case.
        (["Z", "2"], None, "[]",
         "fd 2: the character on stderr, nothing on stdout", "Z"),
    ]
    return run_harness_cases(student_file, FUNCTION, FUNCTION, cases)
