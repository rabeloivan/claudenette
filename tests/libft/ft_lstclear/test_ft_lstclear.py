from ..harness_runner import run_harness_cases

FUNCTION = "ft_lstclear"


def run_libft_ft_lstclear(student_file):
    cases = [
        ([], None, "3|0|HEADNULL",
         "del runs on all three contents, nothing is leaked, "
         "and the head pointer is set to NULL"),
    ]
    return run_harness_cases(
        student_file, FUNCTION, FUNCTION, cases, with_free_tracker=True
    )
