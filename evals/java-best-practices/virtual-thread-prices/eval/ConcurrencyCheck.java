import com.example.prices.*;
import java.io.IOException;
import java.math.BigDecimal;
import java.util.List;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.stream.IntStream;

public class ConcurrencyCheck {
    static void check(boolean ok, String msg) {
        if (!ok) throw new AssertionError(msg);
    }

    public static void main(String[] args) throws Exception {
        AtomicInteger inFlight = new AtomicInteger();
        AtomicInteger peak = new AtomicInteger();
        AtomicInteger platform = new AtomicInteger();
        PriceSource source = sku -> {
            if (!Thread.currentThread().isVirtual()) platform.incrementAndGet();
            peak.accumulateAndGet(inFlight.incrementAndGet(), Math::max);
            try {
                Thread.sleep(200);
            } finally {
                inFlight.decrementAndGet();
            }
            if (sku.equals("bad")) throw new IOException("supplier down");
            return new BigDecimal(sku.substring(4));
        };
        List<String> skus = IntStream.range(0, 20).mapToObj(i -> "sku-" + i).toList();

        long start = System.nanoTime();
        List<Price> prices = new PriceService(source, 4).fetchAll(skus);
        long millis = (System.nanoTime() - start) / 1_000_000;
        check(prices.stream().map(Price::sku).toList().equals(skus), "results in input order");
        check(prices.get(7).amount().equals(new BigDecimal(7)), "amount of sku-7");
        check(peak.get() <= 4, "at most 4 calls in flight, saw " + peak.get());
        check(peak.get() >= 2, "calls run concurrently, peak was " + peak.get());
        check(millis < 2500, "20 calls of 200 ms with limit 4 took " + millis + " ms");
        check(platform.get() == 0, platform.get() + " calls ran on platform threads");

        peak.set(0);
        check(new PriceService(source).fetchAll(skus).size() == 20, "one-arg constructor");
        check(peak.get() <= 8, "default limit is 8, saw " + peak.get());
        check(new PriceService(source, 2).fetchAll(List.of()).isEmpty(), "empty input");
        for (int bad : new int[] {0, -1}) {
            try {
                new PriceService(source, bad);
                throw new AssertionError("limit " + bad + " accepted");
            } catch (IllegalArgumentException expected) {
                // rejected, as required
            }
        }

        try {
            new PriceService(source, 4).fetchAll(List.of("sku-1", "bad", "sku-2"));
            throw new AssertionError("failure not reported");
        } catch (PriceLookupException e) {
            check(e.getCause() instanceof IOException && "supplier down".equals(e.getCause().getMessage()),
                    "cause is the supplier's IOException, got " + e.getCause());
        }
        System.out.println("ok");
    }
}
