package com.example.catalog;

import java.util.HashSet;
import java.util.List;
import java.util.Set;

public final class Main {

    private Main() {
    }

    public static void main(String[] args) {
        List<Product> feed = List.of(
                new Product("MUG-01", "Enamel mug", 1250),
                new Product("TOTE-4", "Canvas tote", 1250),
                new Product("GIFT-X", "Gift card", 5_000_000_000L),
                new Product("MUG-01", "Enamel mug", 1250),
                new Product("PEN-05", "Pen", 299));
        Set<Product> unique = new HashSet<>(feed);
        Catalog catalog = new Catalog();
        for (Product product : unique) {
            catalog.add(product);
        }
        System.out.println("products: " + catalog.getProducts().size());
        for (Product product : catalog.priceList()) {
            System.out.println(product);
        }
        Product mug = catalog.find("MUG-01");
        System.out.println("mug: " + mug.getName());
    }
}
