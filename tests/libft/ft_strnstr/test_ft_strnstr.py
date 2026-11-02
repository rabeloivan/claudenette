from ..harness_runner import run_harness_cases

FUNCTION = "ft_strnstr"

H = "lorem ipsum dolor sit amet"


def run_libft_ft_strnstr(student_file):
    cases = [
        ([H, "ipsum", "26"], None, "6", "a needle present once"),
        ([H, "lorem", "26"], None, "0", "a needle at offset 0"),
        ([H, "amet", "26"], None, "22", "a needle at the very end"),
        ([H, "", "26"], None, "0",
         "an empty needle returns the haystack itself"),
        ([H, "xyz", "26"], None, "NULL", "an absent needle returns NULL"),
        ([H, "amet", "24"], None, "NULL",
         "a match starting inside len but running past it does not count"),
        ([H, "ipsum", "5"], None, "NULL", "len stops the search early"),
        (["", "a", "5"], None, "NULL", "no match in an empty haystack"),
        (["", "", "5"], None, "0", "an empty needle matches an empty haystack"),
        ([H, "lorem", "0"], None, "NULL",
         "len of 0 finds nothing, not even at offset 0"),
    ]
    return run_harness_cases(student_file, FUNCTION, FUNCTION, cases)
