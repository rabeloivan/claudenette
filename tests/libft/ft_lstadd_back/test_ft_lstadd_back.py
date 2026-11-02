from ..harness_runner import run_harness_cases

FUNCTION = "ft_lstadd_back"


def run_libft_ft_lstadd_back(student_file):
    cases = [
        (["0"], None, "[new]",
         "adding to an empty list makes the new node the head"),
        (["1"], None, "[a][b][new]",
         "the new node goes at the END, after the existing ones"),
    ]
    return run_harness_cases(student_file, FUNCTION, FUNCTION, cases)
