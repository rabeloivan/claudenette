import glob
import os
import shutil
import subprocess
import tempfile

from utils.functions import get_defined_functions
from utils.ui import (
    print_command_execution,
    print_exercise_result,
    print_test_fail,
    print_test_pass,
)

from ..harness_runner import uses_restrict

# The 43 mandatory prototypes, spelled the way the subject spells them. Part 1
# is "the same prototypes and behaviors as the originals", minus `restrict`,
# which the subject forbids in your own prototypes; Part 2 is copied from each
# function's own table (hence `char const *`).
#
# (name, return type, parameter list)
PROTOTYPES = [
    ("ft_isalpha", "int", "int c"),
    ("ft_isdigit", "int", "int c"),
    ("ft_isalnum", "int", "int c"),
    ("ft_isascii", "int", "int c"),
    ("ft_isprint", "int", "int c"),
    ("ft_strlen", "size_t", "const char *s"),
    ("ft_memset", "void *", "void *b, int c, size_t len"),
    ("ft_bzero", "void", "void *s, size_t n"),
    ("ft_memcpy", "void *", "void *dst, const void *src, size_t n"),
    ("ft_memmove", "void *", "void *dst, const void *src, size_t len"),
    ("ft_strlcpy", "size_t", "char *dst, const char *src, size_t dstsize"),
    ("ft_strlcat", "size_t", "char *dst, const char *src, size_t dstsize"),
    ("ft_toupper", "int", "int c"),
    ("ft_tolower", "int", "int c"),
    ("ft_strchr", "char *", "const char *s, int c"),
    ("ft_strrchr", "char *", "const char *s, int c"),
    ("ft_strncmp", "int", "const char *s1, const char *s2, size_t n"),
    ("ft_memchr", "void *", "const void *s, int c, size_t n"),
    ("ft_memcmp", "int", "const void *s1, const void *s2, size_t n"),
    ("ft_strnstr", "char *", "const char *haystack, const char *needle, size_t len"),
    ("ft_atoi", "int", "const char *str"),
    ("ft_calloc", "void *", "size_t count, size_t size"),
    ("ft_strdup", "char *", "const char *s1"),
    ("ft_substr", "char *", "char const *s, unsigned int start, size_t len"),
    ("ft_strjoin", "char *", "char const *s1, char const *s2"),
    ("ft_strtrim", "char *", "char const *s1, char const *set"),
    ("ft_split", "char **", "char const *s, char c"),
    ("ft_itoa", "char *", "int n"),
    ("ft_strmapi", "char *", "char const *s, char (*f)(unsigned int, char)"),
    ("ft_striteri", "void", "char *s, void (*f)(unsigned int, char *)"),
    ("ft_putchar_fd", "void", "char c, int fd"),
    ("ft_putstr_fd", "void", "char *s, int fd"),
    ("ft_putendl_fd", "void", "char *s, int fd"),
    ("ft_putnbr_fd", "void", "int n, int fd"),
    ("ft_lstnew", "t_list *", "void *content"),
    ("ft_lstadd_front", "void", "t_list **lst, t_list *new"),
    ("ft_lstsize", "unsigned int", "t_list *lst"),
    ("ft_lstlast", "t_list *", "t_list *lst"),
    ("ft_lstadd_back", "void", "t_list **lst, t_list *new"),
    ("ft_lstdelone", "void", "t_list *lst, void (*del)(void *)"),
    ("ft_lstclear", "void", "t_list **lst, void (*del)(void *)"),
    ("ft_lstiter", "void", "t_list *lst, void (*f)(void *)"),
    ("ft_lstmap", "t_list *", "t_list *lst, void *(*f)(void *), void (*del)(void *)"),
]

CFLAGS = ["-Wall", "-Wextra", "-Werror"]


def _prototype(name, ret, params):
    sep = "" if ret.endswith("*") else " "
    return f"{ret}{sep}{name}({params});"


def _pointer_check(name, ret, params):
    # A typed function pointer initialised from the declaration. C requires a
    # diagnostic when the types are incompatible, and -Werror makes it fatal,
    # so this line compiles only if libft.h declares the function with the
    # subject's prototype. Parameter NAMES are allowed in a pointer declarator
    # and ignored, as are top-level qualifiers - so `char const *` versus
    # `const char *`, or `size_t` versus `unsigned long` on LP64, never trip it.
    return f"{ret} (*g_{name})({params}) = {name};"


