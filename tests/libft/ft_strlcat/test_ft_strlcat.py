from ..harness_runner import run_harness_cases

FUNCTION = "ft_strlcat"


def _expected(dst_init, src, dstsize):
    # Model of strlcat(3): append src to dst, writing at most dstsize-1 bytes
    # total and always terminating. The return value is the length it TRIED to
    # create - initial dst length plus src length - except that when dstsize is
    # smaller than the existing dst length, dst is not a string within the
    # buffer at all, and the return is dstsize + strlen(src).
    buf = [0x2A] * 16
    for i, ch in enumerate(dst_init):
        buf[i] = ord(ch)
    buf[len(dst_init)] = 0x00

    dlen = len(dst_init)
    if dstsize <= dlen:
        ret = dstsize + len(src)
    else:
        ret = dlen + len(src)
        room = dstsize - dlen - 1
        appended = min(len(src), room)
        for i in range(appended):
            buf[dlen + i] = ord(src[i])
        buf[dlen + appended] = 0x00
    dump = "".join(f"{b:02x}" for b in buf)
    return f"{ret}|{dump}"


def run_libft_ft_strlcat(student_file):
    cases = [
        (["ab", "cd", "16"], None, _expected("ab", "cd", 16),
         "an append that fits"),
        (["ab", "cdef", "5"], None, _expected("ab", "cdef", 5),
         "truncation still returns the length it tried to build"),
        (["abc", "de", "3"], None, _expected("abc", "de", 3),
         "dstsize equal to the existing length appends nothing"),
        (["abcde", "xy", "2"], None, _expected("abcde", "xy", 2),
         "dstsize smaller than dst: returns dstsize + srclen, dst untouched"),
        (["ab", "", "16"], None, _expected("ab", "", 16), "an empty source"),
        (["", "abc", "16"], None, _expected("", "abc", 16),
         "appending to an empty dst behaves like a copy"),
        (["ab", "cd", "0"], None, _expected("ab", "cd", 0),
         "dstsize of 0 returns srclen and touches nothing"),
    ]
    return run_harness_cases(student_file, FUNCTION, FUNCTION, cases)
