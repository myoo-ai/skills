// Package attach serves uploaded attachments from a directory.
package attach

import (
	"errors"
	"io/fs"
	"net/http"
	"os"
	"path/filepath"
	"strings"
)

// Store reads attachments from Dir.
type Store struct {
	Dir string
}

// Read returns the content of the attachment called name. Names may
// contain slashes for attachments in subdirectories.
func (s *Store) Read(name string) ([]byte, error) {
	if strings.Contains(name, "..") {
		return nil, errors.New("invalid attachment name")
	}
	return os.ReadFile(filepath.Join(s.Dir, name))
}

// Handler serves GET /files/{name...}.
func Handler(s *Store) http.Handler {
	mux := http.NewServeMux()
	mux.HandleFunc("GET /files/{name...}", func(w http.ResponseWriter, r *http.Request) {
		data, err := s.Read(r.PathValue("name"))
		if errors.Is(err, fs.ErrNotExist) {
			http.NotFound(w, r)
			return
		}
		if err != nil {
			http.Error(w, "bad request", http.StatusBadRequest)
			return
		}
		w.Header().Set("Content-Type", "application/octet-stream")
		w.Write(data)
	})
	return mux
}
