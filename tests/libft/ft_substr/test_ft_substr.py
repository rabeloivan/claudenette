from ..harness_runner import run_harness_cases, run_allocation_cases

FUNCTION = "ft_substr"


def _expected(s, start, length):
    # Result is bracketed by the harness so an empty string is distinguishable
    # from a NULL return, which is a different failure entirely.
    return "[" + s[start:start + length] + "]"


def run_libft_ft_substr(student_file):
    cases = [
        (["hello world", "6", "5"], None, _expected("hello world", 6, 5),
         "a substring from the middle"),
        (["hello", "0", "5"], None, _expected("hello", 0, 5),
         "the whole string"),
        (["hello", "1", "100"], None, _expected("hello", 1, 100),
         "len longer than what remains is clamped, not read past"),
        (["hello", "0", "0"], None, "[]", "len of 0 gives an empty string"),
        # The subject does not spell this out, but reading from beyond the end
        # would be a buffer overrun, so the only safe answer is an empty
        # string - and it must still be a real allocation, not NULL.
        (["abc", "10", "5"], None, "[]",
         "start beyond the end gives an empty string, not NULL"),
        (["abc", "3", "5"], None, "[]",
         "start exactly at the terminator gives an empty string"),
        (["", "0", "5"], None, "[]", "an empty source"),
        (["hello", "4", "1"], None, _expected("hello", 4, 1),
         "the final character"),
        # "-1" reaches ft_substr as SIZE_MAX (the harness casts to size_t).
        # Clamped first, it is just "the rest of the string". Used first, it
        # overflows: malloc(len + 1) wraps to malloc(0), and a
        # `start + len > slen` bound wraps below slen and never clamps.
        (["hello", "1", "-1"], None, _expected("hello", 1, len("hello")),
         "len of SIZE_MAX is clamped to the rest of the string, not overflowed"),
    ]
    behavior_ok = run_harness_cases(
        student_file, FUNCTION, FUNCTION, cases, with_free_tracker=True
    )
    allocation_ok = run_allocation_cases(student_file, FUNCTION)
    return behavior_ok and allocation_ok
