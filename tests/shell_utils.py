from utils.runner import run_test_case


def run_sh(file_path, interpreter="sh", cwd=None, env=None, args=None, timeout=5):
    # Every shell00/01 exercise turns in a single command line or short
    # script - not necessarily +x or shebang'd, since several are described
    # as "write a command line", not "write a script". Invoked via an
    # explicit interpreter rather than direct exec so a missing chmod +x
    # doesn't fail a test that isn't about chmod - the subject's own worked
    # examples do exactly this for git_commit.sh/git_ignore.sh ("bash
    # git_commit.sh"), so this isn't a guessed convention.
    return run_test_case(
        interpreter, args=[file_path] + (args or []), cwd=cwd, env=env, timeout=timeout
    )
