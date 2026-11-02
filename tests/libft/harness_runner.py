import atexit
import os
import re
import shutil
import subprocess
import tempfile

from rich.console import Console

from utils.compiler import compile_source
from utils.functions import get_defined_functions
from utils.reporting import record_problem
from utils.runner import run_test_case
from utils.ui import (
    print_command_execution,
    print_exercise_result,
    print_test_fail,
    print_test_pass,
)
from .result_messages import success_message, failure_values

LIBFT_DIR = os.path.dirname(os.path.abspath(__file__))
FREE_TRACKER = os.path.join(os.path.dirname(LIBFT_DIR), "free_tracker.c")
REFS_DIR = os.path.join(LIBFT_DIR, "refs")

console = Console()

_REF_ARCHIVE = []


def harness_path(function_name):
    return os.path.join(LIBFT_DIR, function_name, f"{function_name}_harness.c")


def uses_restrict(path):
    """True when the C file uses the `restrict` keyword outside comments.

    "Some of the function prototypes you need to reimplement use the
    'restrict' qualifier [...] it is forbidden to include it in your own
    prototypes." It compiles either way, so nothing else would notice.
    Comments are stripped first: a remark mentioning the word is not a use.
    """
    try:
        with open(path, errors="replace") as handle:
            text = handle.read()
    except OSError:
        return False
    text = re.sub(r"/\*.*?\*/", " ", text, flags=re.S)
    text = re.sub(r"//[^\n]*", " ", text)
    return re.search(r"\brestrict\b", text) is not None


def compiles_alone(path):
    """True when the file compiles on its own, the way get_defined_functions
    compiles it - so an empty set from there can be told apart as "defines
    nothing" or "could not be compiled to look"."""
    try:
        result = subprocess.run(
            ["cc", "-x", "c", "-c", path, "-o", os.devnull],
            capture_output=True,
            text=True,
            timeout=30,
        )
    except (OSError, subprocess.SubprocessError):
        return False
    return result.returncode == 0


def check_student_definition(student_file, symbol):
    """Reject a missing implementation before references can supply its symbol.

    Compilation errors proceed to the real harness build for its diagnostic.
    A prototype-only or empty source compiles, but cannot be tested.
    """
    if symbol in get_defined_functions(student_file) or not compiles_alone(student_file):
        return True
    print_command_execution(
        f"nm {os.path.basename(student_file)} (checking it defines {symbol})"
    )
    message = (f"{os.path.basename(student_file)} does not define "
               f"{symbol}() — nothing to test.")
    record_problem('implementation', message)
    console.print(message, style='deep_pink2', markup=False, highlight=False)
    print()
    return False


