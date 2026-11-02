from ..harness_runner import run_harness_cases, run_allocation_cases

FUNCTION = "ft_split"

CASES = [
    ("hello world", " ", ["hello", "world"], "two words"),
    ("  hello   world  ", " ", ["hello", "world"],
     "leading, trailing and repeated delimiters produce no empty elements"),
    ("abc", ",", ["abc"], "no delimiter present gives a single element"),
    ("", " ", [], "an empty string gives an array holding only the terminator"),
    ("///", "/", [], "a string of only delimiters gives an empty array"),
    (",a,", ",", ["a"], "delimiters at both ends"),
    ("a b c d e", " ", ["a", "b", "c", "d", "e"], "five single-character words"),
    ("one", "\n", ["one"], "a delimiter that never appears"),
    ("aXbXXcX", "X", ["a", "b", "c"], "an uppercase delimiter with a run"),
    ("  ", " ", [], "only spaces"),
    # The harness passes argv[2][0], so "" is c == '\0'. The only '\0' in
    # the string is its terminator, so the whole string is one word - and a
    # delimiter-skipping loop without its own end-of-string check,
    # `while (s[i] == c) i++;`, walks straight past that terminator.
    ("hello world", "", ["hello world"], "c == '\\0': the whole string is one word"),
    ("", "", [], "c == '\\0' on an empty string"),
]


def run_libft_ft_split(student_file):
    cases = [
        (
            [text, delim],
            None,
            "".join(f"[{part}]" for part in parts) + f"|{len(parts)}",
            f"ft_split with {description}",
        )
        for text, delim, parts, description in CASES
    ]
    behavior_ok = run_harness_cases(
        student_file, FUNCTION, FUNCTION, cases, with_free_tracker=True
    )
    allocation_ok = run_allocation_cases(student_file, FUNCTION)
    return behavior_ok and allocation_ok
