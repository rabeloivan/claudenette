#!/usr/bin/env python3
"""Install only checkout-local Python dependencies; no sudo, venv or system pip needed."""
import os
import hashlib
import json
import zipfile
from pathlib import Path
import subprocess
import sys
import tempfile
import urllib.request

REPO = Path(__file__).resolve().parent
# Bootstrap a pinned PyPI wheel in a temporary directory, even without pip/venv.
PIP_VERSION = '25.3'
PIP_METADATA = f'https://pypi.org/pypi/pip/{PIP_VERSION}/json'


def main():
    if sys.version_info < (3, 10):
        print('Python 3.10+ is required (Ubuntu 22.04 provides Python 3.10).', file=sys.stderr)
        return 2
    print('Installing Claudenette dependencies locally in .deps/ ...', flush=True)
    with tempfile.TemporaryDirectory(prefix='claudenette-install-') as directory:
        pip = Path(directory) / 'pip.whl'
        try:
            with urllib.request.urlopen(PIP_METADATA, timeout=30) as response:
                metadata = json.load(response)
            wheel = next(item for item in metadata['urls'] if item['filename'].endswith('.whl'))
            with urllib.request.urlopen(wheel['url'], timeout=30) as response:
                pip.write_bytes(response.read())
            if hashlib.sha256(pip.read_bytes()).hexdigest() != wheel['digests']['sha256']:
                raise ValueError('pip download checksum mismatch')
            with zipfile.ZipFile(pip) as archive:
                archive.extractall(Path(directory) / 'bootstrap')
            bootstrap_env = {**os.environ, 'PYTHONPATH': str(Path(directory) / 'bootstrap')}
            result = subprocess.run([
                sys.executable, '-m', 'pip', '--isolated', 'install', '--disable-pip-version-check',
                '--no-warn-script-location', '--no-input', '--upgrade',
                '--target', str(REPO / '.deps'), '-r', str(REPO / 'requirements.txt'),
            ], capture_output=True, text=True, env=bootstrap_env)
        except (OSError, ValueError) as exc:
            print(f'Installation failed: {exc}. Check network access and retry.', file=sys.stderr)
            return 2
        if result.returncode:
            print(result.stdout + result.stderr, file=sys.stderr)
            return 2
    env = {**os.environ, 'PYTHONPATH': str(REPO / '.deps')}
    check = subprocess.run([sys.executable, '-c', 'import rich, norminette'], env=env,
                           capture_output=True, text=True)
    if check.returncode:
        print(check.stderr, file=sys.stderr)
        return 2
    print('Ready. From your submission directory, run:')
    print(f'  python3 {REPO / "main.py"}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
