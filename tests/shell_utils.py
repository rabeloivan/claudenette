import time

from utils.runner import run_test_case

# GNU ls's "six months": half an average Gregorian year, in seconds.
SIX_MONTHS = 31556952 // 2
MONTHS = ("Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")


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


def ls_date(mtime, now=None):
    """The date column `ls -l` prints for mtime, in local time.

    ls prints HH:MM for a timestamp from the last six months, and the year
    in its place for anything older or in the future - GNU ls's rule, which
    the moulinette's machines use.
    """
    now = time.time() if now is None else now
    t = time.localtime(mtime)
    recent = now - SIX_MONTHS < mtime < now
    tail = f"{t.tm_hour:02d}:{t.tm_min:02d}" if recent else f" {t.tm_year}"
    return f"{MONTHS[t.tm_mon - 1]} {t.tm_mday:2d} {tail}"


def ls_date_matches(mtime, wanted):
    """Whether ls -l shows mtime as the subject's date, e.g. "Jun  1 23:42".

    The subjects give dates as ls -l prints them and add: "A year will be
    accepted instead of the time in the file's timestamp". So the month and
    day must match, and the time must too whenever ls would print it; a
    timestamp old enough to be shown with its year is accepted with any.
    """
    shown = ls_date(mtime)
    if shown == wanted:
        return True, shown
    month_day = wanted[:6]
    return shown[:6] == month_day and ":" not in shown, shown
