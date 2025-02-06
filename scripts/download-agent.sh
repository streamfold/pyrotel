#!/bin/bash

CWD="$(cd -P -- "$(dirname -- "$0")" && pwd -P)"

set -e

ROTEL_ARCH="x86_64-unknown-linux-gnu"

if [ -z "$ROTEL_RELEASE" ]; then
  echo "Must set ROTEL_RELEASE"
  exit 1
fi

ROTEL_FILE="rotel_${ROTEL_RELEASE}_${ROTEL_ARCH}.tar.gz"
ROTEL_REPO_OWNER=streamfold
ROTEL_REPO=rotel

$CWD/download-gh-asset.sh $ROTEL_REPO_OWNER $ROTEL_REPO $ROTEL_RELEASE $ROTEL_FILE

tar -O -zxf $ROTEL_FILE rotel > $CWD/../rotel/rotel-agent
rm $ROTEL_FILE

chmod +x $CWD/../app/rotel/rotel-agent
