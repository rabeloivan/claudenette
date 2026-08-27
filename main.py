import importlib
import os
import re
import shutil
import subprocess
import sys
import time
import traceback

try:
    from rich.console import Console
except ImportError:
    # rich is the one hard Python dependency, and this import is the very
    # first thing that can fail on a fresh clone. A bare ImportError
    # traceback doesn't tell a student what to do about it.
    sys.stderr.write(
        "Claudenette needs the 'rich' package, which isn't installed.\n\n"
        "    pip install -r requirements.txt\n\n"
        "(or: pip install rich)\n"
    )
    sys.exit(1)

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
        console.print(f"  [deep_pink2]missing:[/deep_pink2] {', '.join(missing_pip)}")
        console.print("  [white]fix:[/white]     pip install -r requirements.txt")
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
                "           [bright_black](Debian/Ubuntu: sudo apt install "
                "build-essential binutils)[/bright_black]"
            )
        print()

    if missing_oracles:
        for tool, keys in sorted(missing_oracles.items()):
            console.print(f"  [deep_pink2]missing:[/deep_pink2] {tool}")
            console.print(
                f"  [white]needed by:[/white] {', '.join(sorted(keys))} "
                f"(graded against the real {tool})"
            )
            if sys.platform == "darwin":
                console.print(f"  [white]fix:[/white]       brew install {tool}")
            else:
                console.print(
                    f"  [white]fix:[/white]       install the package providing "
                    f"{tool} (Debian/Ubuntu: bsdextrautils for hexdump)"
                )
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
        console.print(
            "[bright_black]Grade the rest meanwhile by naming exercises, e.g. "
            "`python3 main.py ex00 ex01`.[/bright_black]"
        )
    print()
    sys.exit(1)


def get_current_exercise_mapping():
    current_dir = os.path.basename(os.getcwd())

    project_names = {"rush00", "rush01", "rush02", "bsq", "shell00", "shell01"}

    if re.match(r"^C(0[0-9]|1[0-3])$", current_dir):
        package_name = current_dir
    elif current_dir.lower() in project_names:
        # Project directories (unlike C00-C13) aren't consistently cased
        # across campuses/students (e.g. "Rush00") - the package on disk is
        # lowercase, so normalize for the import while still reporting the
        # user's actual directory name everywhere else.
        package_name = current_dir.lower()
    else:
        return None, current_dir

    try:
        module = importlib.import_module(f"tests.{package_name}")
        mapping = module.get_mapping()
        return mapping, current_dir

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
        sys.exit(1)

    except AttributeError:
        error_msg = f"Error: {current_dir} module is missing 'get_mapping()' function."
        console.print(f"[deep_pink2]{error_msg:^{BANNER_WIDTH}s}[/deep_pink2]")
        sys.exit(1)


