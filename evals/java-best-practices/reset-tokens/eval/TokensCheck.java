import com.example.reset.ResetTokens;
import java.io.ByteArrayOutputStream;
import java.io.PrintStream;
import java.time.Clock;
import java.time.Duration;
import java.time.Instant;
import java.time.ZoneId;
import java.time.ZoneOffset;
import java.util.HashSet;
import java.util.Set;
import java.util.logging.Handler;
import java.util.logging.Level;
import java.util.logging.LogRecord;
import java.util.logging.Logger;
import java.util.logging.SimpleFormatter;

public class TokensCheck {
    static void check(boolean ok, String msg) {
        if (!ok) throw new AssertionError(msg);
    }

    static final class TestClock extends Clock {
        Instant now = Instant.parse("2026-11-27T10:00:00Z");

        @Override
        public ZoneId getZone() {
            return ZoneOffset.UTC;
        }

        @Override
        public Clock withZone(ZoneId zone) {
            return this;
        }

        @Override
        public Instant instant() {
            return now;
        }
    }

    public static void main(String[] args) throws Exception {
        // capture everything that is logged or printed
        StringBuilder logged = new StringBuilder();
        SimpleFormatter formatter = new SimpleFormatter();
        Logger root = Logger.getLogger("");
        root.setLevel(Level.ALL);
        root.addHandler(new Handler() {
            @Override
            public void publish(LogRecord r) {
                synchronized (logged) {
                    logged.append(formatter.formatMessage(r)).append(' ').append(r.getMessage()).append('\n');
                    if (r.getThrown() != null) logged.append(r.getThrown()).append('\n');
                }
            }

            @Override
            public void flush() {
            }

            @Override
            public void close() {
            }
        });
        PrintStream out = System.out;
        ByteArrayOutputStream printed = new ByteArrayOutputStream();
        PrintStream capture = new PrintStream(printed, true);
        System.setOut(capture);
        System.setErr(capture);

        Set<String> issued = new HashSet<>();
        String email = "ann@example.com";
        try {
            TestClock clock = new TestClock();
            ResetTokens tokens = new ResetTokens(clock);
            String first = tokens.issue(email);
            issued.add(first);
            clock.now = clock.now.plus(Duration.ofMinutes(29).plusSeconds(59));
            check(tokens.redeem(first).orElse("").equals(email), "token valid after 29:59");
            check(tokens.redeem(first).isEmpty(), "token works only once");

            String late = tokens.issue(email);
            issued.add(late);
            clock.now = clock.now.plus(Duration.ofMinutes(30).plusSeconds(1));
            check(tokens.redeem(late).isEmpty(), "token rejected after 30:01");
            check(tokens.redeem("not-a-token").isEmpty(), "unknown token rejected");

            ResetTokens system = new ResetTokens();
            String now = system.issue(email);
            check(system.redeem(now).orElse("").equals(email), "no-arg constructor uses the system clock");
            issued.add(now);

            for (int i = 0; i < 2000; i++) {
                String t = system.issue("user" + i + "@example.com");
                check(t.matches("[A-Za-z0-9_-]{22,}"), "token is URL-safe with at least 128 bits: " + t);
                check(issued.add(t), "duplicate token " + t);
            }
        } finally {
            System.setOut(out);
            System.setErr(out);
        }

        String all = logged + printed.toString();
        if (args.length > 0 && args[0].equals("--email")) {
            check(!all.contains("@example.com"), "email addresses show up in the logs");
            System.out.println("ok");
            return;
        }
        for (String t : issued) {
            check(!all.contains(t), "token " + t + " shows up in the logs");
        }
        System.out.println("ok");
    }
}
