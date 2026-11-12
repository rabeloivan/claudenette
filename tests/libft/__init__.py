import os
import re

from .ft_atoi.test_ft_atoi import run_libft_ft_atoi
from .ft_bzero.test_ft_bzero import run_libft_ft_bzero
from .ft_calloc.test_ft_calloc import run_libft_ft_calloc
from .ft_isalnum.test_ft_isalnum import run_libft_ft_isalnum
from .ft_isalpha.test_ft_isalpha import run_libft_ft_isalpha
from .ft_isascii.test_ft_isascii import run_libft_ft_isascii
from .ft_isdigit.test_ft_isdigit import run_libft_ft_isdigit
from .ft_isprint.test_ft_isprint import run_libft_ft_isprint
from .ft_itoa.test_ft_itoa import run_libft_ft_itoa
from .ft_lstadd_back.test_ft_lstadd_back import run_libft_ft_lstadd_back
from .ft_lstadd_front.test_ft_lstadd_front import run_libft_ft_lstadd_front
from .ft_lstclear.test_ft_lstclear import run_libft_ft_lstclear
from .ft_lstdelone.test_ft_lstdelone import run_libft_ft_lstdelone
from .ft_lstiter.test_ft_lstiter import run_libft_ft_lstiter
from .ft_lstlast.test_ft_lstlast import run_libft_ft_lstlast
from .ft_lstmap.test_ft_lstmap import run_libft_ft_lstmap
from .ft_lstnew.test_ft_lstnew import run_libft_ft_lstnew
from .ft_lstsize.test_ft_lstsize import run_libft_ft_lstsize
from .ft_memchr.test_ft_memchr import run_libft_ft_memchr
from .ft_memcmp.test_ft_memcmp import run_libft_ft_memcmp
from .ft_memcpy.test_ft_memcpy import run_libft_ft_memcpy
from .ft_memmove.test_ft_memmove import run_libft_ft_memmove
from .ft_memset.test_ft_memset import run_libft_ft_memset
from .ft_putchar_fd.test_ft_putchar_fd import run_libft_ft_putchar_fd
from .ft_putendl_fd.test_ft_putendl_fd import run_libft_ft_putendl_fd
from .ft_putnbr_fd.test_ft_putnbr_fd import run_libft_ft_putnbr_fd
from .ft_putstr_fd.test_ft_putstr_fd import run_libft_ft_putstr_fd
from .ft_split.test_ft_split import run_libft_ft_split
from .ft_strchr.test_ft_strchr import run_libft_ft_strchr
from .ft_striteri.test_ft_striteri import run_libft_ft_striteri
from .ft_strmapi.test_ft_strmapi import run_libft_ft_strmapi
from .ft_strdup.test_ft_strdup import run_libft_ft_strdup
from .ft_strjoin.test_ft_strjoin import run_libft_ft_strjoin
from .ft_strlcat.test_ft_strlcat import run_libft_ft_strlcat
from .ft_strlcpy.test_ft_strlcpy import run_libft_ft_strlcpy
from .ft_strlen.test_ft_strlen import run_libft_ft_strlen
from .ft_strncmp.test_ft_strncmp import run_libft_ft_strncmp
from .ft_strnstr.test_ft_strnstr import run_libft_ft_strnstr
from .ft_strtrim.test_ft_strtrim import run_libft_ft_strtrim
from .ft_substr.test_ft_substr import run_libft_ft_substr
from .libft_h.test_libft_h import run_libft_libft_h
from .makefile.test_makefile import run_libft_makefile
from .ft_strrchr.test_ft_strrchr import run_libft_ft_strrchr
from .ft_tolower.test_ft_tolower import run_libft_ft_tolower
from .ft_toupper.test_ft_toupper import run_libft_ft_toupper

