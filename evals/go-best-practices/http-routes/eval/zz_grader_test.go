package notes

import (
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"strings"
	"testing"
)

func TestGraderRoutes(t *testing.T) {
	var s Store
	s.Add("first")
	s.Add("second")
	h := Handler(&s)
	do := func(method, path string) *httptest.ResponseRecorder {
		rec := httptest.NewRecorder()
		h.ServeHTTP(rec, httptest.NewRequest(method, path, nil))
		return rec
	}
	rec := do(http.MethodGet, "/notes/2")
	var n Note
	if rec.Code != http.StatusOK || json.NewDecoder(rec.Body).Decode(&n) != nil || n.ID != 2 || n.Text != "second" {
		t.Errorf("GET /notes/2 = %d %+v", rec.Code, n)
	}
	for _, c := range []struct {
		method, path string
		want         int
	}{
		{http.MethodGet, "/notes/99", http.StatusNotFound},
		{http.MethodGet, "/notes/abc", http.StatusBadRequest},
		{http.MethodDelete, "/notes/1", http.StatusNoContent},
		{http.MethodGet, "/notes/1", http.StatusNotFound},
		{http.MethodDelete, "/notes/1", http.StatusNotFound},
		{http.MethodGet, "/notes", http.StatusOK},
	} {
		if got := do(c.method, c.path).Code; got != c.want {
			t.Errorf("%s %s = %d; want %d", c.method, c.path, got, c.want)
		}
	}
	for _, c := range []struct{ method, path, allow string }{
		{http.MethodPost, "/notes/2", "DELETE"},
		{http.MethodPut, "/notes/2", "GET"},
		{http.MethodPost, "/notes", "GET"},
	} {
		rec := do(c.method, c.path)
		if rec.Code != http.StatusMethodNotAllowed || !strings.Contains(rec.Header().Get("Allow"), c.allow) {
			t.Errorf("%s %s = %d, Allow %q; want 405 listing %s", c.method, c.path, rec.Code, rec.Header().Get("Allow"), c.allow)
		}
	}
}
