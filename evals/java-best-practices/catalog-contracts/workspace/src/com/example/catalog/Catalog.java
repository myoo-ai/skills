package com.example.catalog;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.SortedSet;
import java.util.TreeSet;

public class Catalog {

    private final List<Product> products = new ArrayList<>();

    public void add(Product product) {
        products.add(product);
    }

    public List<Product> getProducts() {
        return products;
    }

    public Product find(String sku) {
        for (Product product : products) {
            if (product.getSku().equals(sku)) {
                return product;
            }
        }
        return null;
    }

    public List<Product> sortedByPrice() {
        List<Product> sorted = new ArrayList<>(products);
        Collections.sort(sorted);
        return sorted;
    }

    public SortedSet<Product> priceList() {
        return new TreeSet<>(products);
    }
}
