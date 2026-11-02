from ..harness_runner import run_harness_cases

FUNCTION = "ft_lstsize"


def run_libft_ft_lstsize(student_file):
    cases = [
        (["0"], None, "0", "an empty list (NULL) has size 0"),
        (["1"], None, "1", "a single node"),
        (["2"], None, "2", "two nodes"),
        (["8"], None, "8", "eight nodes"),
    ]
    return run_harness_cases(student_file, FUNCTION, FUNCTION, cases)
