import fnmatch
import importlib
import os
import re
import shutil
import subprocess
import sys
import time
import traceback

REPO = os.path.dirname(os.path.abspath(__file__))
LOCAL_DEPS = os.path.join(REPO, ".deps")
if os.path.isdir(LOCAL_DEPS):
    sys.path.insert(0, LOCAL_DEPS)
    # Let subprocesses importing norminette use the same local installation.
    os.environ["PYTHONPATH"] = LOCAL_DEPS + os.pathsep + os.environ.get("PYTHONPATH", "")
    os.environ["PATH"] = os.path.join(LOCAL_DEPS, "bin") + os.pathsep + os.environ.get("PATH", "")


# The verdict as an exit status, grep- and diff-style, so a script or a git
# hook can act on it without reading the output: 0 PASSED, 1 FAILED, and 2
# for no verdict - Status UNKNOWN, or a run that could not grade at all (not
# a module directory, an unknown option, no exercise matched, a missing
# tool). Every exit used to be 0 after grading and 1 before it, so FAILED
# and "could not run" looked the same and neither differed from PASSED.
EXIT_CODES = {"PASSED": 0, "FAILED": 1}
EXIT_NO_VERDICT = 2


def _tilde(path):
    home = os.path.expanduser("~")
    if path == home or path.startswith(home + os.sep):
        return "~" + path[len(home):]
    return path


def install_lines():
    """The README's install and run commands, with this checkout's real paths.

    main.py runs from the student's directory, so a bare `requirements.txt`
    names a file that isn't there. The local installer works without sudo,
    system pip or venv support, including on managed campus machines.
    """
    return [
        f"python3 {_tilde(os.path.join(REPO, 'install.py'))}",
        "Dependencies are installed in this checkout; no sudo is required.",
        f"python3 {_tilde(os.path.join(REPO, 'main.py'))}",
    ]


try:
    from rich.console import Console
except ImportError:
    # rich is the one hard Python dependency, and this import is the very
    # first thing that can fail on a fresh clone - or when main.py is run by
    # a Python without the installed dependencies. A bare traceback doesn't
    # tell a student what to do about it.
    setup, install, run = install_lines()
    sys.stderr.write(
        "Claudenette needs the 'rich' package, which this Python doesn't have.\n\n"
        f"    {setup}\n    {install}\n\n"
        f"then run claudenette:\n\n    {run}\n"
    )
    sys.exit(EXIT_NO_VERDICT)

from utils.reporting import (
    exercise_report, function_report, start_compact_report, finish_compact_report,
    record_problem,
)
from utils.runner import RUNTIME_ISSUES, TestUnavailable
from tests.libft.harness_runner import check_student_definition
from tests.null_contracts import run_null_contracts
from tests.memory_contracts import run_memory_contracts
from tests.piscine_boundaries import run_boundary_contracts
from utils.extra_files import check_no_extra_files
from utils.functions import check_allowed_functions
from utils.norminette import check_norminette
from utils.ui import BANNER_WIDTH, print_final_summary, print_header

console = Console(width=BANNER_WIDTH)


def norminette_available():
    # Mirrors utils/norminette.py's own resolution order: prefer the
    # binary, fall back to the importable module (norminette ships on
    # PyPI, so `pip install norminette` leaves it reachable that way even
    # when the console script isn't on PATH - e.g. a --user install whose
    # bin dir isn't exported).
    if shutil.which("norminette") is not None:
        return True
    try:
        return (
            subprocess.run(
                [sys.executable, "-m", "norminette", "--version"],
                capture_output=True,
                timeout=10,
            ).returncode
            == 0
        )
    except Exception:
        return False


# The Debian/Ubuntu package providing each tool a test grades against. All of
# them ship with macOS, so there a missing one means PATH has lost /usr/bin;
# on Linux one goes missing on a minimal install - plain ubuntu:22.04 has no
# hexdump, which is why tools/docker/Dockerfile adds bsdextrautils.
ORACLE_PACKAGES = {
    "hexdump": "bsdextrautils",
    "tail": "coreutils",
}


