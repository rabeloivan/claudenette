import glob
import os
import subprocess


def run_make(student_dir, *targets, timeout=30):
    """`make <targets>` in the student's directory, never raising.

    A Makefile that hangs is the student's failure, not claudenette's: a
    TimeoutExpired escaping from a test is reported as CRASH, which blames the
    grader, so it comes back here as exit -1 with "TIMEOUT" on stderr.
    """
    try:
        return subprocess.run(
            ["make", *targets],
            cwd=student_dir,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        return subprocess.CompletedProcess(["make", *targets], -1, stdout="", stderr="TIMEOUT")


def _objects(student_dir):
    return sorted(glob.glob(os.path.join(student_dir, "**", "*.o"), recursive=True))


def check_makefile_rules(student_dir, binary_name, build_rule="all", clean=True, fclean=True):
    """Run the rules a subject names and check each one does its job.

    C10 ("a Makefile with the following rules: all, clean, fclean"), rush02
    ("compile your project using the rules $NAME, clean and fclean") and
    C11 ex05 (whose moulinette transcript starts with `make clean`) all state
    rules that the behaviour tests never invoke, so a Makefile missing them
    built, ran, passed every case and still omitted a stated deliverable.

    Rules are checked by behaviour, never by grepping the Makefile - a rule can
    come from a variable or a pattern - and the behaviour has to be real:

    - The build rule runs after `fclean` and the binary is deleted by hand, so
      it has to produce the binary itself. Checked while the default target's
      binary still existed, a Makefile with no `all` passed.
    - `clean` has to remove the object files the build left. Exiting 0 is not
      enough: a name listed only in .PHONY is a target to make with nothing to
      do, so `make clean` exits 0 ("Nothing to be done") - and `make -n clean`
      prints that same line on stdout, so it cannot tell a real rule apart
      either. A Makefile that leaves no objects has nothing to clean and passes.
    - `fclean` has to remove the binary.

    Returns [(passed, description, expected, actual), ...] for the caller to
    fold into its own check() counter.
    """
    binary_path = os.path.join(student_dir, binary_name)
    results = []

    run_make(student_dir, "fclean")
    if os.path.exists(binary_path):
        os.remove(binary_path)

    # build_rule=None is the default target: C11 ex05's transcript just says `make`.
    result = run_make(student_dir, *([build_rule] if build_rule else []))
    built = result.returncode == 0 and os.path.exists(binary_path)
    shown = f"make {build_rule}" if build_rule else "make"
    results.append((
        built,
        f"`{shown}` builds {binary_name} from a clean tree",
        f"exit 0, {binary_name} present",
        "exit %d, %spresent (%s)" % (
            result.returncode,
            "" if os.path.exists(binary_path) else "not ",
            result.stderr.strip() or "no stderr",
        ),
    ))

    if clean:
        # Judged on its own: if the build rule above produced nothing (no
        # `all`, say), build through the default target so `clean` still has
        # objects to prove itself on.
        objects = _objects(student_dir)
        if not objects:
            run_make(student_dir)
            objects = _objects(student_dir)
        result = run_make(student_dir, "clean")
        left = _objects(student_dir) if objects else []
        results.append((
            result.returncode == 0 and not left,
            "`make clean` exists and removes the object files",
            "exit 0, no .o left",
            "exit %d, %s (%s)" % (
                result.returncode,
                ("left: " + ", ".join(os.path.relpath(p, student_dir) for p in left))
                if left else "no .o left",
                result.stderr.strip() or "no stderr",
            ),
        ))

    if fclean:
        result = run_make(student_dir, "fclean")
        results.append((
            result.returncode == 0 and not os.path.exists(binary_path),
            f"`make fclean` succeeds and removes {binary_name}",
            f"exit 0, {binary_name} gone",
            "exit %d, %s (%s)" % (
                result.returncode,
                binary_name + (" still present" if os.path.exists(binary_path) else " gone"),
                result.stderr.strip() or "no stderr",
            ),
        ))

    return results
