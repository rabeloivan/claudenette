# Standard English number-to-words, dictionary-driven - matches the subject's
# own worked examples exactly (42 -> "forty two", 0 -> "zero",
# 100000 -> "one hundred thousand"), confirming plain space-joined output
# with no hyphens/commas/"and" (those are explicitly a bonus: "Using '-',
# ',', 'and' to be closer to the correct written syntax"). Dictionary keys
# are the composable building blocks (0-19, the tens, and each scale word),
# not a literal entry per possible number - the subject's own "20 : hey
# everybody !" example overrides exactly the tens-building-block used when
# the ones digit is 0, not a special-cased whole-number lookup.
ONES = [
    "zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine",
    "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen", "sixteen",
    "seventeen", "eighteen", "nineteen",
]
TENS = {20: "twenty", 30: "thirty", 40: "forty", 50: "fifty", 60: "sixty",
        70: "seventy", 80: "eighty", 90: "ninety"}
SCALE_WORDS = {100: "hundred", 1000: "thousand", 1000000: "million",
               1000000000: "billion", 1000000000000: "trillion"}
# Descending so the biggest scale is peeled off first.
SCALES = [1000000000000, 1000000000, 1000000, 1000, 1]


def default_dictionary():
    d = {i: ONES[i] for i in range(20)}
    d.update(TENS)
    d.update(SCALE_WORDS)
    return d


# Bonus: "doing the same exercise in a different language, using another
# dictionary which will contain the translated entries." Deliberately a
# placeholder vocabulary, not a real language: every real language checked
# while designing this (Portuguese, Spanish, French) has some irregularity
# that breaks the simple "one word per building block, concatenated with a
# space" composition this test's algorithm (and the mandatory English
# examples) both use - a glue word between tens and ones (Portuguese
# "vinte e dois", not "vinte dois"), fused/irregular hundreds
# ("trezentos" for 300, not "três" + "cem"), or a non-decimal tens system
# entirely (French 80 = "quatre-vingts", "four-twenties"). None of that is
# something the bonus actually asks students to implement - "using another
# dictionary" describes a word swap, not per-language grammar rules - so
# asserting output against a real language would risk failing a
# genuinely-correct dictionary-driven implementation over a grammar
# nuance this test has no business requiring. A placeholder vocabulary
# tests exactly the property that matters (does composition genuinely
# come from the given dictionary, for every building block, not just a
# single overridden key) without implying linguistic authority this
# project doesn't have.
PLACEHOLDER_ONES = [
    "nul", "ay", "bo", "ci", "du", "ee", "fu", "gi", "ha", "io",
    "jen", "kra", "lom", "miv", "nix", "opa", "pyx", "quo", "rez", "syn",
]
PLACEHOLDER_TENS = {20: "tigo", 30: "trigo", 40: "quadrigo", 50: "pentigo",
                     60: "hexigo", 70: "septigo", 80: "octigo", 90: "nonigo"}
PLACEHOLDER_SCALE_WORDS = {100: "kem", 1000: "mil", 1000000: "meg",
                            1000000000: "gig", 1000000000000: "ter"}


def placeholder_dictionary():
    d = {i: PLACEHOLDER_ONES[i] for i in range(20)}
    d.update(PLACEHOLDER_TENS)
    d.update(PLACEHOLDER_SCALE_WORDS)
    return d


def dictionary_to_file_content(dictionary):
    return "".join(f"{key} : {dictionary[key]}\n" for key in sorted(dictionary))


def _group_to_words(g, d):
    # g is 0-999 (one 3-digit group). Raises KeyError for a missing
    # building block - number_to_words below turns that into None (the
    # "Dict Error" signal), never lets it propagate as a crash.
    parts = []
    hundreds, rest = divmod(g, 100)
    if hundreds:
        parts.append(d[hundreds])
        parts.append(d[100])
    if rest:
        if rest < 20:
            parts.append(d[rest])
        else:
            tens, ones = divmod(rest, 10)
            parts.append(d[tens * 10])
            if ones:
                parts.append(d[ones])
    return parts


def number_to_words(n, dictionary=None):
    # Returns None for "Dict Error" (a building block the conversion
    # actually needs is missing from the dictionary) rather than raising,
    # so callers can test the Dict-Error path the same way as any other
    # expected output.
    d = dictionary if dictionary is not None else default_dictionary()
    try:
        if n == 0:
            return d[0]
        words = []
        remaining = n
        for scale in SCALES:
            group, remaining = divmod(remaining, scale)
            if group == 0:
                continue
            group_words = _group_to_words(group, d)
            if scale != 1:
                group_words.append(d[scale])
            words.extend(group_words)
        return " ".join(words)
    except KeyError:
        return None
