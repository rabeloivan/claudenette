import os
import shutil
import subprocess
import tempfile

SOURCE_SUFFIXES = (".c", ".h")


def run_make(cwd, args=None, timeout=60):
    try:
        result = subprocess.run(
            ["make"] + (args or []),
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return result.stdout + result.stderr, result.returncode
    except subprocess.TimeoutExpired:
        return "TIMEOUT", -1


def seeded_copy(student_dir):
    """Copy the student's sources and Makefile into a scratch directory.

    Building in place would drop libft.a and a pile of .o files into the graded
    directory, which for libft IS the directory the extra-files check inspects
    - so a build left half-finished by a failing rule would be reported as
    extra files against every other key. tests/C09/ex01 seeds a scratch dir for
    the same reason.
    """
    build_dir = tempfile.mkdtemp(prefix="claudenette_libft_make_")
    for name in os.listdir(student_dir):
        if name.endswith(SOURCE_SUFFIXES) or name == "Makefile":
            shutil.copy(os.path.join(student_dir, name), os.path.join(build_dir, name))
    return build_dir


def archive_is_ar(archive_path):
    """True when the file is a real ar archive whose members can be listed.

    The subject is explicit: "You must use the ar command to create your
    library. The use of libtool is strictly forbidden." An archive built by
    libtool still links, so nothing else in the pipeline would notice.
    """
    try:
        with open(archive_path, "rb") as handle:
            if handle.read(8) != b"!<arch>\n":
                return False
    except OSError:
        return False
    try:
        result = subprocess.run(
            ["ar", "t", archive_path], capture_output=True, text=True, timeout=10
        )
    except (subprocess.SubprocessError, OSError):
        return False
    return result.returncode == 0 and bool(result.stdout.strip())


def archive_defines(archive_path):
    """The function names libft.a defines, read from `nm` over the archive.

    Every harness compiles the student's ft_*.c directly, so nothing else in
    the pipeline ever links against libft.a - a Makefile whose SRCS forgot a
    file built an archive missing that function and still scored OK, while
    the evaluation links its tests against the archive and fails. Names are
    compared by symbol, not by member file name, so a Makefile that builds its
    objects somewhere else or under other names is judged on what the linker
    will actually find. Leading underscores are stripped (Mach-O prefixes one).
    """
    try:
        result = subprocess.run(
            ["nm", archive_path], capture_output=True, text=True, timeout=30
        )
    except (subprocess.SubprocessError, OSError):
        return set()
    defined = set()
    for line in result.stdout.splitlines():
        parts = line.split()
        if len(parts) == 3 and parts[1] == "T":
            defined.add(parts[2].lstrip("_"))
    return defined


def mentions_libtool(makefile_path):
    try:
        with open(makefile_path, encoding="utf-8", errors="replace") as handle:
            text = handle.read()
    except OSError:
        return False
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            continue
        if "libtool" in stripped:
            return True
    return False
