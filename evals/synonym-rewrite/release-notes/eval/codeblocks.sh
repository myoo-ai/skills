#!/bin/sh
# usage: codeblocks.sh <file>
# fails unless the fenced code blocks of <file> equal those of ../original/<file>
blocks() { awk '/^[[:space:]]*```/ { c = !c; print; next } c' "$1"; }
o=$(blocks "../original/$1")
n=$(blocks "$1")
test -n "$o" && test "$o" = "$n"