def oracle_hint(tool):
    if sys.platform == "darwin":
        return f"{tool} ships with macOS, in /usr/bin - check that it is on your PATH"
    package = ORACLE_PACKAGES.get(tool)
    if package is None:
        return f"install the package providing {tool}"
    return f"{tool} should be provided by the campus ({package}); ask campus staff if missing"


def preflight(test_map, skip_norm, skip_fn):
    # Without this, a missing external tool is not an error: check_norminette
    # and check_allowed_functions each print a yellow "skipping" line and
    # return True. On a machine with no norminette that means every exercise
    # reports OK and the run ends in "Status: PASSED" - from a tool whose
    # entire purpose is predicting whether the real moulinette will pass you.
    # The warning scrolls past mid-output and never reaches the summary, so
    # refuse to start instead.
    #
    # Only what this module actually needs is required: shell00/shell01 set
    # skip_precheck on every exercise and their deliverables aren't C, so
    # they need no toolchain at all.
    #
    # Some tests grade against a real system tool rather than a hardcoded
    # expectation - C10 ex03 diffs the student's hexdump against the system
    # one. Without that tool the exercise cannot be graded at ALL, which is
    # not the same thing as the student being wrong: reporting KO there blames
    # them for claudenette's own incomplete environment. Exercises declare
    # what they need via the mapping's `requires_tools` option and it is
    # checked here, so the run refuses with instructions instead.
    missing_oracles = {}
    for key, entry in test_map.items():
        options = entry[3] if len(entry) == 4 else {}
        for tool in options.get("requires_tools", []):
            if shutil.which(tool) is None:
                missing_oracles.setdefault(tool, []).append(key)

    needs_c_toolchain = any(
        not (entry[3] if len(entry) == 4 else {}).get("skip_precheck", False)
        for entry in test_map.values()
    )
    if not needs_c_toolchain and not missing_oracles:
        return

    missing_pip = []
    missing_system = []

    if needs_c_toolchain and not skip_norm and not norminette_available():
        missing_pip.append("norminette")
    # cc is needed to build every C harness, not just the allowed-functions
    # check, so --skip-fn doesn't excuse it; nm is used only by that check.
    if needs_c_toolchain and shutil.which("cc") is None:
        missing_system.append("cc")
    if needs_c_toolchain and not skip_fn and shutil.which("nm") is None:
        missing_system.append("nm")

    if not missing_pip and not missing_system and not missing_oracles:
        return

    console.print()
    console.print(
        "[deep_pink2]Claudenette can't grade without these tools:[/deep_pink2]"
    )
    print()

    if missing_pip:
        setup, install, run = install_lines()
        console.print(f"  [deep_pink2]missing:[/deep_pink2] {', '.join(missing_pip)}")
        console.print(f"  [white]fix:[/white]     {setup}", highlight=False)
        console.print(f"           {install}", highlight=False)
        console.print(f"  [white]then:[/white]    {run}", highlight=False)
        print()

    if missing_system:
        console.print(
            f"  [deep_pink2]missing:[/deep_pink2] {', '.join(missing_system)}"
        )
        if sys.platform == "darwin":
            console.print("  [white]fix:[/white]     xcode-select --install")
        else:
            console.print("  [white]fix:[/white]     install your distro's C toolchain")
            console.print(
                "           [bright_black]On 42 Ubuntu 22.04.5 these are campus tools; "
                "ask campus staff if missing. No sudo is required by Claudenette.[/bright_black]"
            )
        print()

    if missing_oracles:
        for tool, keys in sorted(missing_oracles.items()):
            console.print(f"  [deep_pink2]missing:[/deep_pink2] {tool}")
            console.print(
                f"  [white]needed by:[/white] {', '.join(sorted(keys))} "
                f"(graded against the real {tool})"
            )
            console.print(f"  [white]fix:[/white]       {oracle_hint(tool)}")
            print()

    if missing_pip or missing_system:
        console.print(
            "[bright_black]Grading without these would report PASSED for checks that "
            "never ran.[/bright_black]"
        )
        console.print(
            "[bright_black]To grade anyway, knowing the result is incomplete: "
            "--skip-norm / --skip-fn[/bright_black]"
        )
    else:
        # --skip-norm/--skip-fn only bypass the norm and forbidden-function
        # checks; neither can substitute for a missing oracle, so offering
        # them here would just send the student down a dead end.
        console.print(
            "[bright_black]There is no flag for this one - the exercise is graded "
            "against that tool's own output.[/bright_black]"
        )
        # This Python evidently has what claudenette needs, so the example
        # repeats it in the command shown to the user.
        this_run = f"{_tilde(sys.executable)} {_tilde(os.path.join(REPO, 'main.py'))}"
        console.print(
            "[bright_black]Grade the rest meanwhile by naming exercises, e.g. "
            f"`{this_run} ex00 ex01`.[/bright_black]",
            highlight=False,
        )
    print()
    sys.exit(EXIT_NO_VERDICT)


