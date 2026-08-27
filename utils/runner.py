import os
import subprocess

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
        process = subprocess.Popen(
            [executable_path] + (args or []),
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=cwd,
            env=env,
        )
        # Binary mode, decoded manually below - Popen's text=True mode always
        # applies universal-newline translation (e.g. a raw 0x0D byte in the
        # program's actual output silently becomes 0x0A) with no way to turn
        # it off, unlike open()'s newline="" - so text mode can't guarantee
        # byte-for-byte round-tripping the way encoding="latin-1" alone
        # implies it does.
        input_bytes = input_data.encode("latin-1") if input_data is not None else None
        stdout_data, stderr_data = process.communicate(
            input=input_bytes, timeout=timeout
        )
        return stdout_data.decode("latin-1"), stderr_data.decode("latin-1"), process.returncode

    except subprocess.TimeoutExpired:
        process.kill()
        return "", "TIMEOUT", -1

    except Exception as e:
        return "", str(e), -1
