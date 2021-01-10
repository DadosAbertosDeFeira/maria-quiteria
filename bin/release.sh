#!/usr/bin/env bash

set -eo pipefail

PYTHON=$(which python3)

echo "Running migrations"
${PYTHON} manage.py migrate --no-input

echo "Done!"
