package stock

import (
	"errors"
	"io/fs"
	"path/filepath"
	"slices"
	"strings"
	"testing"
)

func TestGraderBehavior(t *testing.T) {
	missing := filepath.Join(t.TempDir(), "missing.json")
	if _, err := Load(missing); !errors.Is(err, fs.ErrNotExist) || !strings.Contains(err.Error(), "load stock from "+missing) {
		t.Errorf("Load(missing) error = %v", err)
	}
	items := []Item{{SKU: "NUT-2", Quantity: 7}, {SKU: "BOLT-1", Quantity: 3}, {SKU: "NUT-1", Quantity: 1}, {SKU: "WASHER", Quantity: 4}}
	SortBySKU(items)
	var skus []string
	for _, it := range items {
		skus = append(skus, it.SKU)
	}
	if !slices.Equal(skus, []string{"BOLT-1", "NUT-1", "NUT-2", "WASHER"}) {
		t.Errorf("SortBySKU = %v", skus)
	}
	if lo, hi, ok := Range(items); lo != 1 || hi != 7 || !ok {
		t.Errorf("Range = %d, %d, %v", lo, hi, ok)
	}
	if _, _, ok := Range(nil); ok {
		t.Error("Range(nil) ok = true")
	}
	if Clamp(-3, 10) != 0 || Clamp(4, 10) != 4 || Clamp(12, 10) != 10 {
		t.Error("Clamp is wrong")
	}
	totals := Totals(items)
	if len(totals) != 3 || totals["NUT"] != 8 || totals["BOLT"] != 3 || totals["WASHER"] != 4 {
		t.Errorf("Totals = %v", totals)
	}
	if got := Prefixes(totals); !slices.Equal(got, []string{"BOLT", "NUT", "WASHER"}) {
		t.Errorf("Prefixes = %v", got)
	}
	if !Contains(items, "NUT-1") || Contains(items, "NUT-9") {
		t.Error("Contains is wrong")
	}
	if got := Labels(3); !slices.Equal(got, []string{"BIN-01", "BIN-02", "BIN-03"}) || len(Labels(0)) != 0 {
		t.Errorf("Labels(3) = %v", got)
	}
	if got := Describe(42); got != "42" {
		t.Errorf("Describe(42) = %q", got)
	}
	doubled := Restock(items, func(it Item) Item { it.Quantity *= 2; return it })
	for i, it := range items {
		if doubled[i].SKU != it.SKU || doubled[i].Quantity != 2*it.Quantity {
			t.Errorf("Restock[%d] = %v", i, doubled[i])
		}
	}
}
