package com.example.prices;

import java.math.BigDecimal;
import java.util.List;
import java.util.stream.IntStream;

public final class Main {

    private Main() {
    }

    public static void main(String[] args) throws PriceLookupException {
        PriceSource supplier = sku -> {
            Thread.sleep(100);
            return new BigDecimal(sku.substring(sku.indexOf('-') + 1)).movePointLeft(2);
        };
        List<String> skus = IntStream.rangeClosed(1, 40).mapToObj(i -> "SKU-" + (1000 + i)).toList();

        long start = System.nanoTime();
        List<Price> prices = new PriceService(supplier).fetchAll(skus);
        long millis = (System.nanoTime() - start) / 1_000_000;

        System.out.println("fetched " + prices.size() + " prices in " + millis + " ms");
        System.out.println("first: " + prices.getFirst() + ", last: " + prices.getLast());
    }
}
