package com.example.prices;

import java.io.IOException;
import java.math.BigDecimal;

@FunctionalInterface
public interface PriceSource {

    BigDecimal fetch(String sku) throws IOException, InterruptedException;
}
