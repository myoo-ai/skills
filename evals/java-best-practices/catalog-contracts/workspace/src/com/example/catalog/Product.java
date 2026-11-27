package com.example.catalog;

public class Product implements Comparable<Product> {

    private String sku;
    private String name;
    private long priceCents;

    public Product(String sku, String name, long priceCents) {
        this.sku = sku;
        this.name = name;
        this.priceCents = priceCents;
    }

    public String getSku() {
        return sku;
    }

    public String getName() {
        return name;
    }

    public long getPriceCents() {
        return priceCents;
    }

    public void setPriceCents(long priceCents) {
        this.priceCents = priceCents;
    }

    @Override
    public boolean equals(Object o) {
        if (!(o instanceof Product)) {
            return false;
        }
        Product other = (Product) o;
        return sku.equals(other.sku) && name.equals(other.name) && priceCents == other.priceCents;
    }

    @Override
    public int compareTo(Product other) {
        return (int) (priceCents - other.priceCents);
    }

    @Override
    public String toString() {
        return sku + " " + name + " " + priceCents;
    }
}
