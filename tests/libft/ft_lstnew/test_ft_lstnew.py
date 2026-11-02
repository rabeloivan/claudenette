from ..harness_runner import run_harness_cases, run_allocation_cases

FUNCTION = "ft_lstnew"


def run_libft_ft_lstnew(student_file):
    cases = [
        # The subject: "The 'content' member variable is initialized with the
        # given parameter 'content'." It is stored, not duplicated - so the
        # pointer must come back identical, and a node that strdup'd it is
        # wrong (and would leak).
        (["hello"], None, "[hello]|SAMEPTR|NEXTNULL",
         "content is stored as given and next is initialised to NULL"),
        ([""], None, "[]|SAMEPTR|NEXTNULL", "an empty string as content"),
    ]
    behavior_ok = run_harness_cases(
        student_file, FUNCTION, FUNCTION, cases, with_free_tracker=True
    )
    allocation_ok = run_allocation_cases(student_file, FUNCTION)
    return behavior_ok and allocation_ok
