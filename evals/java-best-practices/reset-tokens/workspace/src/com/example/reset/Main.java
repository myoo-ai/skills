package com.example.reset;

public final class Main {

    private Main() {
    }

    public static void main(String[] args) {
        ResetTokens tokens = new ResetTokens();
        String token = tokens.issue("ann@example.com");
        System.out.println("reset link: https://shop.example/reset?token=" + token);
        System.out.println("first use: " + tokens.redeem(token).orElse("rejected"));
        System.out.println("second use: " + tokens.redeem(token).orElse("rejected"));
    }
}
