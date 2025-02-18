#!/bin/bash

CWD="$(cd -P -- "$(dirname -- "$0")" && pwd -P)"

if [ -z "$ROTEL_RELEASE" ]; then
  echo "Must set ROTEL_RELEASE"
  exit 1
fi

ROTEL_OUT_FILE=$CWD/../rotel/rotel-agent
if [ $# -eq 1 ]; then
  echo "setting rotel out file to $1"
  ROTEL_OUT_FILE="$1"
fi

set -e

ROTEL_FILE="rotel_${ROTEL_RELEASE}_${ROTEL_ARCH}.tar.gz"
ROTEL_REPO_OWNER=streamfold
ROTEL_REPO=rotel

$CWD/download-gh-asset.sh $ROTEL_REPO_OWNER $ROTEL_REPO $ROTEL_RELEASE $ROTEL_FILE

tar -O -zxf $ROTEL_FILE rotel > $ROTEL_OUT_FILE
rm $ROTEL_FILE

chmod +x $ROTEL_OUT_FILE
