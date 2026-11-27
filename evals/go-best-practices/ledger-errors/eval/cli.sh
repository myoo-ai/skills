#!/bin/sh
# Builds cmd/ledger and checks its exit codes: 3 missing file, 4 unknown
# account, 5 insufficient funds, 0 success.
set -u
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
go build -o "$tmp/ledger" ./cmd/ledger || exit 1
printf 'alice 100\nbob 5\ncarol -1\n' > "$tmp/l.txt"
fail=0
check() {
	want=$1
	shift
	"$tmp/ledger" "$@" > /dev/null 2>&1
	got=$?
	if [ "$got" != "$want" ]; then
		echo "ledger $*: exit $got; want $want"
		fail=1
	fi
}
check 3 "$tmp/missing.txt" alice bob 1
check 4 "$tmp/l.txt" dave bob 1
check 4 "$tmp/l.txt" alice dave 1
check 5 "$tmp/l.txt" bob alice 6
check 5 "$tmp/l.txt" carol alice 1
check 0 "$tmp/l.txt" alice bob 1
exit $fail
