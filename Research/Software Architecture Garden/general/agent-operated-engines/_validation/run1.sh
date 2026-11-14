#!/usr/bin/env bash
# One logged run: run1.sh NN SCENARIO TAG
HERE=$(cd "$(dirname "$0")" && pwd)
echo "$(date +%T) start $1 $2 $3" >> "$HERE/batch.log"
"$HERE/validate.sh" "$1" "$2" "$3" > /dev/null 2>&1
echo "$(date +%T) end $1 $2 $3 exit $?" >> "$HERE/batch.log"
