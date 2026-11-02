from ..harness_runner import run_harness_cases

FUNCTION = "ft_strlcpy"


def _expected(dst_init, src, dstsize):
    # Model of strlcpy(3): copy at most dstsize-1 bytes and always NUL
    # terminate (unless dstsize is 0, when dst is untouched); return the
    # length of src regardless of how much fitted. That return value is the
    # part students most often get wrong - returning the copied length makes
    # every non-truncating case look right.
    buf = [0x2A] * 16
    for i, ch in enumerate(dst_init):
        buf[i] = ord(ch)
    buf[len(dst_init)] = 0x00

    if dstsize > 0:
        copied = min(len(src), dstsize - 1)
        for i in range(copied):
            buf[i] = ord(src[i])
        buf[copied] = 0x00
    dump = "".join(f"{b:02x}" for b in buf)
    return f"{len(src)}|{dump}"


def run_libft_ft_strlcpy(student_file):
    cases = [
        (["", "hello", "16"], None, _expected("", "hello", 16),
         "a copy that fits"),
        (["", "hello", "3"], None, _expected("", "hello", 3),
         "truncation still returns the full source length"),
        (["", "hello", "1"], None, _expected("", "hello", 1),
         "dstsize of 1 writes only the terminator"),
        (["abcdefg", "hello", "0"], None, _expected("abcdefg", "hello", 0),
         "dstsize of 0 leaves dst untouched and returns srclen"),
        (["", "", "8"], None, _expected("", "", 8), "an empty source"),
        (["xxxx", "ab", "8"], None, _expected("xxxx", "ab", 8),
         "the terminator lands right after the copy, not at the old end"),
    ]
    return run_harness_cases(student_file, FUNCTION, FUNCTION, cases)
