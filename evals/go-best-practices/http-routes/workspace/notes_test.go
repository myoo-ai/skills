package notes

import (
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"
)

func TestListNotes(t *testing.T) {
	var s Store
	s.Add("buy milk")
	s.Add("call example.com support")

	rec := httptest.NewRecorder()
	Handler(&s).ServeHTTP(rec, httptest.NewRequest(http.MethodGet, "/notes", nil))
	if rec.Code != http.StatusOK {
		t.Fatalf("GET /notes status = %d; want %d", rec.Code, http.StatusOK)
	}
	var got []Note
	if err := json.NewDecoder(rec.Body).Decode(&got); err != nil {
		t.Fatal(err)
	}
	if len(got) != 2 || got[0].ID != 1 || got[1].Text != "call example.com support" {
		t.Errorf("GET /notes = %v", got)
	}
}
