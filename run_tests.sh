#!/bin/bash

rm -rf .pytest_cache

readlink=$(which greadlink 2>/dev/null) || readlink=$(which readlink)
base_dir=$(cd $(dirname $(${readlink} -f "$0")); pwd)

echo "Cleaning *.pyc files ..."
find . -name \*.pyc | xargs rm 2>/dev/null

python -m coverage run -m pytest -v -rsx -k "test_" --ignore=bin/
ecode=$?
coverage report -m --omit="*/venv/*"

if [ $ecode -eq 5 ]; then
    echo ".-----------------------------------------------------------------------."
    echo "|  WARNING: No tests found!                                             |"
    echo "'-----------------------------------------------------------------------'"
    exit 0
fi
exit $ecode
