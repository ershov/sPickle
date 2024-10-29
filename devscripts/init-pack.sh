#!/bin/bash

set -ueo pipefail

[[ -f .venv/bin/activate ]] || virtualenv -q -p python3 .venv
chmod 755 .venv/bin/activate

. .venv/bin/activate
# pip3 -q install -r requirements.txt

# set up packaging environment
pip3 -q install setuptools wheel twine

