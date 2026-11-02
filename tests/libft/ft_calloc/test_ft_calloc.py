from ..harness_runner import run_harness_cases, run_allocation_cases

FUNCTION = "ft_calloc"

ZEROS = "00" * 16


def run_libft_ft_calloc(student_file):
    cases = [
        (["0"], None, ZEROS, "16 bytes are actually zeroed, not merely allocated"),
        (["1"], None, ZEROS, "count * size is the byte count (4 * 4 = 16)"),
        # The subject overrides the man page here: "If nmemb or size is 0, then
        # calloc() returns a unique pointer value that can be successfully
        # passed to free()." Returning NULL is a real failure, not a variant.
        (["2"], None, "NONNULL", "calloc(0, 0) returns a freeable pointer, not NULL"),
        (["3"], None, "NONNULL", "calloc(0, 5) returns a freeable pointer, not NULL"),
        # "If the multiplication of nmemb and size would result in integer
        # overflow, then calloc() returns an error" (calloc(3)) - which is the
        # difference between calloc and malloc(nmemb * size): the product
        # wraps to a few bytes, and the caller is handed a block far smaller
        # than it asked for. Both libcs return NULL here.
        (["4"], None, "NULL", "calloc(SIZE_MAX / 2 + 2, 2), whose product wraps, returns NULL"),
        (["5"], None, "NULL", "calloc(SIZE_MAX, SIZE_MAX), whose product wraps, returns NULL"),
    ]
    behavior_ok = run_harness_cases(
        student_file, FUNCTION, FUNCTION, cases, with_free_tracker=True
    )
    allocation_ok = run_allocation_cases(student_file, FUNCTION)
    return behavior_ok and allocation_ok
