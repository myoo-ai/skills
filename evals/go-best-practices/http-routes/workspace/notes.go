package notes

import (
	"encoding/json"
	"maps"
	"net/http"
	"slices"
	"sync"
)

type Note struct {
	ID   int    `json:"id"`
	Text string `json:"text"`
}

type Store struct {
	mu    sync.Mutex
	notes map[int]Note
	next  int
}

func (s *Store) Add(text string) Note {
	s.mu.Lock()
	defer s.mu.Unlock()
	if s.notes == nil {
		s.notes = make(map[int]Note)
	}
	s.next++
	n := Note{ID: s.next, Text: text}
	s.notes[n.ID] = n
	return n
}

func (s *Store) List() []Note {
	s.mu.Lock()
	defer s.mu.Unlock()
	out := make([]Note, 0, len(s.notes))
	for _, id := range slices.Sorted(maps.Keys(s.notes)) {
		out = append(out, s.notes[id])
	}
	return out
}

func Handler(s *Store) http.Handler {
	mux := http.NewServeMux()
	mux.HandleFunc("/notes", func(w http.ResponseWriter, r *http.Request) {
		if r.Method != http.MethodGet {
			http.Error(w, "method not allowed", http.StatusMethodNotAllowed)
			return
		}
		writeJSON(w, http.StatusOK, s.List())
	})
	return mux
}

func writeJSON(w http.ResponseWriter, status int, v any) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(status)
	json.NewEncoder(w).Encode(v)
}
