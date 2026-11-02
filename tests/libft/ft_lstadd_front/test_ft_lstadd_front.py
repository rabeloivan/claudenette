from ..harness_runner import run_harness_cases

FUNCTION = "ft_lstadd_front"


def run_libft_ft_lstadd_front(student_file):
    cases = [
        (["0"], None, "[new]",
         "adding to an empty list makes the new node the head"),
        (["1"], None, "[new][a][b]",
         "the new node goes at the FRONT and the old head follows"),
    ]
    return run_harness_cases(student_file, FUNCTION, FUNCTION, cases)