def _compile(student_dir, build_dir, body, label):
    source = os.path.join(build_dir, f"{label}.c")
    with open(source, "w") as handle:
        handle.write('#include "libft.h"\n\n' + body + "\n")
    result = subprocess.run(
        ["cc"] + CFLAGS + ["-I", ".", "-c", source,
                           "-o", os.path.join(build_dir, f"{label}.o")],
        cwd=student_dir,
        capture_output=True,
        text=True,
    )
    first_error = ""
    for line in result.stderr.splitlines():
        if "error" in line:
            first_error = line.replace(source, "libft.h test").strip()
            break
    return result.returncode == 0, first_error


def _turned_in(student_dir):
    """The mandatory functions this submission contains.

    Used only to word a missing declaration, not to decide whether it counts:
    libft.h must declare all 43 regardless, because that is what the subject
    asks of the header. But "you wrote ft_strchr.c and forgot to declare it" is
    a bug to fix now, while "ft_strchr isn't written yet" is just progress -
    and a work-in-progress run is mostly the second kind, so conflating them
    buries the one that matters.

    A function counts as turned in if its ft_<name>.c exists (even empty - the
    intent is plain) or if any ft_*.c defines it (covering a function written
    in another file). Intersected with the mandatory list, so a non-static
    helper never appears here.
    """
    names = {name for name, _, _ in PROTOTYPES}
    present = {n for n in names if os.path.isfile(os.path.join(student_dir, f"{n}.c"))}
    for path in glob.glob(os.path.join(student_dir, "ft_*.c")):
        present |= get_defined_functions(path) & names
    return present


def run_libft_libft_h(student_file):
    student_dir = os.path.dirname(os.path.abspath(student_file)) or "."
    # All 43, always. The subject asks libft.h to declare the library, so a
    # function that isn't declared yet is a real shortfall even while its .c
    # is still ABSENT - the header's verdict reflects the header. What the
    # report must do is make the correct declarations obvious rather than
    # burying them: one line per function, a tick for each one already right.
    required = PROTOTYPES
    turned_in = _turned_in(student_dir)

    print_command_execution(
        f"cc {' '.join(CFLAGS)} -I . -c libft.h "
        f"(checking it declares all {len(required)} mandatory functions)"
    )

    build_dir = tempfile.mkdtemp(prefix="claudenette_libft_h_")
    try:
        total = 1 + len(required) + 1
        passed = 0

        # 1. Self-contained. Evaluation mains typically include only libft.h,
        #    so a header that leans on its includer - say, using size_t with no
        #    <stddef.h> of its own - builds fine alongside your .c files and
        #    breaks everything else. It is also the precondition for the
        #    per-function checks below to mean anything.
        ok, error = _compile(student_dir, build_dir, "", "standalone")
        if ok:
            print_test_pass(1, "libft.h compiles on its own")
            passed += 1
        else:
            print_test_fail(
                1,
                "libft.h does not compile on its own, so a test that includes "
                "only libft.h fails",
                actual=error or None,
            )
            print_exercise_result("libft.h", 0, total)
            return False

        # 2. Every mandatory function is declared, with the subject's
        #    prototype. One combined compile covers a finished header; only when
        #    it fails is each function compiled alone - which is what turns a
        #    truncated wall of compiler errors into one precise line each, and
        #    lets the ones already right show as right.
        combined = "\n".join(_pointer_check(*p) for p in required)
        all_ok, _ = _compile(student_dir, build_dir, combined, "combined")

        for index, (name, ret, params) in enumerate(required, start=2):
            expected = _prototype(name, ret, params)
            if all_ok or _compile(student_dir, build_dir,
                                  _pointer_check(name, ret, params), name)[0]:
                print_test_pass(index, f"{name} declared with the subject's prototype")
                passed += 1
                continue

            declared, _ = _compile(
                student_dir, build_dir,
                f"unsigned long g_probe = sizeof(&{name});", f"{name}_probe",
            )
            if declared:
                description = f"{name}: libft.h declares it with a different prototype"
            elif name not in turned_in:
                description = f"{name}: not declared in libft.h ({name}.c not turned in yet)"
            elif os.path.isfile(os.path.join(student_dir, f"{name}.c")):
                description = (
                    f"{name}: you turned in {name}.c, but libft.h does not declare it"
                )
            else:
                description = (
                    f"{name}: your sources define it, but libft.h does not declare it"
                )
            print_test_fail(index, description, expected=expected)

        # 3. "it is forbidden to include [restrict] in your own prototypes" -
        #    the typed pointers above ignore qualifiers, so this is separate.
        if uses_restrict(student_file):
            print_test_fail(total, "libft.h declares a prototype with `restrict`, which the subject forbids")
        else:
            print_test_pass(total, "libft.h declares no prototype with `restrict`")
            passed += 1

        print_exercise_result("libft.h", passed, total)
        return passed == total

    finally:
        shutil.rmtree(build_dir, ignore_errors=True)