def reference_archive():
    """Build (once) an archive of reference libft implementations to link last.

    libft's functions legitimately call each other - the subject says so
    outright ("Some of the functions from Part 1 may be useful for
    implementing the functions below") - so a harness that compiles only the
    one file under test fails to link as soon as, say, ft_strrchr calls
    ft_strlen.

    Linking a static ARCHIVE rather than the object files solves this without
    any per-function configuration, and without letting the grader's code mask
    the student's: the linker pulls a member out of an archive only to resolve
    a symbol that is still undefined. The student's own definition always
    wins, and a reference is used only for a helper their file calls but does
    not define. When ft_strlen itself is under test it is the student's
    ft_strlen.c that provides the symbol, so its reference member is never
    pulled in.

    This is the *_ref.c pattern tests/C12 and tests/C13 already use ("so a
    later exercise can be graded without depending on the student's earlier
    one"), scaled to a module where nearly every function is a potential
    dependency of every other.
    """
    if _REF_ARCHIVE:
        return _REF_ARCHIVE[0]

    build_dir = tempfile.mkdtemp(prefix="claudenette_libft_refs_")
    objects = []
    for name in sorted(os.listdir(REFS_DIR)):
        if not name.endswith(".c"):
            continue
        obj = os.path.join(build_dir, name[:-2] + ".o")
        result = subprocess.run(
            ["cc", "-c", os.path.join(REFS_DIR, name), "-o", obj],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            objects.append(obj)

    archive = os.path.join(build_dir, "libftref.a")
    if objects:
        subprocess.run(
            ["ar", "rcs", archive] + objects, capture_output=True, text=True
        )
    atexit.register(shutil.rmtree, build_dir, True)
    _REF_ARCHIVE.append(archive if os.path.exists(archive) else None)
    return _REF_ARCHIVE[0]


def run_harness_cases(
    student_file,
    display_name,
    function_name,
    cases,
    with_free_tracker=False,
    extra_sources=None,
    flags=None,
    include_student_file=True,
    symbol_name=None,
    harness_source=None,
):
    """Compile <fn>_harness.c with the student's file and run one case per entry.

    Each case is (args, stdin, expected_stdout, description), optionally
    followed by expected stderr and a per-case timeout; the harness selects behaviour from argv
    and writes its result to stdout, which is compared byte for byte - and
    so is stderr, when a case gives one.

    Unlike the Piscine modules, the binary is built into a temp directory
    rather than the module root. Those modules build into the module root
    because the extra-files check inspects the exercise subdirectory, so a
    build artefact there is invisible to it. libft has no subdirectories -
    every file key sits at the repository root, which IS the checked
    directory - so a binary built there would be reported as an extra file by
    the next key's check, and a run_func that raised before its cleanup would
    poison every exercise after it.
    """
    if harness_source is None and include_student_file:
        from .combined_cases import merge_cases
        cases = merge_cases(function_name, cases)
    build_dir = tempfile.mkdtemp(prefix="claudenette_libft_")
    exe_path = os.path.join(build_dir, f"{function_name}_test")

    try:
        # The reference archive fills in helpers the student calls but doesn't
        # define - which is the point of it, and also its danger: an EMPTY or
        # missing implementation defines no symbol either, so the linker
        # happily supplies the grader's own reference and the harness tests
        # that instead. A 0-byte ft_bzero.c scored 3/3 this way.
        #
        # Verifying the definition is what separates the two cases. A broken
        # implementation still defines its symbol, so it is graded (and fails)
        # on its own merit; an absent one is reported as absent.
        #
        # A file that does not compile defines nothing either, and was told
        # "does not define ft_x()" with cc's error shown nowhere - the
        # functions check leaves compile errors to the harness compile, which
        # this return skipped. Such a file goes on to that compile instead,
        # which prints the error and fails it.
        if include_student_file:
            symbol = symbol_name or function_name
            if not check_student_definition(student_file, symbol):
                print_exercise_result(display_name, 0, 0)
                return False

            if uses_restrict(student_file):
                console.print(
                    f"[deep_pink2]{os.path.basename(student_file)} uses `restrict`, "
                    "which the subject forbids in your own prototypes.[/deep_pink2]",
                    highlight=False,
                )
                print()
                print_exercise_result(display_name, 0, len(cases))
                return False

        # include_student_file=False is for the libft.h key, whose "student
        # file" is a header: passing it to cc as a source would compile the
        # header itself rather than test that it declares the library.
        # Student file FIRST: compile_source names source_files[0] in the
        # command it prints, and every Piscine module shows the student's file
        # there, not the harness. Link order between these two is irrelevant -
        # only the reference archive has to come last.
        sources = []
        if include_student_file:
            sources.append(student_file)
        sources.append(harness_source or harness_path(function_name))
        sources += list(extra_sources or [])
        if with_free_tracker:
            sources.append(FREE_TRACKER)
        # Last, so it only ever fills in symbols still undefined - see
        # reference_archive().
        archive = reference_archive()
        if archive:
            sources.append(archive)

        if flags is None:
            # -I at the student's own directory so a harness can include their
            # libft.h. The list harnesses need it for t_list, which the
            # subject says to declare there ("add the following structure
            # declaration to your libft.h file"), and the libft.h key needs it
            # for everything. Harmless for the harnesses that declare their
            # own prototype and include nothing.
            # "." rather than the absolute directory: main.py always runs
            # from the student's submission directory, so they are the same
            # path, and the Piscine modules never print a long absolute one
            # for a location the reader is already standing in.
            flags = ["-Wall", "-Wextra", "-Werror", "-I", "."]

        if not compile_source(sources, exe_path, flags=flags):
            print_exercise_result(display_name, 0, len(cases))
            return False

        print_command_execution(f"{function_name}_test")

        passed_count = 0
        for i, case in enumerate(cases, 1):
            args, stdin, expected, description = case[:4]
            expected_err = case[4] if len(case) > 4 else None
            actual, err, _code = run_test_case(
                exe_path, input_data=stdin, args=list(args), timeout=case[5] if len(case)>5 else 2
            )
            if actual != expected:
                message, wanted, received = failure_values(
                    function_name, args, description, expected, actual,
                    campaign=harness_source is not None,
                )
                print_test_fail(
                    i,
                    message,
                    expected=wanted,
                    actual=received,
                )
            elif expected_err is not None and err != expected_err:
                print_test_fail(
                    i,
                    f"{description}: not as expected on stderr",
                    expected=expected_err,
                    actual=err,
                )
            else:
                print_test_pass(i, success_message(
                    function_name, args, description, actual,
                    stderr=err if expected_err is not None else None,
                    campaign=harness_source is not None,
                ))
                passed_count += 1

        print_exercise_result(display_name, passed_count, len(cases))
        extension_ok = True
        if harness_source is None and include_student_file:
            from .edge_cases import cases_for, KINDS, HARNESS
            edge_cases = cases_for(function_name)
            if edge_cases:
                edge_source = os.path.join(build_dir, "boundaries.c")
                with open(edge_source, "w") as source:
                    source.write(f'#define FT {function_name}\n#define KIND {KINDS[function_name]}\n'
                                 + f'#include "{HARNESS}"\n')
                extension_ok = run_harness_cases(
                    student_file, function_name + " boundaries", function_name, edge_cases,
                    with_free_tracker=True, harness_source=edge_source)
        return passed_count == len(cases) and extension_ok

    finally:
        shutil.rmtree(build_dir, ignore_errors=True)


def run_allocation_cases(student_file, function_name):
    """Fail each allocation made by a constructor, then inspect ownership."""
    return run_harness_cases(
        student_file, function_name + " allocation failures", function_name,
        [([], None, "OK", "each malloc failure returns NULL and frees all partial results")],
        with_free_tracker=True,
        flags=["-Wall", "-Wextra", "-Werror", "-I", ".",
               "-DTEST_" + function_name.upper()],
        harness_source=os.path.join(LIBFT_DIR, "allocation_harness.c"),
    )
