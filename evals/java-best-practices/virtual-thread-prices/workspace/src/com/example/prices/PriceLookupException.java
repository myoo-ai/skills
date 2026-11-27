package com.example.prices;

public class PriceLookupException extends Exception {

    private static final long serialVersionUID = 1L;

    public PriceLookupException(String message, Throwable cause) {
        super(message, cause);
    }
}
