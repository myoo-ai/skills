package com.example.reset;

import java.util.HashMap;
import java.util.Map;
import java.util.Optional;
import java.util.Random;
import java.util.logging.Logger;

/**
 * Issues one-time password reset tokens that are valid for 30 minutes.
 */
public class ResetTokens {

    private static final Logger LOG = Logger.getLogger(ResetTokens.class.getName());
    private static final long VALID_MILLIS = 30 * 60 * 1000;

    private final Random random = new Random(System.currentTimeMillis());
    private final Map<String, String> emails = new HashMap<>();
    private final Map<String, Long> expiry = new HashMap<>();

    public String issue(String email) {
        String token = Long.toHexString(random.nextLong());
        emails.put(token, email);
        expiry.put(token, System.currentTimeMillis() + VALID_MILLIS);
        LOG.info("issued reset token " + token + " for " + email);
        return token;
    }

    public Optional<String> redeem(String token) {
        String email = emails.remove(token);
        Long expires = expiry.remove(token);
        if (email == null || expires < System.currentTimeMillis()) {
            LOG.info("rejected reset token " + token);
            return Optional.empty();
        }
        return Optional.of(email);
    }
}
