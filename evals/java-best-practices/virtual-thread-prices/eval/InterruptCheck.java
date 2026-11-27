import com.example.prices.*;
import java.math.BigDecimal;
import java.util.List;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.atomic.AtomicReference;
import java.util.stream.IntStream;

public class InterruptCheck {
    public static void main(String[] args) throws Exception {
        AtomicInteger inFlight = new AtomicInteger();
        PriceSource source = sku -> {
            inFlight.incrementAndGet();
            try {
                Thread.sleep(200);
            } finally {
                inFlight.decrementAndGet();
            }
            return BigDecimal.ONE;
        };
        List<String> skus = IntStream.range(0, 60).mapToObj(i -> "sku-" + i).toList();
        AtomicReference<String> outcome = new AtomicReference<>("fetchAll returned normally");
        Thread caller = Thread.ofPlatform().start(() -> {
            try {
                new PriceService(source, 4).fetchAll(skus);
            } catch (PriceLookupException e) {
                outcome.set(Thread.currentThread().isInterrupted()
                        ? "ok" : "PriceLookupException thrown but interrupt flag cleared");
            } catch (RuntimeException e) {
                outcome.set("unexpected " + e);
            }
        });
        Thread.sleep(300);
        caller.interrupt();
        caller.join(1500);
        if (caller.isAlive()) throw new AssertionError("fetchAll still running 1.5 s after interrupt");
        if (!outcome.get().equals("ok")) throw new AssertionError(outcome.get());
        Thread.sleep(300);
        if (inFlight.get() != 0) throw new AssertionError(inFlight.get() + " fetches still running after fetchAll threw");
        System.out.println("ok");
    }
}
