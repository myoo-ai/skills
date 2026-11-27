// Command orders-worker moves paid orders through fulfilment.
package main

import (
	"context"
	"log/slog"
	"os"
	"os/signal"
	"time"
)

func main() {
	if os.Getenv("DATABASE_URL") == "" {
		slog.Error("DATABASE_URL is not set")
		os.Exit(1)
	}
	ctx, stop := signal.NotifyContext(context.Background(), os.Interrupt)
	defer stop()
	tick := time.NewTicker(10 * time.Second)
	defer tick.Stop()
	for {
		select {
		case <-ctx.Done():
			return
		case <-tick.C:
			// The real worker claims orders in status 'processing' and ships them.
			slog.InfoContext(ctx, "polling for processing orders")
		}
	}
}