# Unlike every Piscine module, libft is graded at the root of the student's git
# REPOSITORY, not in an exercise subdirectory - the subject says so twice
# ("All files must be placed at the root of your repository", and again in a
# red warning box). Two consequences for the extra-files check:
#
#   1. .git is repository metadata. It is accepted explicitly but omitted from
#      the displayed deliverables. Other dotfiles are checked normally.
#   2. A file key checks its own directory allowing at least its own basename,
#      and here every key shares one directory. So each entry needs the FULL
#      list or it would report its 40-odd siblings as extras - hence one
#      constant applied to all of them.
#
# "ft_*.c" rather than "*.c" is deliberate: the subject's file list is
# "Makefile, libft.h, ft_*.c" and "submitting unused files is not allowed", so
# a stray main.c or test.c is a real finding, not noise.
ALLOWED_FILES = [
    "Makefile",
    "libft.h",
    "ft_*.c",
    "README.md",
    ".git",
]
TURN_IN_FILES = [name for name in ALLOWED_FILES if name != '.git']

# (function name, run_func, allowed external functions, extra options)
#
# "Allowed external functions" comes from each function's own "External
# Function" row in the subject. Part 1 says the reimplementations "must not
# rely on any external functions", so those are empty except calloc and
# strdup, which the subject introduces with "In order to implement the two
# following functions, you will use malloc()".
#
# strict_symbols re-enables checking for a name that COMPILER_ARTIFACTS
# normally excuses. Those four exclusions exist because the compiler can
# synthesise calls to memcpy/memset/memmove/bzero that the student never
# wrote; libft is the one module where they are also mandatory deliverables,
# so without this an ft_memset whose body is `return (memset(s, c, n));`
# passes silently. See utils/functions.py.
PRESERVE_ORDER = True

# Subject 19.3, read down each column in Part 1. All three parts are mandatory.
_PART1 = [
    ("ft_isalpha", run_libft_ft_isalpha, [], {}),
    ("ft_isdigit", run_libft_ft_isdigit, [], {}),
    ("ft_isalnum", run_libft_ft_isalnum, [], {}),
    ("ft_isascii", run_libft_ft_isascii, [], {}),
    ("ft_isprint", run_libft_ft_isprint, [], {}),
    ("ft_strlen", run_libft_ft_strlen, [], {}),
    ("ft_memset", run_libft_ft_memset, [], {"strict_symbols": ["memset"]}),
    ("ft_bzero", run_libft_ft_bzero, [], {"strict_symbols": ["bzero", "memset"]}),
    ("ft_memcpy", run_libft_ft_memcpy, [], {"strict_symbols": ["memcpy"]}),
    ("ft_memmove", run_libft_ft_memmove, [],
        {"strict_symbols": ["memmove", "memcpy"]}),
    ("ft_strlcpy", run_libft_ft_strlcpy, [], {}),
    ("ft_strlcat", run_libft_ft_strlcat, [], {}),
    ("ft_toupper", run_libft_ft_toupper, [], {}),
    ("ft_tolower", run_libft_ft_tolower, [], {}),
    ("ft_strchr", run_libft_ft_strchr, [], {}),
    ("ft_strrchr", run_libft_ft_strrchr, [], {}),
    ("ft_strncmp", run_libft_ft_strncmp, [], {}),
    ("ft_memchr", run_libft_ft_memchr, [], {}),
    ("ft_memcmp", run_libft_ft_memcmp, [], {}),
    ("ft_strnstr", run_libft_ft_strnstr, [], {}),
    ("ft_atoi", run_libft_ft_atoi, [], {}),
    ("ft_calloc", run_libft_ft_calloc, ["malloc"], {}),
    ("ft_strdup", run_libft_ft_strdup, ["malloc"], {}),
]