if __name__ == "__main__":
    print_header()

    test_map, dir_name = get_current_exercise_mapping()

    if test_map is None:
        error_msg = (
            f"Current directory '{dir_name}' does not match expected pattern "
            "(C00~13, rush00, rush01, bsq, shell00, shell01)."
        )
        fix_msg = "Please navigate to an appropriate directory to run tests."
        console.print(f"[deep_pink2]{error_msg:^{BANNER_WIDTH}s}[/deep_pink2]")
        console.print(f"[white]{fix_msg:^{BANNER_WIDTH}s}[/white]")
        sys.exit(1)

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

    unknown_flags = [
        a for a in argv if a.startswith("-") and a not in ("--skip-norm", "--skip-fn")
    ]
    if unknown_flags:
        error_msg = f"Unknown option: {' '.join(unknown_flags)}"
        console.print(f"[deep_pink2]{error_msg:^{BANNER_WIDTH}s}[/deep_pink2]")
        fix_msg = "Valid options: --skip-norm, --skip-fn"
        console.print(f"[white]{fix_msg:^{BANNER_WIDTH}s}[/white]")
        sys.exit(1)

    targets = [a for a in argv if not a.startswith("-")]
    sorted_paths = sorted(test_map.keys())

    if targets:
        filtered_paths = []

        for path in sorted_paths:
            if any(t in path for t in targets):
                filtered_paths.append(path)

        if not filtered_paths:
            error_msg = f"No exercises matched '{' '.join(targets)}'."
            console.print(f"[deep_pink2]{error_msg:^{BANNER_WIDTH}s}[/deep_pink2]")
            sys.exit(1)

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
    last_was_grouped = False

    for student_file_path in sorted_paths:
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

        if not os.path.exists(student_file_path):
            if not last_was_grouped:
                console.print("-" * BANNER_WIDTH, style="bright_black")
                print()

            console.print(f"[deep_pink2]Missing file: {student_file_path}[/deep_pink2]")
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
            allowed_set = [os.path.basename(student_file_path)] + list(extra_allowed_files or [])

        files_passed = check_no_extra_files(check_dir, allowed_set) if allowed_set else True

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
            if skip_norm:
                norm_passed = True
            else:
                norm_passed = check_norminette(
                    student_file_path, extra_rules=extra_norm_rules
                )

            if skip_fn:
                fns_passed = True
            else:
                fns_passed = check_allowed_functions(
                    student_file_path, allowed_fns, extra_flags=extra_compile_flags
                )

            checks_bypassed = skip_norm or skip_fn
        # run_func is student-controlled code and test code alike - either
        # side can raise (a harness that isn't defensive about malformed
        # program output, e.g. tests/C12/ex15, or a genuine bug in the test
        # itself). Uncaught, that exception used to kill the whole process,
        # silently leaving every later exercise ungraded with no indication
        # why. Catch it, report it plainly, and let the existing priority
        # ladder below fold it in like any other failure.
        crashed = False
        try:
            if dir_name.lower() == "rush00":
                # rush00 prints its own summary block instead of using the
                # generic one, so it's the only run_func that has to be told
                # the precheck verdict - otherwise a norm/forbidden failure
                # here is computed and then discarded. See run_C_rush00.
                tests_passed = run_func(
                    student_file_path, precheck_ok=(norm_passed and fns_passed)
                )
            else:
                tests_passed = run_func(student_file_path)
        except Exception as exc:
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

        if not files_passed:
            results.append((ex_name, "EXTRA FILES"))
        elif not norm_passed:
            results.append((ex_name, "NORM ERR"))
        elif not fns_passed:
            results.append((ex_name, "FORBIDDEN FN"))
        elif crashed:
            results.append((ex_name, "CRASH"))
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

    # rush00 prints its own multi-variant Result/Final score/Status block
    # inline (see run_C_rush00) since its real grading - a per-team random
    # draw across 5 variants with a >100% bonus mechanic - doesn't fit the
    # generic one-name-per-mapping-key summary below.
    #
    # It only does so when it actually reached that point with a clean
    # precheck, which is exactly the "OK"/"KO" statuses: ABSENT and TODO
    # exit before run_func is ever called, CRASH means it raised partway
    # through, and EXTRA FILES / NORM ERR / FORBIDDEN FN mean run_C_rush00
    # deliberately suppressed its own block so this generic summary can
    # report the real failure instead of a misleading "125% PASSED".
    rush00_printed_own_summary = (
        dir_name.lower() == "rush00" and results and results[0][1] in ("OK", "KO")
    )

    # Right above the score, where it can't be missed - the whole point of
    # SKIPPED is that the student knows this run doesn't predict the real
    # moulinette.
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

    if not rush00_printed_own_summary:
        print_final_summary(results)

    elapsed = time.time() - start_time
    console.print(
        f"\n[bright_black]Test completed. Total elapsed time: {elapsed:.2f}s.[/bright_black]",
        highlight=False,
    )
    trailer = "Claudenette is a test automation tool and may make mistakes. Rely on your own tests."
    console.print(f"\n[orange3]{trailer:^{BANNER_WIDTH}s}[/orange3]", highlight=False)
