#!/bin/sh
# usage: swapped.sh <file> <percent>
# fails unless at least <percent> % of the distinct words of 5 or more letters
# in the prose of ../original/<file> (code and link targets left out) are gone from <file>
words() {
	awk '/^[[:space:]]*```/ { c = !c; next } !c' "$1" |
		sed 's/`[^`]*`//g; s/](\([^)]*\))/]/g; s/https\{0,1\}:[^ ]*//g' |
		tr -s '[:space:][:punct:]' '\n\n' | tr 'A-Z' 'a-z' |
		awk -v tag="$2" 'length($0) >= 5 && $0 !~ /[0-9]/ { print tag, $0 }'
}
{ words "../original/$1" o; words "$1" n; } | awk -v pct="$2" '
	$1 == "o" { o[$2] = 1 }
	$1 == "n" { n[$2] = 1 }
	END {
		for (w in o) { t++; if (!(w in n)) g++ }
		printf "%d of %d words swapped\n", g, t
		exit !(t > 0 && g * 100 >= pct * t)
	}'
