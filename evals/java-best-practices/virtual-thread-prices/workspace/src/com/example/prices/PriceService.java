package com.example.prices;

import java.io.IOException;
import java.util.ArrayList;
import java.util.List;
import java.util.Objects;

public final class PriceService {

    private final PriceSource source;

    public PriceService(PriceSource source) {
        this.source = Objects.requireNonNull(source, "source");
    }

    public List<Price> fetchAll(List<String> skus) throws PriceLookupException {
        List<Price> prices = new ArrayList<>();
        for (String sku : skus) {
            try {
                prices.add(new Price(sku, source.fetch(sku)));
            } catch (IOException e) {
                throw new PriceLookupException("price lookup failed for " + sku, e);
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                throw new PriceLookupException("interrupted while fetching " + sku, e);
            }
        }
        return prices;
    }
}
