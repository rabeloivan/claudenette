from ..harness_runner import run_harness_cases

FUNCTION = "ft_memmove"


def _dump(byte_values):
    return "".join(f"{b:02x}" for b in byte_values)


def _moved(dst, src, length):
    buf = list(range(16))
    chunk = buf[src:src + length]
    buf[dst:dst + length] = chunk
    return _dump(buf) + "|R1"


def run_libft_ft_memmove(student_file):
    cases = [
        (["0"], None, _moved(4, 0, 8),
         "overlap with dst > src (a naive forward copy corrupts the tail)"),
        (["1"], None, _moved(0, 4, 8),
         "overlap with dst < src (a naive backward copy corrupts it)"),
        (["2"], None, _moved(2, 2, 6), "dst == src leaves the buffer unchanged"),
        (["3"], None, _dump(list(range(16))) + "|R1", "len of 0 moves nothing"),
    ]
    return run_harness_cases(student_file, FUNCTION, FUNCTION, cases)
