<?php

namespace Example\Shop;

require_once __DIR__ . '/Cart.php';

class CartCookie
{
    const NAME = 'cart';

    public static function encode(Cart $cart)
    {
        return base64_encode(serialize($cart));
    }

    public static function decode($value)
    {
        $cart = @unserialize(base64_decode($value));
        if (!$cart) {
            return new Cart();
        }
        return $cart;
    }
}
