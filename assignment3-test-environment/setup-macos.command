#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")"
python3 -c 'import sys; assert sys.version_info[:2] == (3, 14), "Install Python 3.14 (tested with 3.14.4) first"'
if [ ! -x .venv/bin/python ]; then
    python3 -m venv .venv
fi
.venv/bin/python -m pip install --cache-dir .cache/pip -r requirements.txt
.venv/bin/python -m pytest tests/test_environment.py -v
