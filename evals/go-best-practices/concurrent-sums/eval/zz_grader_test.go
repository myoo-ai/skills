package filesum

import (
	"context"
	"crypto/sha256"
	"encoding/hex"
	"errors"
	"io/fs"
	"os"
	"path/filepath"
	"slices"
	"strings"
	"testing"
)

func TestGraderSumAll(t *testing.T) {
	dir := t.TempDir()
	var paths []string
	want := map[string]string{}
	for i, name := range []string{"c.txt", "a.txt", "b.txt", "d.txt", "e.txt"} {
		p := filepath.Join(dir, name)
		data := []byte(strings.Repeat(name, i+1))
		if err := os.WriteFile(p, data, 0o600); err != nil {
			t.Fatal(err)
		}
		sum := sha256.Sum256(data)
		want[p] = hex.EncodeToString(sum[:])
		paths = append(paths, p)
	}
	broken := append(slices.Clone(paths), filepath.Join(dir, "gone-1.txt"), filepath.Join(dir, "gone-2.txt"))
	for _, workers := range []int{0, 1, 2, 16} {
		got, err := SumAll(context.Background(), paths, workers)
		if err != nil || len(got) != len(paths) {
			t.Fatalf("workers=%d: SumAll = %d results, %v", workers, len(got), err)
		}
		if !slices.IsSortedFunc(got, func(a, b Result) int { return strings.Compare(a.Path, b.Path) }) {
			t.Errorf("workers=%d: results not sorted by path: %v", workers, got)
		}
		for _, r := range got {
			if want[r.Path] != r.Sum {
				t.Errorf("workers=%d: %s sum = %s; want %s", workers, r.Path, r.Sum, want[r.Path])
			}
		}
		got, err = SumAll(context.Background(), broken, workers)
		if !errors.Is(err, fs.ErrNotExist) || !strings.Contains(err.Error(), "gone-1.txt") || !strings.Contains(err.Error(), "gone-2.txt") {
			t.Errorf("workers=%d: error = %v; want both missing files, matching fs.ErrNotExist", workers, err)
		}
		if len(got) != len(paths) {
			t.Errorf("workers=%d: %d results with failures; want %d", workers, len(got), len(paths))
		}
	}
	ctx, cancel := context.WithCancel(context.Background())
	cancel()
	if _, err := SumAll(ctx, paths, 2); !errors.Is(err, context.Canceled) {
		t.Errorf("canceled ctx: error = %v; want context.Canceled", err)
	}
}
