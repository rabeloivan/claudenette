from ..harness_runner import run_harness_cases

FUNCTION = "ft_putendl_fd"


def run_libft_ft_putendl_fd(student_file):
    cases = [
        (["hello", "1"], None, "hello\n", "a string followed by a newline"),
        (["", "1"], None, "\n", "the empty string still emits the newline"),
        (["a\tb", "1"], None, "a\tb\n", "embedded control characters"),
        # Staying off stdout is half of it - see ft_putstr_fd's case.
        (["hello", "2"], None, "[]", "fd 2: the line on stderr, nothing on stdout",
         "hello\n"),
    ]
    return run_harness_cases(student_file, FUNCTION, FUNCTION, cases)
