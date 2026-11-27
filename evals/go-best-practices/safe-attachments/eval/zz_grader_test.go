package attach

import (
	"net/http"
	"net/http/httptest"
	"os"
	"path/filepath"
	"strings"
	"testing"
)

func TestGraderConfinement(t *testing.T) {
	base := t.TempDir()
	dir := filepath.Join(base, "uploads")
	write := func(path, content string) {
		t.Helper()
		if err := os.MkdirAll(filepath.Dir(path), 0o700); err != nil {
			t.Fatal(err)
		}
		if err := os.WriteFile(path, []byte(content), 0o600); err != nil {
			t.Fatal(err)
		}
	}
	link := func(target, path string) {
		t.Helper()
		if err := os.Symlink(target, path); err != nil {
			t.Fatal(err)
		}
	}
	write(filepath.Join(base, "secret.txt"), "TOPSECRET")
	write(filepath.Join(base, "outside", "key.txt"), "TOPSECRET")
	write(filepath.Join(dir, "a.txt"), "alpha")
	write(filepath.Join(dir, "q3..q4-report.txt"), "report")
	write(filepath.Join(dir, "sub", "b.txt"), "beta")
	link(filepath.Join(base, "secret.txt"), filepath.Join(dir, "abs-out.txt"))
	link("../secret.txt", filepath.Join(dir, "rel-out.txt"))
	link("../outside", filepath.Join(dir, "outdir"))
	link("a.txt", filepath.Join(dir, "dedupe.txt"))
	link("../a.txt", filepath.Join(dir, "sub", "up.txt"))
	link("sub", filepath.Join(dir, "sublink"))

	s := &Store{Dir: dir}
	for name, want := range map[string]string{
		"a.txt":             "alpha",
		"q3..q4-report.txt": "report",
		"sub/b.txt":         "beta",
		"dedupe.txt":        "alpha",
		"sub/up.txt":        "alpha",
		"sublink/b.txt":     "beta",
	} {
		got, err := s.Read(name)
		if err != nil || string(got) != want {
			t.Errorf("Read(%q) = %q, %v; want %q", name, got, err, want)
		}
	}
	for _, name := range []string{
		"../secret.txt",
		"sub/../../secret.txt",
		"abs-out.txt",
		"rel-out.txt",
		"outdir/key.txt",
	} {
		got, err := s.Read(name)
		if err == nil || strings.Contains(string(got), "TOPSECRET") {
			t.Errorf("Read(%q) = %q, %v; want an error", name, got, err)
		}
	}

	h := Handler(s)
	for path, code := range map[string]int{
		"/files/a.txt":          http.StatusOK,
		"/files/dedupe.txt":     http.StatusOK,
		"/files/missing.txt":    http.StatusNotFound,
		"/files/abs-out.txt":    0,
		"/files/rel-out.txt":    0,
		"/files/outdir/key.txt": 0,
	} {
		rec := httptest.NewRecorder()
		h.ServeHTTP(rec, httptest.NewRequest(http.MethodGet, path, nil))
		if code != 0 && rec.Code != code {
			t.Errorf("GET %s = %d; want %d", path, rec.Code, code)
		}
		if code == 0 && (rec.Code == http.StatusOK || strings.Contains(rec.Body.String(), "TOPSECRET")) {
			t.Errorf("GET %s = %d %q; want an error status", path, rec.Code, rec.Body.String())
		}
	}
}
