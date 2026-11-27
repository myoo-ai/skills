package filesum

import (
	"os"
	"path/filepath"
	"testing"
)

func TestSum(t *testing.T) {
	path := filepath.Join(t.TempDir(), "hello.txt")
	if err := os.WriteFile(path, []byte("hello\n"), 0o600); err != nil {
		t.Fatal(err)
	}
	got, err := Sum(path)
	if err != nil {
		t.Fatal(err)
	}
	const want = "5891b5b522d5df086d0ff0b110fbd9d21bb4fc7163af34d08286a2e846f6be03"
	if got != want {
		t.Errorf("Sum(%q) = %s; want %s", path, got, want)
	}
}
