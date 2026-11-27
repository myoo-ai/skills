package ledger

import (
	"errors"
	"io/fs"
	"os"
	"path/filepath"
	"strings"
	"testing"
)

func graderLedger(t *testing.T, content string) (string, *Ledger, error) {
	t.Helper()
	path := filepath.Join(t.TempDir(), "ledger.txt")
	if err := os.WriteFile(path, []byte(content), 0o600); err != nil {
		t.Fatal(err)
	}
	l, err := Load(path)
	return path, l, err
}

// graderBalance accepts either (int64, bool) or (int64, error) results.
func graderBalance(t *testing.T, l *Ledger, account string) (int64, bool) {
	t.Helper()
	switch f := any(l.Balance).(type) {
	case func(string) (int64, bool):
		return f(account)
	case func(string) (int64, error):
		b, err := f(account)
		if err != nil && !errors.Is(err, ErrUnknownAccount) {
			t.Errorf("Balance(%q) error = %v; want it to match ErrUnknownAccount", account, err)
		}
		return b, err == nil
	default:
		t.Fatalf("Balance has type %T; want an ok bool or an error result", l.Balance)
		return 0, false
	}
}

func graderNoPanic(t *testing.T, name string, f func() error) (err error) {
	t.Helper()
	defer func() {
		if r := recover(); r != nil {
			t.Errorf("%s panicked: %v", name, r)
		}
	}()
	return f()
}

func TestGraderErrors(t *testing.T) {
	missing := filepath.Join(t.TempDir(), "nope.txt")
	if _, err := Load(missing); !errors.Is(err, fs.ErrNotExist) || !strings.Contains(err.Error(), "nope.txt") {
		t.Errorf("Load(missing) error = %v; want it to match fs.ErrNotExist and name the file", err)
	}

	if _, _, err := graderLedger(t, "alice 10\nbob ten\n"); err == nil || !strings.Contains(err.Error(), "2") {
		t.Errorf("Load(bad amount) error = %v; want an error naming line 2", err)
	}
	if _, _, err := graderLedger(t, "alice 10\n\nbob\n"); err == nil || !strings.Contains(err.Error(), "3") {
		t.Errorf("Load(malformed) error = %v; want an error naming line 3", err)
	}

	_, l, err := graderLedger(t, "# accounts\nalice 100\nbob 5\ncarol -1\n")
	if err != nil {
		t.Fatalf("Load = %v", err)
	}
	if b, ok := graderBalance(t, l, "carol"); !ok || b != -1 {
		t.Errorf("Balance(carol) = %d, %v; want -1, found", b, ok)
	}
	if _, ok := graderBalance(t, l, "dave"); ok {
		t.Error("Balance(dave) reported an account that does not exist")
	}

	for _, tc := range []struct {
		from, to string
		amount   int64
		want     error
	}{
		{"dave", "bob", 1, ErrUnknownAccount},
		{"alice", "dave", 1, ErrUnknownAccount},
		{"bob", "alice", 6, ErrInsufficientFunds},
	} {
		err := l.Transfer(tc.from, tc.to, tc.amount)
		if !errors.Is(err, tc.want) {
			t.Errorf("Transfer(%s, %s, %d) = %v; want %v", tc.from, tc.to, tc.amount, err, tc.want)
		}
	}
	if err := l.Transfer("bob", "alice", 6); err == nil || !strings.Contains(err.Error(), "bob") {
		t.Errorf("Transfer(bob, alice, 6) = %v; want an error naming the account", err)
	}
	for _, amount := range []int64{0, -5} {
		if err := graderNoPanic(t, "Transfer", func() error { return l.Transfer("alice", "bob", amount) }); err == nil {
			t.Errorf("Transfer(alice, bob, %d) = nil; want an error", amount)
		}
	}
	if err := l.Transfer("alice", "bob", 40); err != nil {
		t.Fatalf("Transfer(alice, bob, 40) = %v", err)
	}
	if a, _ := graderBalance(t, l, "alice"); a != 60 {
		t.Errorf("Balance(alice) = %d after transfer; want 60", a)
	}
	if b, _ := graderBalance(t, l, "bob"); b != 45 {
		t.Errorf("Balance(bob) = %d after transfer; want 45", b)
	}
}
