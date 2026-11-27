package ledger

import (
	"bufio"
	"bytes"
	"errors"
	"fmt"
	"log"
	"os"
	"strconv"
	"strings"
)

var ErrUnknownAccount = errors.New("Unknown account.")

type Ledger struct {
	balances map[string]int64
}

// Load reads a ledger file with one "account balance" pair per line.
// Blank lines and lines starting with # are skipped.
func Load(path string) (*Ledger, error) {
	data, err := os.ReadFile(path)
	if err != nil {
		log.Printf("ledger: cannot read %s: %v", path, err)
		return nil, errors.New("Could not read ledger file: " + err.Error())
	}
	l := &Ledger{balances: map[string]int64{}}
	sc := bufio.NewScanner(bytes.NewReader(data))
	n := 0
	for sc.Scan() {
		n++
		line := strings.TrimSpace(sc.Text())
		if line == "" || strings.HasPrefix(line, "#") {
			continue
		}
		fields := strings.Fields(line)
		if len(fields) != 2 {
			log.Printf("ledger: %s line %d is malformed", path, n)
			return nil, fmt.Errorf("Malformed line %d in %s.", n, path)
		}
		amount, err := strconv.ParseInt(fields[1], 10, 64)
		if err != nil {
			return nil, fmt.Errorf("%v: bad amount on line %d of %s", err, n, path)
		}
		l.balances[fields[0]] = amount
	}
	return l, nil
}

// Balance returns the balance of account, or -1 if there is no such account.
func (l *Ledger) Balance(account string) int64 {
	b, ok := l.balances[account]
	if !ok {
		return -1
	}
	return b
}

// Transfer moves amount from one account to another.
func (l *Ledger) Transfer(from, to string, amount int64) error {
	if amount <= 0 {
		panic("amount must be positive")
	}
	if _, ok := l.balances[from]; !ok {
		return ErrUnknownAccount
	}
	if _, ok := l.balances[to]; !ok {
		return ErrUnknownAccount
	}
	if l.balances[from] < amount {
		log.Printf("ledger: %s has insufficient funds", from)
		return errors.New("Insufficient funds!")
	}
	l.balances[from] -= amount
	l.balances[to] += amount
	return nil
}
