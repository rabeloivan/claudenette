"""Oracle for shell01 ex08 (add_chelou).

The subject (en.shell01.pdf ch. XII) gives three bases by example rather than by
name, so they're transcribed here verbatim:

    FT_NBR1  is written in base  '\\"?!
    FT_NBR2  is written in base  mrdoc
    the sum is printed in base   gtaio luSnemf   (note: the 6th digit is a space)

The three bases are pinned by the subject's first worked example
(FT_NBR1=\\'?"\\"'\\ + FT_NBR2=rcrdmddd -> "Salut"), which these strings reproduce
exactly; test_ex08.py re-asserts that at grading time so a bad edit to this file
fails loudly instead of silently mis-grading.

A note on the second example, whose FT_NBR1 is a dense run of escaped quotes: read
straight off the rendered PDF it does NOT produce the subject's stated output. Its
true value was recovered by solving (expected_output - FT_NBR2), giving the clean
repeating pattern \\"\\"! x5 + \\"\\" - i.e. the first reading had dropped one \\"
from each group. That recovery is only sound because the bases were already fixed
independently by example 1; it re-derives a hard-to-read input, not the encoding.

Computing the expected answer rather than hardcoding it follows tests/rush02/numbers.py.
"""

BASE_NBR1 = "'\\\"?!"
BASE_NBR2 = "mrdoc"
BASE_OUT = "gtaio luSnemf"


def is_valid(value, base):
    # An empty string has no digits at all, so it isn't a number in any base.
    if not value:
        return False
    return all(c in base for c in value)


def to_int(value, base):
    n = 0
    for c in value:
        n = n * len(base) + base.index(c)
    return n


def to_base(n, base):
    if n == 0:
        return base[0]
    digits = []
    while n:
        digits.append(base[n % len(base)])
        n //= len(base)
    return "".join(reversed(digits))


def expected_output(nbr1, nbr2):
    """The line add_chelou.sh should print, or None if the input is invalid.

    Returning None models "the subject shows no defined output for this", which
    the test treats as 'anything but a plausible number' rather than pinning an
    exact string - the subject never specifies an error message.
    """
    if not is_valid(nbr1, BASE_NBR1) or not is_valid(nbr2, BASE_NBR2):
        return None
    return to_base(to_int(nbr1, BASE_NBR1) + to_int(nbr2, BASE_NBR2), BASE_OUT)
