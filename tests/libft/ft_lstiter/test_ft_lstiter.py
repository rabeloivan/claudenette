from ..harness_runner import run_harness_cases

FUNCTION = "ft_lstiter"


def run_libft_ft_lstiter(student_file):
    cases = [
        (["1"], None, "[AB][CD][EF]",
         "f is applied to every node's content, not just the first"),
        (["0"], None, "[ab][cd][ef]",
         "a NULL list is a no-op rather than a crash"),
    ]
    return run_harness_cases(student_file, FUNCTION, FUNCTION, cases)
