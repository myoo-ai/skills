package stock

import (
	"encoding/json"
	"errors"
	"fmt"
	"io/ioutil"
	"os"
	"sort"
	"strings"
	"sync"
)

type Item struct {
	SKU      string `json:"sku"`
	Name     string `json:"name"`
	Quantity int    `json:"quantity"`
}

func Load(path string) ([]Item, error) {
	data, err := ioutil.ReadFile(path)
	if err != nil {
		var pe *os.PathError
		if errors.As(err, &pe) {
			return nil, fmt.Errorf("load stock from %s: %w", pe.Path, err)
		}
		return nil, err
	}
	var items []Item
	if err := json.Unmarshal(data, &items); err != nil {
		return nil, fmt.Errorf("parse stock: %w", err)
	}
	return items, nil
}

func Save(path string, items []Item) error {
	data, err := json.MarshalIndent(items, "", "  ")
	if err != nil {
		return fmt.Errorf("encode stock: %w", err)
	}
	return ioutil.WriteFile(path, data, 0o644)
}

func SortBySKU(items []Item) {
	sort.Slice(items, func(i, j int) bool {
		return items[i].SKU < items[j].SKU
	})
}

func Range(items []Item) (lo, hi int, ok bool) {
	if len(items) == 0 {
		return 0, 0, false
	}
	lo, hi = items[0].Quantity, items[0].Quantity
	for i := 1; i < len(items); i++ {
		if items[i].Quantity < lo {
			lo = items[i].Quantity
		}
		if items[i].Quantity > hi {
			hi = items[i].Quantity
		}
	}
	return lo, hi, true
}

func Clamp(q, limit int) int {
	if q < 0 {
		return 0
	}
	if q > limit {
		return limit
	}
	return q
}

func Totals(items []Item) map[string]int {
	totals := make(map[string]int)
	for _, it := range items {
		prefix := it.SKU
		if i := strings.Index(it.SKU, "-"); i >= 0 {
			prefix = it.SKU[:i]
		}
		totals[prefix] += it.Quantity
	}
	return totals
}

func Prefixes(totals map[string]int) []string {
	keys := make([]string, 0, len(totals))
	for k := range totals {
		keys = append(keys, k)
	}
	sort.Strings(keys)
	return keys
}

func Contains(items []Item, sku string) bool {
	for i := 0; i < len(items); i++ {
		if items[i].SKU == sku {
			return true
		}
	}
	return false
}

func Labels(n int) []string {
	var out []string
	for i := 0; i < n; i++ {
		out = append(out, fmt.Sprintf("BIN-%02d", i+1))
	}
	return out
}

func Describe(v interface{}) string {
	return fmt.Sprintf("%v", v)
}

func Restock(items []Item, fn func(Item) Item) []Item {
	out := make([]Item, len(items))
	var wg sync.WaitGroup
	for i, it := range items {
		i, it := i, it
		wg.Add(1)
		go func() {
			defer wg.Done()
			out[i] = fn(it)
		}()
	}
	wg.Wait()
	return out
}
