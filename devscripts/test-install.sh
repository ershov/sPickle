#!/bin/bash

set -ueo pipefail

SRCDIR="$(realpath "$(dirname -- "${BASH_SOURCE[0]}")"/..)"
TMPDIR=$(mktemp -d)

trap 'rm -rf $TMPDIR' EXIT

cd $TMPDIR
pwd
virtualenv -q -p python3 .venv
. .venv/bin/activate
LATEST=$(ls -1 "$SRCDIR"/dist/restrictedpickle-*.whl | sort -r | head -1)
echo $LATEST
pip install $LATEST
python -c 'import restrictedpickle; print(restrictedpickle.VERSION)'
echo OK
