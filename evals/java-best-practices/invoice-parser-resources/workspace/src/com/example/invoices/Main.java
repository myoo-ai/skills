package com.example.invoices;

import java.nio.file.Path;
import java.util.List;

public final class Main {

    private Main() {
    }

    public static void main(String[] args) {
        long total = 0;
        int count = 0;
        for (String arg : args) {
            List<Invoice> invoices = InvoiceParser.parse(Path.of(arg));
            for (Invoice invoice : invoices) {
                total += invoice.getAmountCents();
                count++;
            }
        }
        System.out.printf("%d invoices, %d.%02d EUR%n", count, total / 100, total % 100);
    }
}
