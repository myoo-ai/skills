#!/bin/sh
# usage: names.sh <file>
# fails unless <file> contains every name listed in ../eval/names.txt, letter for letter
status=0
while IFS= read -r name; do
	test -n "$name" || continue
	grep -qF -- "$name" "$1" || { echo "missing: $name"; status=1; }
done < ../eval/names.txt
exit $status
