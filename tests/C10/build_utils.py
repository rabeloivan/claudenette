import glob
import os
import subprocess

from utils.functions import check_allowed_functions
from utils.norminette import check_norminette


def discover_c_files(student_dir):
    return sorted(glob.glob(os.path.join(student_dir, "*.c")))


def check_all_c_files(student_dir, allowed):
    c_files = discover_c_files(student_dir)
    if not c_files:
        return False
    norm_ok = all(check_norminette(path) for path in c_files)
    fns_ok = all(check_allowed_functions(path, allowed) for path in c_files)
    return norm_ok and fns_ok


def build_via_makefile(student_dir, binary_name, timeout=30):
    try:
        result = subprocess.run(
            ["make"], cwd=student_dir, capture_output=True, text=True, timeout=timeout
        )
    except subprocess.TimeoutExpired:
        result = subprocess.CompletedProcess(["make"], -1, stdout="", stderr="TIMEOUT")
    binary_path = os.path.join(student_dir, binary_name)
    return result, binary_path


def cleanup_build(student_dir, binary_name):
    try:
        subprocess.run(
            ["make", "fclean"],
            cwd=student_dir,
            capture_output=True,
            text=True,
            timeout=30,
        )
    except subprocess.TimeoutExpired:
        pass

    binary_path = os.path.join(student_dir, binary_name)
    if os.path.exists(binary_path):
        os.remove(binary_path)

    for name in os.listdir(student_dir):
        if name.endswith(".o"):
            os.remove(os.path.join(student_dir, name))
