from ..harness_runner import run_harness_cases

FUNCTION = "ft_lstdelone"


def run_libft_ft_lstdelone(student_file):
    cases = [
        ([], None, "1|1|1|0",
         "del is called once, the node and its content are freed, "
         "and the next node is left alone"),
    ]
    return run_harness_cases(
        student_file, FUNCTION, FUNCTION, cases, with_free_tracker=True
    )
