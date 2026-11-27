package attach

import (
	"net/http"
	"net/http/httptest"
	"os"
	"path/filepath"
	"testing"
)

func TestHandler(t *testing.T) {
	dir := t.TempDir()
	if err := os.WriteFile(filepath.Join(dir, "a.txt"), []byte("hello"), 0o600); err != nil {
		t.Fatal(err)
	}
	h := Handler(&Store{Dir: dir})
	for _, tc := range []struct {
		path string
		code int
	}{
		{"/files/a.txt", http.StatusOK},
		{"/files/missing.txt", http.StatusNotFound},
	} {
		t.Run(tc.path, func(t *testing.T) {
			rec := httptest.NewRecorder()
			h.ServeHTTP(rec, httptest.NewRequest(http.MethodGet, tc.path, nil))
			if rec.Code != tc.code {
				t.Errorf("GET %s = %d; want %d", tc.path, rec.Code, tc.code)
			}
		})
	}
}
