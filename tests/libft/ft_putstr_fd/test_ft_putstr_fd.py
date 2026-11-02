from ..harness_runner import run_harness_cases

FUNCTION = "ft_putstr_fd"


def run_libft_ft_putstr_fd(student_file):
    cases = [
        (["hello", "1"], None, "hello", "a plain string"),
        (["", "1"], None, "", "the empty string writes nothing"),
        (["a\tb\nc", "1"], None, "a\tb\nc", "embedded control characters"),
        (["x" * 200, "1"], None, "x" * 200, "a 200-byte string"),
        # Staying off stdout is half of it: a function that writes only
        # when fd == 1 passed, having written nothing at all. The payload
        # has to arrive on the descriptor it was given.
        (["hello", "2"], None, "[]", "fd 2: all of it on stderr, none on stdout",
         "hello"),
    ]
    return run_harness_cases(student_file, FUNCTION, FUNCTION, cases)
