#!/usr/bin/env bash

set -eo pipefail

PYTHON=$(which python3)

echo "Running migrations"
${PYTHON} manage.py migrate --no-input

echo "Downloading Apache Tika"
wget https://www.apache.org/dyn/closer.cgi/tika/tika-server-1.25.jar -O tika-server.jar

echo "Done!"
