package rates

import (
	"errors"
	"testing"
)

func TestQuote(t *testing.T) {
	tests := []struct {
		name   string
		grams  int
		zone   string
		want   int
		hasErr bool
	}{
		{"light domestic", 200, "domestic", 450, false},
		{"two kilos eu", 1500, "eu", 1780, false},
		{"unknown zone", 100, "moon", 0, true},
	}
	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got, err := Quote(tt.grams, tt.zone)
			if tt.hasErr != errors.Is(err, ErrUnknownZone) {
				t.Fatalf("Quote(%d, %q) error = %v", tt.grams, tt.zone, err)
			}
			if got != tt.want {
				t.Errorf("Quote(%d, %q) = %d; want %d", tt.grams, tt.zone, got, tt.want)
			}
		})
	}
}
