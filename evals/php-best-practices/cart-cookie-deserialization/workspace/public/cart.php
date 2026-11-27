<?php

require __DIR__ . '/../src/CartCookie.php';

use Example\Shop\CartCookie;

$cart = CartCookie::decode(isset($_COOKIE[CartCookie::NAME]) ? $_COOKIE[CartCookie::NAME] : '');

if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['sku'])) {
    $cart->add($_POST['sku'], (int) $_POST['quantity']);
    setcookie(CartCookie::NAME, CartCookie::encode($cart), array('path' => '/', 'samesite' => 'Lax'));
}

echo 'Items in cart: ' . $cart->count() . "\n";
