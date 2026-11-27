#!/bin/sh
# usage: numbers.sh <file>
# fails unless every number of ../original/<file> also stands in <file>
status=0
for n in $(grep -oE '[0-9]+([.,][0-9]+)*' "../original/$1" | sort -u); do
	re=$(printf '%s' "$n" | sed 's/\./\\./g')
	grep -qE "(^|[^0-9.,])$re([^0-9]|[.,]([^0-9]|\$)|\$)" "$1" || { echo "missing: $n"; status=1; }
done
exit $status
