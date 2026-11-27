// Package rates prices parcels by weight and destination zone.
package rates

import (
	"errors"
	"fmt"
)

// ErrUnknownZone reports a zone without a price table.
var ErrUnknownZone = errors.New("unknown zone")

var perKiloCents = map[string]int{
	"domestic": 450,
	"eu":       890,
	"world":    1690,
}

// Quote returns the price in cents of a parcel of weightGrams sent to zone.
func Quote(weightGrams int, zone string) (int, error) {
	rate, ok := perKiloCents[zone]
	if !ok {
		return 0, fmt.Errorf("quote %q: %w", zone, ErrUnknownZone)
	}
	kilos := max(1, (weightGrams+999)/1000)
	return kilos * rate, nil
}
