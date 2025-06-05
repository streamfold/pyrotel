#!/bin/bash

CWD="$(cd -P -- "$(dirname -- "$0")" && pwd -P)"

# Define the required environment variables
required_vars=("ROTEL_RELEASE" "ROTEL_ARCH" "ROTEL_PY_VERSION")

for var in "${required_vars[@]}"; do
    if [[ -z "${!var}" ]]; then
        echo "ERROR: Environment variable '$var' is not set or is empty" >&2
        exit 1
    fi
done

ROTEL_OUT_FILE=$CWD/../rotel/rotel-agent
if [ $# -eq 1 ]; then
  #echo "setting rotel out file to $1"
  ROTEL_OUT_FILE="$1"
fi

set -e

ROTEL_FILE="rotel_py_processor_${ROTEL_PY_VERSION}_${ROTEL_RELEASE}_${ROTEL_ARCH}.tar.gz"
ROTEL_REPO_OWNER=streamfold
ROTEL_REPO=rotel

$CWD/download-gh-asset.sh $ROTEL_REPO_OWNER $ROTEL_REPO $ROTEL_RELEASE $ROTEL_FILE

tar -O -zxf $ROTEL_FILE rotel > $ROTEL_OUT_FILE
rm $ROTEL_FILE

chmod +x $ROTEL_OUT_FILE
