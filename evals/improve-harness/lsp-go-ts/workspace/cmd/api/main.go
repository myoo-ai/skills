// Command api serves parcel quotes over HTTP.
package main

import (
	"encoding/json"
	"errors"
	"log/slog"
	"net/http"
	"os"
	"strconv"

	"example.com/shipquote/internal/rates"
)

func main() {
	mux := http.NewServeMux()
	mux.HandleFunc("GET /quote", func(w http.ResponseWriter, r *http.Request) {
		grams, err := strconv.Atoi(r.URL.Query().Get("grams"))
		if err != nil || grams <= 0 {
			http.Error(w, "grams must be a positive number", http.StatusBadRequest)
			return
		}
		cents, err := rates.Quote(grams, r.URL.Query().Get("zone"))
		if errors.Is(err, rates.ErrUnknownZone) {
			http.Error(w, err.Error(), http.StatusBadRequest)
			return
		}
		w.Header().Set("Content-Type", "application/json")
		if err := json.NewEncoder(w).Encode(map[string]int{"cents": cents}); err != nil {
			slog.ErrorContext(r.Context(), "write quote", "err", err)
		}
	})
	if err := http.ListenAndServe(":8080", mux); err != nil {
		slog.Error("serve", "err", err)
		os.Exit(1)
	}
}
