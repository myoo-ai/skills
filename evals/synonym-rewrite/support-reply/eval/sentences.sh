#!/bin/sh
# usage: sentences.sh <file>
# fails unless <file> has as many sentences as ../original/<file>, give or take 1
count() { grep -oE '[.!?]+(["”)]?)( |$)' "$1" | wc -l; }
o=$(count "../original/$1")
n=$(count "$1")
echo "$n sentences, original $o"
test "$n" -ge $((o - 1)) && test "$n" -le $((o + 1))
