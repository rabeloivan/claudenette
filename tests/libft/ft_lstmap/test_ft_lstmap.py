from ..harness_runner import run_harness_cases, run_allocation_cases

FUNCTION = "ft_lstmap"


def run_libft_ft_lstmap(student_file):
    cases = [
        ([], None, "[AB][CD][EF]|NEW|SOURCEOK|FREED",
         "a new list is built from f applied to each content, "
         "and the original list is left alone"),
        (["1"], None, "[ab][cd][ef]|NEW|SOURCEOK|FREED",
         "identity callback shares contents while allocating independent nodes"),
        (["2"], None, "[][][]|NEW|SOURCEOK|FREED",
         "NULL callback results are valid node contents"),
        (["3"], None, "EMPTY", "mapping an empty list creates no nodes"),
    ]
    behavior_ok = run_harness_cases(
        student_file, FUNCTION, FUNCTION, cases, with_free_tracker=True
    )
    allocation_ok = run_allocation_cases(student_file, FUNCTION)
    return behavior_ok and allocation_ok
