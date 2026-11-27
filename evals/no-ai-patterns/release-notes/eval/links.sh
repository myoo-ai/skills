#!/bin/sh
# usage: links.sh <file>
# fails unless <file> keeps every URL of ../original/<file>
o=$(grep -oE 'https?://[^] )>"`]+' "../original/$1" | sort -u)
test -n "$o" || exit 1
status=0
for u in $o; do
	grep -qF "$u" "$1" || { echo "missing: $u"; status=1; }
done
exit $status
