import subprocess


def run_test_case(executable_path, input_data=None, timeout=2, args=None, cwd=None, env=None):
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
