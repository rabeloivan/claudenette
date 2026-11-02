from ..harness_runner import run_harness_cases

FUNCTION = "ft_lstlast"


def run_libft_ft_lstlast(student_file):
    cases = [
        (["0"], None, "NULL", "an empty list returns NULL"),
        (["1"], None, "0", "a single node is its own last"),
        (["2"], None, "1", "the second of two nodes"),
        (["8"], None, "7", "the eighth of eight nodes"),
    ]
    return run_harness_cases(student_file, FUNCTION, FUNCTION, cases)
