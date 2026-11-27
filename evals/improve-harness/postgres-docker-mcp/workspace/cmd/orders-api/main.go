// Command orders-api serves the order HTTP API.
package main

import (
	"log/slog"
	"net/http"
	"os"
)

func main() {
	if os.Getenv("DATABASE_URL") == "" {
		slog.Error("DATABASE_URL is not set")
		os.Exit(1)
	}
	mux := http.NewServeMux()
	mux.HandleFunc("GET /healthz", func(w http.ResponseWriter, _ *http.Request) {
		w.WriteHeader(http.StatusNoContent)
	})
	if err := http.ListenAndServe(":8080", mux); err != nil {
		slog.Error("serve", "err", err)
		os.Exit(1)
	}
}