def turned_in_headers(key, test_map):
    """Headers beside a file key that are not mapping keys themselves.

    ft_list.h (every C12 exercise), ft_btree.h (C13) and the headers of the
    Makefile-built exercises are turned in and must follow the norm, but only
    keys were ever norminetted - a header breaking the norm scored OK, where
    the moulinette checks every file. A directory key needs none of this:
    norminette already recurses into it.
    """
    here = os.path.dirname(key) or "."
    keys = {os.path.normpath(k) for k in test_map}
    return [
        os.path.join(here, name)
        for name in sorted(os.listdir(here))
        if name.endswith(".h") and os.path.normpath(os.path.join(here, name)) not in keys
    ]


def get_current_exercise_mapping():
    current_dir = os.path.basename(os.getcwd())

    # libft is the first common-core module rather than a Piscine one. It is
    # graded at a git repository root holding flat ft_*.c files, not a
    # directory of exNN/ subdirectories - see tests/libft/__init__.py.
    project_names = {
        "rush00",
        "rush01",
        "rush02",
        "bsq",
        "shell00",
        "shell01",
        "libft",
        "ft_printf",
    }

    if re.match(r"^C(0[0-9]|1[0-3])$", current_dir):
        package_name = current_dir
    elif current_dir.lower() in project_names:
        # Project directories (unlike C00-C13) aren't consistently cased
        # across campuses/students (e.g. "Rush00") - the package on disk is
        # lowercase, so normalize for the import while still reporting the
        # user's actual directory name everywhere else.
        package_name = current_dir.lower()
    else:
        return None, current_dir, None

    try:
        module = importlib.import_module(f"tests.{package_name}")
        mapping = module.get_mapping()
        return mapping, current_dir, module

    except ImportError:
        error_msg = f"Error: Could not load configuration for '{current_dir}'."
        # Resolved from this file rather than hardcoded: the repo is named
        # lowercase 'claudenette', which a capital-C literal got away with
        # only on macOS's case-insensitive filesystem - and 42's clusters
        # run Linux. This also stays correct if the clone lives elsewhere.
        repo_root = os.path.dirname(os.path.abspath(__file__))
        missing_path = os.path.join(repo_root, "tests", package_name, "__init__.py")
        fix_msg = f"Make sure '{missing_path}' exists."
        console.print(f"[deep_pink2]{error_msg:^{BANNER_WIDTH}s}[/deep_pink2]")
        console.print(f"[white]{fix_msg:^{BANNER_WIDTH}s}[/white]")
        sys.exit(EXIT_NO_VERDICT)

    except AttributeError:
        error_msg = f"Error: {current_dir} module is missing 'get_mapping()' function."
        console.print(f"[deep_pink2]{error_msg:^{BANNER_WIDTH}s}[/deep_pink2]")
        sys.exit(EXIT_NO_VERDICT)


