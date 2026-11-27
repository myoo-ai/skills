import com.example.invoices.*;
import com.sun.management.UnixOperatingSystemMXBean;
import java.io.IOException;
import java.lang.management.ManagementFactory;
import java.nio.file.Files;
import java.nio.file.Path;
import java.time.DateTimeException;
import java.time.LocalDate;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;

public class InvoiceCheck {
    static void check(boolean ok, String msg) {
        if (!ok) throw new AssertionError(msg);
    }

    static Exception failure(Path file) {
        try {
            InvoiceParser.parse(file);
        } catch (Exception e) {
            return e;
        }
        throw new AssertionError("no exception for " + file.getFileName());
    }

    static void rejects(Path dir, String name, String content, String line, Class<?> cause) throws IOException {
        Path file = Files.writeString(dir.resolve(name), content);
        Exception e = failure(file);
        check(e.getClass().getSimpleName().equals("InvoiceParseException"),
                name + ": expected InvoiceParseException, got " + e);
        check(!(e instanceof RuntimeException), name + ": InvoiceParseException is a checked exception");
        String msg = String.valueOf(e.getMessage());
        check(msg.contains(name) && msg.matches("(?s).*\\b" + line + "\\b.*"),
                name + ": message names the file and line " + line + ", got: " + msg);
        if (cause != null) {
            check(cause.isInstance(e.getCause()), name + ": cause is a " + cause.getSimpleName() + ", got " + e.getCause());
        }
    }

    static long openFiles() {
        return ((UnixOperatingSystemMXBean) ManagementFactory.getOperatingSystemMXBean()).getOpenFileDescriptorCount();
    }

    public static void main(String[] args) throws Exception {
        Path dir = Files.createTempDirectory("invoices");

        Path good = Files.writeString(dir.resolve("good.txt"),
                "# ACME\nINV-1;2026-11-02;125000\n\nINV-2;2024-02-29;4999\n  \nINV-3;2026-11-30;730\n");
        List<Invoice> invoices = InvoiceParser.parse(good);
        check(invoices.size() == 3, "3 invoices, got " + invoices.size());
        check(invoices.get(1).number().equals("INV-2"), "number()");
        check(invoices.get(1).issued().equals(LocalDate.of(2024, 2, 29)), "issued() is the LocalDate");
        check(invoices.get(0).amountCents() == 125000L, "amountCents()");

        rejects(dir, "feb30.txt", "INV-1;2026-11-02;100\n# x\nINV-2;2026-02-30;100\n", "3", DateTimeException.class);
        rejects(dir, "month13.txt", "INV-1;2026-13-01;100\n", "1", DateTimeException.class);
        rejects(dir, "amount.txt", "INV-1;2026-11-02;100\n\nINV-2;2026-11-03;12,50\n", "3", NumberFormatException.class);
        rejects(dir, "fields.txt", "INV-1;2026-11-02;100\nINV-2;2026-11-03\n", "2", null);

        Exception missing = failure(dir.resolve("missing.txt"));
        check(missing instanceof IOException, "missing file throws IOException, got " + missing);

        // files are closed, on success and on failure
        Path bad = dir.resolve("feb30.txt");
        long baseline = openFiles();
        for (int i = 0; i < 50; i++) {
            InvoiceParser.parse(good);
            failure(bad);
            long now = openFiles();
            check(now <= baseline + 3, "open files grew from " + baseline + " to " + now + " after " + (i + 1) + " rounds");
        }

        // safe to call from many threads
        StringBuilder big = new StringBuilder();
        List<LocalDate> want = new ArrayList<>();
        LocalDate day = LocalDate.of(2020, 1, 1);
        for (int i = 0; i < 400; i++) {
            day = day.plusDays(37);
            want.add(day);
            big.append("INV-").append(i).append(';').append(day).append(';').append(i).append('\n');
        }
        Path many = Files.writeString(dir.resolve("many.txt"), big);
        try (ExecutorService pool = Executors.newFixedThreadPool(16)) {
            List<Future<List<Invoice>>> results = new ArrayList<>();
            for (int i = 0; i < 64; i++) {
                results.add(pool.submit(() -> InvoiceParser.parse(many)));
            }
            for (Future<List<Invoice>> result : results) {
                check(result.get().stream().map(Invoice::issued).toList().equals(want), "parallel parse gave wrong dates");
            }
        }
        System.out.println("ok");
    }
}
