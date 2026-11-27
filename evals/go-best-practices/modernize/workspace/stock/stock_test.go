package stock

import (
	"io/ioutil"
	"os"
	"path/filepath"
	"reflect"
	"testing"
)

func TestSaveLoad(t *testing.T) {
	dir, err := ioutil.TempDir("", "stock")
	if err != nil {
		t.Fatal(err)
	}
	defer os.RemoveAll(dir)

	path := filepath.Join(dir, "stock.json")
	want := []Item{{SKU: "BOLT-10", Name: "Bolt", Quantity: 40}}
	if err := Save(path, want); err != nil {
		t.Fatal(err)
	}
	got, err := Load(path)
	if err != nil {
		t.Fatal(err)
	}
	if !reflect.DeepEqual(got, want) {
		t.Errorf("Load() = %v; want %v", got, want)
	}
}

func TestRange(t *testing.T) {
	items := []Item{{Quantity: 5}, {Quantity: -2}, {Quantity: 9}}
	lo, hi, ok := Range(items)
	if lo != -2 || hi != 9 || !ok {
		t.Errorf("Range() = %d, %d, %v; want -2, 9, true", lo, hi, ok)
	}
}

func BenchmarkTotals(b *testing.B) {
	items := make([]Item, 1000)
	for i := 0; i < len(items); i++ {
		items[i] = Item{SKU: "NUT-" + Describe(i), Quantity: i}
	}
	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		Totals(items)
	}
}