if __name__ == "__main__":
    print_header()

    test_map, dir_name, test_module = get_current_exercise_mapping()

    if test_map is None:
        error_msg = (
            f"Current directory '{dir_name}' does not match expected pattern "
            "(C00~13, rush00, rush01, rush02, bsq, shell00, shell01, libft, ft_printf)."
        )
        fix_msg = "Please navigate to an appropriate directory to run tests."
        console.print(f"[deep_pink2]{error_msg:^{BANNER_WIDTH}s}[/deep_pink2]")
        console.print(f"[white]{fix_msg:^{BANNER_WIDTH}s}[/white]")
        sys.exit(EXIT_NO_VERDICT)

    if re.match(r"^C(0[0-9]|1[0-3])$", dir_name):
        display_name = f"{dir_name[0]} {dir_name[1:]}"
    else:
        display_name = dir_name
    # Flags are pulled out by name rather than via argparse so the existing
    # "everything else is a substring filter" behaviour stays exactly as it
    # was (filters are matched against mapping keys, which never start with
    # a dash).
    argv = sys.argv[1:]
    skip_norm = "--skip-norm" in argv
    skip_fn = "--skip-fn" in argv
    compact = "--compact" in argv

    unknown_flags = [
        a for a in argv if a.startswith("-") and a not in ("--skip-norm", "--skip-fn", "--compact")
    ]
    if unknown_flags:
        error_msg = f"Unknown option: {' '.join(unknown_flags)}"
        console.print(f"[deep_pink2]{error_msg:^{BANNER_WIDTH}s}[/deep_pink2]")
        fix_msg = "Valid options: --skip-norm, --skip-fn, --compact"
        console.print(f"[white]{fix_msg:^{BANNER_WIDTH}s}[/white]")
        sys.exit(EXIT_NO_VERDICT)

    targets = [a for a in argv if not a.startswith("-")]
    # Most modules use exercise-name order; libft follows the subject order.
    sorted_paths = (
        list(test_map) if getattr(test_module, "PRESERVE_ORDER", False) else sorted(test_map)
    )

    if targets:
        filtered_paths = []

        for path in sorted_paths:
            if any(t in path or t in test_map[path][0] for t in targets):
                filtered_paths.append(path)

        if not filtered_paths:
            error_msg = f"No exercises matched '{' '.join(targets)}'."
            console.print(f"[deep_pink2]{error_msg:^{BANNER_WIDTH}s}[/deep_pink2]")
            sys.exit(EXIT_NO_VERDICT)

        sorted_paths = filtered_paths

    # Preflight the filtered set, not the whole module: asking for `ex00` must
    # not fail because some other exercise needs a tool this run never reaches.
    preflight({k: test_map[k] for k in sorted_paths}, skip_norm, skip_fn)

    console.print(
        f"[sea_green2]{'Generating test for ' + display_name + '...':^{BANNER_WIDTH}s}[/sea_green2]",
        highlight=False,
    )
    print()

    start_time = time.time()
    results = []
    # Display names of any separately evaluated entries, kept out of the
    # mandatory score streak. Libft 19.3 has no such entries.
    bonus_names = set()
    # What rush00 was told - see rush00_printed_own_summary below.
    rush00_precheck_ok = False
    last_was_grouped = False
    if compact:
        start_compact_report([test_map[path][0] for path in sorted_paths])

    for student_file_path in sorted_paths:
        with exercise_report(lambda: results[-1], compact=compact,
                             concise=dir_name.lower() in ('libft', 'ft_printf')):
            mapping_entry = test_map[student_file_path]
            if len(mapping_entry) == 4:
                ex_name, run_func, allowed_fns, options = mapping_entry
            else:
                ex_name, run_func, allowed_fns = mapping_entry
                options = {}
            extra_norm_rules = options.get("norm_rules")
            extra_compile_flags = options.get("compile_flags")
            skip_precheck = options.get("skip_precheck", False)
            extra_allowed_files = options.get("allowed_files")
            strict_symbols = options.get("strict_symbols")
            if options.get("bonus", False):
                bonus_names.add(ex_name)
            if options.get("requires_mandatory") and any(
                status != "OK" for name, status in results if name not in bonus_names
            ):
                console.print("[bright_black]Bonus requires a complete mandatory pass.[/bright_black]")
                results.append((ex_name, "KO"))
                continue

            # TODO is checked BEFORE the file-exists test on purpose. An exercise
            # claudenette has no test for can't be graded whether the student
            # turned it in or not, and checking existence first would report the
            # grader's own gap as "Missing file: ..." - blaming the student for
            # something they may well have done. TODO is the honest status, and
            # it's the only way that branch is reachable at all for an exercise
            # whose deliverable isn't present.
            if run_func is None:
                if not last_was_grouped:
                    console.print("-" * BANNER_WIDTH, style="bright_black")
                    print()

                console.print(
                    f"[yellow]Test for {student_file_path} not implemented yet.[/yellow]"
                )
                results.append((ex_name, "TODO"))
                print()
                last_was_grouped = True
                continue

            required_paths = list(dict.fromkeys([student_file_path] + options.get("source_files", [])))
            missing_paths = [path for path in required_paths if not os.path.exists(path)]
            if missing_paths:
                if not last_was_grouped:
                    console.print("-" * BANNER_WIDTH, style="bright_black")
                    print()

                console.print(f"[deep_pink2]Missing file: {', '.join(missing_paths)}[/deep_pink2]")
                results.append((ex_name, "ABSENT"))
                print()
                last_was_grouped = True
                continue

            last_was_grouped = False
            console.print("-" * BANNER_WIDTH, style="bright_black")
            print()

            # "You must not leave any additional files..." applies regardless
            # of whether this exercise is C at all, so this check is entirely
            # independent of skip_precheck. Directory-keyed mappings (rush01's
            # "ex00", bsq's ".") have no single "the primary file" to default
            # to, so they rely entirely on an explicit allowed_files pattern
            # list; a file-keyed mapping always at least allows itself.
            if os.path.isdir(student_file_path):
                check_dir = student_file_path
                allowed_set = extra_allowed_files
            else:
                check_dir = os.path.dirname(student_file_path) or "."
                explicit = list(extra_allowed_files or [])
                own_name = os.path.basename(student_file_path)
                # A file key implicitly allows itself, which is what makes the
                # check work for a Piscine exercise that declares no list at all.
                # Skip the prefix when the explicit list already matches the file:
                # libft's shared list covers every key through "ft_*.c", so
                # prepending added nothing except a different first entry per key -
                # which printed "allowed: Makefile, Makefile, ..." and, worse, made
                # 45 identical checks look distinct so none could be cached.
                if any(fnmatch.fnmatch(own_name, pattern) for pattern in explicit):
                    allowed_set = explicit
                else:
                    allowed_set = [own_name] + explicit

            files_passed = check_no_extra_files(
                check_dir, allowed_set, turn_in_files=options.get('turn_in_files'),
                recursive=options.get('recursive_extra_files', False),
            ) if allowed_set else True

            if skip_precheck:
                # Norminette and "allowed functions" are C-specific concepts
                # (style rules, nm -u on a compiled object) - for an exercise
                # whose deliverable isn't C at all (a shell one-liner, a
                # filesystem artifact), running them isn't just unnecessary,
                # it's a category error, even though they happen to no-op
                # harmlessly rather than misfire. Real moulinette doesn't apply
                # either check to these exercises, so this tester shouldn't
                # either - skip both entirely instead of relying on the no-op.
                norm_passed = True
                fns_passed = True
                checks_bypassed = False
            else:
                # skip_precheck means "this check doesn't apply here"; --skip-norm
                # / --skip-fn mean "it applies but the student chose not to run
                # it". Only the second is dishonest to report as a plain OK, so
                # only the second sets checks_bypassed - see the ladder below.
                #
                # A key that is neither C source nor a directory of it - the
                # Makefile of C10, C11 ex05 and rush02, C09's libft_creator.sh -
                # has no norm and no symbols of its own; each of those tests runs
                # norminette and nm on the sources itself. Handing the Makefile to
                # norminette only ever worked by accident: every version prints
                # "'Makefile' is not valid C or C header file", 3.3.59 exited 0 on
                # it, and 3.3.60 exits 1 - which made every one of those exercises
                # NORM ERR on a fresh install. skip_precheck would be the wrong
                # fix: it also tells preflight() the module needs no toolchain,
                # and these tests do need norminette, cc and nm for their sources.
                key_is_source = bool(options.get("source_files")) or os.path.isdir(student_file_path) or student_file_path.endswith(
                    (".c", ".h")
                )
                if skip_norm or not key_is_source or options.get("runner_checks_norm"):
                    norm_passed = True
                else:
                    norm_passed = True
                    for source in options.get("source_files", [student_file_path]):
                        norm_passed = check_norminette(source, extra_rules=extra_norm_rules) and norm_passed
                if not skip_norm and not os.path.isdir(student_file_path) and not options.get("source_files"):
                    for header in turned_in_headers(student_file_path, test_map):
                        norm_passed = (
                            check_norminette(header, extra_rules=extra_norm_rules)
                            and norm_passed
                        )

                if skip_fn or not key_is_source or options.get("runner_checks_symbols"):
                    fns_passed = True
                else:
                    fns_passed = True
                    for source in options.get("source_files", [student_file_path]):
                        fns_passed = check_allowed_functions(
                            source, allowed_fns, extra_flags=extra_compile_flags,
                            strict_symbols=strict_symbols,
                        ) and fns_passed

                checks_bypassed = skip_norm or skip_fn
            runner_norm_results = {}

            def check_runner_norm(source):
                runner_norm_results[os.path.abspath(source)] = check_norminette(
                    source, extra_rules=extra_norm_rules,
                )

            # run_func is student-controlled code and test code alike - either
            # side can raise (a harness that isn't defensive about malformed
            # program output, e.g. tests/C12/ex15, or a genuine bug in the test
            # itself). Uncaught, that exception used to kill the whole process,
            # silently leaving every later exercise ungraded with no indication
            # why. Catch it, report it plainly, and let the existing priority
            # ladder below fold it in like any other failure.
            crashed = False
            unavailable = False
            with function_report(os.path.splitext(os.path.basename(student_file_path))[0],
                                 enabled=student_file_path.endswith(".c") and dir_name.lower() != "rush00") as group:
                try:
                    implementation_available = (
                        dir_name.lower() != "libft"
                        or not student_file_path.endswith(".c")
                        or check_student_definition(
                            student_file_path, os.path.splitext(os.path.basename(student_file_path))[0]
                        )
                    )
                    tests_passed = False
                    if implementation_available:
                        if dir_name.lower() == "rush00":
                            # rush00 prints its own summary block instead of using the
                            # generic one, so it's the only run_func that has to be told
                            # the precheck verdict - otherwise a norm/forbidden failure
                            # here is computed and then discarded. See run_C_rush00.
                            #
                            # Everything that can stop the status being OK/KO belongs in
                            # it. Leaving out the extra-files verdict and the --skip-*
                            # bypass printed rush00's own "Status: PASSED" followed by
                            # the generic "FAILED" or "UNKNOWN" - two contradicting
                            # verdicts, the first of which was the one a reader saw.
                            rush00_precheck_ok = (
                                files_passed and norm_passed and fns_passed and not checks_bypassed
                            )
                            tests_passed = run_func(student_file_path, precheck_ok=rush00_precheck_ok)
                        elif options.get("runner_checks_norm"):
                            tests_passed = run_func(
                                student_file_path, check_symbols=not skip_fn,
                                norm_check=None if skip_norm else check_runner_norm,
                            )
                        elif options.get("runner_checks_symbols"):
                            tests_passed = run_func(student_file_path, check_symbols=not skip_fn)
                        else:
                            tests_passed = run_func(student_file_path)
                        boundary_passed = run_boundary_contracts(test_module.__name__.split(".")[-1], student_file_path)
                        tests_passed = tests_passed and boundary_passed
                        null_passed = run_null_contracts(test_module.__name__.split(".")[-1], student_file_path, options)
                        memory_passed = run_memory_contracts(test_module.__name__.split(".")[-1], student_file_path, options)
                        tests_passed = tests_passed and null_passed and memory_passed and not RUNTIME_ISSUES
                    if group is not None:
                        group.success = tests_passed
                except TestUnavailable as exc:
                    unavailable = True
                    if group is not None:
                        group.unavailable = True
                    record_problem('environment', str(exc))
                    console.print(f'Test unavailable: {exc}', style='yellow', markup=False)
                except Exception as exc:
                    if group is not None:
                        group.success = False
                    crashed = True
                    tests_passed = False
                    console.print(
                        f"[deep_pink2]Error: the test itself crashed "
                        f"({type(exc).__name__}: {exc})[/deep_pink2]",
                        highlight=False,
                    )
                    console.print(
                        "[deep_pink2]This is a bug in claudenette's test for this "
                        "exercise, not necessarily your submission.[/deep_pink2]"
                    )
                    print()
                    traceback.print_exc()

            # Complete source prechecks even if an unavailable/crashed runner
            # stopped before reaching its header or runtime presentation stage.
            if options.get("runner_checks_norm") and not skip_norm:
                for source in options.get("source_files", [student_file_path]):
                    if os.path.abspath(source) not in runner_norm_results:
                        check_runner_norm(source)
                norm_passed = all(runner_norm_results.values())

            if not files_passed:
                results.append((ex_name, "EXTRA FILES"))
            elif not norm_passed:
                results.append((ex_name, "NORM ERR"))
            elif not fns_passed:
                results.append((ex_name, "FORBIDDEN FN"))
            elif crashed:
                results.append((ex_name, "CRASH"))
            elif unavailable:
                results.append((ex_name, "UNKNOWN"))
            elif not tests_passed:
                results.append((ex_name, "KO"))
            elif checks_bypassed:
                # Everything that actually ran passed - but a check the student
                # asked to skip might not have. Reporting OK here would recreate
                # exactly the false-PASSED that preflight() exists to prevent,
                # so it gets its own status: not a failure, just not vouched for.
                results.append((ex_name, "SKIPPED"))
            else:
                results.append((ex_name, "OK"))

    if compact:
        finish_compact_report()

    # rush00 prints its own multi-variant Result/Final score/Status block
    # inline (see run_C_rush00) since its real grading - a per-team random
    # draw across 5 variants with a >100% bonus mechanic - doesn't fit the
    # generic one-name-per-mapping-key summary below.
    #
    # It prints that block exactly when it was handed a clean precheck and
    # ran to the end - so this asks what it was told rather than reading it
    # back from the status. The status alone was wrong once: with a check
    # bypassed and a variant failing, KO outranks SKIPPED, rush00 had been
    # told to stay quiet, and neither summary printed - no Result, no
    # Status. ABSENT and TODO never call run_func, and CRASH raised before
    # the block; EXTRA FILES / NORM ERR / FORBIDDEN FN / SKIPPED all mean it
    # was told to stay quiet, so the generic summary reports the real
    # verdict instead of a misleading "125% PASSED".
    rush00_printed_own_summary = (
        dir_name.lower() == "rush00"
        and rush00_precheck_ok
        and results
        and results[0][1] in ("OK", "KO")
    )

    # Right above the score, where it can't be missed - the whole point of
    # SKIPPED is that the student knows this run doesn't predict the real
    # moulinette.
    # Advisories: requirements a module can check but that don't decide the
    # grade - libft's README.md is judged by peers, not by the moulinette.
    # They print right above the score, in the same yellow as the warnings
    # below, and never touch it. A module opts in with get_advisories(),
    # which runs with the student's directory as cwd, like get_mapping().
    get_advisories = getattr(test_module, "get_advisories", None)
    advisories = get_advisories() if callable(get_advisories) else []
    if advisories:
        print()
        for line in advisories:
            console.print(f"[yellow]Note: {line}[/yellow]", highlight=False)

    if skip_norm or skip_fn:
        bypassed = []
        if skip_norm:
            bypassed.append("norminette (--skip-norm)")
        if skip_fn:
            bypassed.append("allowed functions (--skip-fn)")
        print()
        console.print(
            f"[yellow]Warning: did not check {', '.join(bypassed)}.[/yellow]"
        )
        console.print(
            "[yellow]Exercises marked SKIPPED passed the checks that ran, but this "
            "score does not[/yellow]"
        )
        console.print("[yellow]predict the real moulinette.[/yellow]")

    if rush00_printed_own_summary:
        # run_C_rush00 returns score > 0, the same test its Status uses.
        status = "PASSED" if results[0][1] == "OK" else "FAILED"
    else:
        status = print_final_summary(results, bonus_names=bonus_names, compact=compact)

    elapsed = time.time() - start_time
    console.print(
        f"\n[bright_black]Test completed. Total elapsed time: {elapsed:.2f}s.[/bright_black]",
        highlight=False,
    )
    trailer = "Claudenette is a test automation tool. Its score is not an official Moulinette grade."
    console.print(f"\n[orange3]{trailer:^{BANNER_WIDTH}s}[/orange3]", highlight=False)

    sys.exit(EXIT_CODES.get(status, EXIT_NO_VERDICT))
