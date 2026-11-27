package com.example.invoices;

import java.io.BufferedReader;
import java.io.FileReader;
import java.nio.file.Path;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.List;

/**
 * Parses supplier invoice files with one invoice per line as {@code number;yyyy-MM-dd;amountCents}.
 * Blank lines and lines starting with {@code #} are ignored.
 */
public class InvoiceParser {

    private static final SimpleDateFormat DATE = new SimpleDateFormat("yyyy-MM-dd");

    public static List<Invoice> parse(Path file) {
        List<Invoice> invoices = new ArrayList<>();
        try {
            BufferedReader reader = new BufferedReader(new FileReader(file.toFile()));
            String line;
            while ((line = reader.readLine()) != null) {
                if (line.isBlank() || line.startsWith("#")) {
                    continue;
                }
                String[] parts = line.split(";");
                invoices.add(new Invoice(parts[0], DATE.parse(parts[1]), Long.parseLong(parts[2])));
            }
            reader.close();
        } catch (Exception e) {
            e.printStackTrace();
            return new ArrayList<>();
        }
        return invoices;
    }
}
