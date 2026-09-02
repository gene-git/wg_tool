#!/usr/bin/bash
#
# Clean up before running tests
#
set -euo pipefail
testdir="$(dirname "$(realpath "${BASH_SOURCE[0]}")")"

cd $testdir
echo "Cleaning $testdir"
/usr/bin/rm -rf Data Data-wg Edits out.diff
exit 0