_PART2 = [
    ("ft_substr", run_libft_ft_substr, ["malloc"], {}),
    ("ft_strjoin", run_libft_ft_strjoin, ["malloc"], {}),
    ("ft_strtrim", run_libft_ft_strtrim, ["malloc"], {}),
    ("ft_split", run_libft_ft_split, ["malloc", "free"], {}),
    ("ft_itoa", run_libft_ft_itoa, ["malloc"], {}),
    ("ft_strmapi", run_libft_ft_strmapi, ["malloc"], {}),
    ("ft_striteri", run_libft_ft_striteri, [], {}),
    ("ft_putchar_fd", run_libft_ft_putchar_fd, ["write"], {}),
    ("ft_putstr_fd", run_libft_ft_putstr_fd, ["write"], {}),
    ("ft_putendl_fd", run_libft_ft_putendl_fd, ["write"], {}),
    ("ft_putnbr_fd", run_libft_ft_putnbr_fd, ["write"], {}),
]

_PART3 = [
    ("ft_lstnew", run_libft_ft_lstnew, ["malloc"], {}),
    ("ft_lstadd_front", run_libft_ft_lstadd_front, [], {}),
    ("ft_lstsize", run_libft_ft_lstsize, [], {}),
    ("ft_lstlast", run_libft_ft_lstlast, [], {}),
    ("ft_lstadd_back", run_libft_ft_lstadd_back, [], {}),
    ("ft_lstdelone", run_libft_ft_lstdelone, ["free"], {}),
    ("ft_lstclear", run_libft_ft_lstclear, ["free"], {}),
    ("ft_lstiter", run_libft_ft_lstiter, [], {}),
    ("ft_lstmap", run_libft_ft_lstmap, ["malloc", "free"], {}),
]

README_FIRST_LINE = re.compile(
    r"^([*_])This project has been created as part of the 42 curriculum by \S.*\1\.?$"
)
README_SECTIONS = ("Description", "Instructions", "Resources")


def get_advisories():
    """What README.md lacks, per the subject's "Readme Requirements" chapter.

    "A README.md file must be provided at the root of your Git repository",
    its very first line italicised and reading "This project has been created
    as part of the 42 curriculum by <login1>[, <login2>...]", with
    "Description", "Instructions" and "Resources" sections. Peers check this
    at the defense, not the moulinette, so it is reported as advice and never
    changes the score. Like get_mapping(), runs with the student's directory
    as cwd.
    """
    if not os.path.isfile("README.md"):
        return ["README.md is missing; the subject requires one at the repository root."]
    with open("README.md", encoding="utf-8", errors="replace") as handle:
        lines = handle.read().splitlines()
    notes = []
    if not lines or not README_FIRST_LINE.match(lines[0].strip()):
        notes.append(
            "README.md: the very first line must be italic and read "
            "\"This project has been created as part of the 42 curriculum by <login>\"."
        )
    for section in README_SECTIONS:
        heading = re.compile(r"^#{1,6}\s*" + section + r"\b", re.IGNORECASE)
        if not any(heading.match(line.strip()) for line in lines):
            notes.append(f"README.md has no \"{section}\" section.")
    return notes


def _build(entries):
    mapping = {}
    for name, run_func, allowed_fns, extra in entries:
        options = {"allowed_files": ALLOWED_FILES, "turn_in_files": TURN_IN_FILES}
        options.update(extra)
        mapping[f"{name}.c"] = (name, run_func, allowed_fns, options)
    return mapping


def get_mapping():
    # The header is checked before the functions, followed by Parts 1, 2 and 3.
    # main.py preserves this insertion order for this module, including filters.
    mapping = {
        "Makefile": (
            "Makefile", run_libft_makefile, [],
            {"allowed_files": ALLOWED_FILES, "turn_in_files": TURN_IN_FILES, "skip_precheck": True},
        ),
        "libft.h": (
            "libft.h", run_libft_libft_h, [],
            {"allowed_files": ALLOWED_FILES, "turn_in_files": TURN_IN_FILES},
        ),
    }
    mapping.update(_build(_PART1 + _PART2 + _PART3))
    return mapping
