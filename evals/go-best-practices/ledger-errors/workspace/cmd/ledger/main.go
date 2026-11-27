// Command ledger moves money between accounts in a ledger file.
//
// Usage: ledger FILE FROM TO AMOUNT
package main

import (
	"fmt"
	"os"
	"strconv"
	"strings"

	"example.com/ledger"
)

func main() {
	if len(os.Args) != 5 {
		fmt.Fprintln(os.Stderr, "usage: ledger FILE FROM TO AMOUNT")
		os.Exit(2)
	}
	amount, err := strconv.ParseInt(os.Args[4], 10, 64)
	if err != nil {
		fmt.Fprintln(os.Stderr, "amount must be a number")
		os.Exit(2)
	}
	l, err := ledger.Load(os.Args[1])
	if err != nil {
		if strings.Contains(err.Error(), "no such file") {
			fmt.Fprintln(os.Stderr, "ledger file does not exist")
			os.Exit(3)
		}
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
	if b := l.Balance(os.Args[2]); b == -1 {
		fmt.Fprintf(os.Stderr, "no account %s\n", os.Args[2])
		os.Exit(4)
	}
	err = l.Transfer(os.Args[2], os.Args[3], amount)
	if err == ledger.ErrUnknownAccount {
		fmt.Fprintln(os.Stderr, "unknown account")
		os.Exit(4)
	}
	if err != nil && strings.Contains(err.Error(), "Insufficient") {
		fmt.Fprintln(os.Stderr, "not enough money")
		os.Exit(5)
	}
	if err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
	fmt.Printf("%s: %d\n", os.Args[2], l.Balance(os.Args[2]))
}
