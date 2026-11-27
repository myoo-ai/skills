package com.example.prices;

import java.math.BigDecimal;
import java.util.Objects;

public record Price(String sku, BigDecimal amount) {

    public Price {
        Objects.requireNonNull(sku, "sku");
        Objects.requireNonNull(amount, "amount");
    }
}
