import os
import subprocess
import resource

# Expected crash probes must not leave `core` files in the graded directory.
# Lower only this process's soft limit; children (including cc) inherit it.
_, core_hard_limit = resource.getrlimit(resource.RLIMIT_CORE)
resource.setrlimit(resource.RLIMIT_CORE, (0, core_hard_limit))
RUNTIME_ISSUES = []

# Make the allocator hand back DIRTY memory to whatever we run.
#
# tests/free_tracker.c poisons malloc for harness-built binaries, but the
# whole-program projects (bsq, rush01, rush02, the C10 Makefile exercises)
# build their own binary through make, so nothing links the tracker and their
# malloc returns the freshly-zeroed pages the OS supplies. That silently hides
# a whole class of bug: a mutation probe over bsq found `ft_memset(&map, 0,
# sizeof(t_map))`, two '\0' terminators and a zeroed length could all be
# deleted while the tests still passed, purely because the memory happened to
# already be zero.
#
# Both libcs can do this natively, so it costs nothing and needs no cooperation
# from the student's Makefile. Each variable is simply ignored by the other
# platform:
#   MALLOC_PERTURB_ (glibc)  - allocated bytes become (byte)(v ^ 0xff); 85
#                              gives 0xAA, matching free_tracker's poison.
#   MallocScribble  (macOS)  - allocated memory filled with 0xAA, freed 0x55.
#
# This is not a trick: malloc has never promised zeroed memory, so correct code
# already initialises what it allocates.
DIRTY_ALLOC_ENV = {
    "MALLOC_PERTURB_": "85",
    "MallocScribble": "1",
}


def run_test_case(executable_path, input_data=None, timeout=2, args=None, cwd=None, env=None):
    # A caller passing env= means "exactly this environment", so layer the
    # allocator settings on top of whatever they asked for rather than
    # replacing it; passing nothing keeps the inherited environment.
    if env is None:
        env = {**os.environ, **DIRTY_ALLOC_ENV}
    else:
        env = {**env, **DIRTY_ALLOC_ENV}
    try:
        # The with-block closes the pipes and reaps the child on every way
        # out of it - a timed-out child used to stay a <defunct> zombie, its
        # pipes open, until some later Popen and the garbage collector got
        # to them. Its exit wait()s rather than communicate()s: a grandchild
        # the program started could still hold stdout open, and reading to
        # EOF would block on it.
        with subprocess.Popen(
            [executable_path] + (args or []),
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=cwd,
            env=env,
        ) as process:
            # Binary mode, decoded manually below - Popen's text=True mode
            # always applies universal-newline translation (e.g. a raw 0x0D
            # byte in the program's actual output silently becomes 0x0A) with
            # no way to turn it off, unlike open()'s newline="" - so text mode
            # can't guarantee byte-for-byte round-tripping the way
            # encoding="latin-1" alone implies it does.
            input_bytes = input_data.encode("latin-1") if input_data is not None else None
            try:
                stdout_data, stderr_data = process.communicate(
                    input=input_bytes, timeout=timeout
                )
            except subprocess.TimeoutExpired:
                RUNTIME_ISSUES.append(f"Program timed out after {timeout:g}s")
                process.kill()
                return "", "TIMEOUT", -1
        stdout_text = stdout_data.decode("latin-1")
        # A process killed by a signal must never compare equal to the output
        # it managed to write first. Most tests compare stdout alone, and a
        # function that prints every digit and then segfaults - a stack
        # smashed on return, a write through a freed pointer - produced
        # exactly the expected bytes and scored OK. Appending the signal here
        # fails every such comparison at once and names the cause in the
        # "got:" line; tests that check `code` themselves are unaffected.
        # stdout only: a marker in stderr would satisfy the checks that only
        # ask whether an error was reported at all.
        if process.returncode < 0:
            RUNTIME_ISSUES.append(f"Program crashed (signal {-process.returncode})")
            stdout_text += f"\n[killed by signal {-process.returncode}]"
        return stdout_text, stderr_data.decode("latin-1"), process.returncode

    except Exception as e:
        return "", str(e), -1
