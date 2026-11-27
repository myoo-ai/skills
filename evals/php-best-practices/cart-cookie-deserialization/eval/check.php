<?php
declare(strict_types=1);
set_error_handler(static function (int $no, string $msg, string $file, int $line): never {
    throw new ErrorException($msg, 0, $no, $file, $line);
});
foreach (glob(getcwd() . '/src/*.php') as $file) {
    require_once $file;
}
use Example\Shop\{Cart, CartCookie, InvalidCartCookie};
function check(bool $ok, string $what): void {
    if (!$ok) { fwrite(STDERR, "FAIL: $what\n"); exit(1); }
}
final class Gadget
{
    public static bool $fired = false;
    public string $cmd = 'touch /tmp/pwned';
    public function __wakeup(): void { self::$fired = true; }
    public function __unserialize(array $data): void { self::$fired = true; }
    public function __destruct() { if ($this->cmd === 'from-cookie') { self::$fired = true; } }
}
function rejects(mixed $value, string $what): void {
    try {
        CartCookie::decode($value);
    } catch (InvalidCartCookie) {
        return;
    } catch (Throwable $e) {
        check(false, "$what: threw " . $e::class . ' instead of InvalidCartCookie');
    }
    check(false, "$what: accepted");
}
check(class_exists(InvalidCartCookie::class) && is_a(InvalidCartCookie::class, Throwable::class, true), 'InvalidCartCookie exception exists');

$cart = new Cart();
$cart->add('MUG-01', 2);
$cart->add('TOTE-4');
$cart->add('MUG-01', 1);
check($cart->items() === ['MUG-01' => 3, 'TOTE-4' => 1] && $cart->count() === 4, 'cart behaviour unchanged');
$cookie = CartCookie::encode($cart);
check(is_string($cookie) && $cookie !== '' && preg_match('/^[\x21-\x7e]+$/', $cookie) === 1 && !preg_match('/[",;\\\\]/', $cookie), 'cookie value is safe in a Set-Cookie header');
$back = CartCookie::decode($cookie);
check($back instanceof Cart && $back->items() === ['MUG-01' => 3, 'TOTE-4' => 1], 'round trip keeps the items');
check(CartCookie::decode(CartCookie::encode(new Cart()))->items() === [], 'empty cart round trip');

// object injection
$gadget = new Gadget();
$gadget->cmd = 'from-cookie';
$payloads = [
    'serialized gadget' => base64_encode(serialize($gadget)),
    'raw serialized gadget' => serialize($gadget),
    'gadget inside an array' => base64_encode(serialize(['MUG-01' => $gadget])),
    'legacy serialized cart' => base64_encode(serialize($cart)),
];
$gadget->cmd = 'harmless';
foreach ($payloads as $what => $payload) {
    rejects($payload, $what);
    gc_collect_cycles();
    check(!Gadget::$fired, "$what: the cookie created an object of an arbitrary class");
}

// malformed or out-of-range content
$json = static fn (mixed $v): array => [base64_encode(json_encode($v)), rtrim(strtr(base64_encode(json_encode($v)), '+/', '-_'), '='), rawurlencode(json_encode($v))];
$bad = [
    'garbage' => ['%%%not a cookie%%%'],
    'empty string' => [''],
    'truncated json' => [base64_encode('{"MUG-01":'), rawurlencode('{"MUG-01":')],
    'list instead of map' => $json([1, 2]),
    'negative quantity' => $json(['MUG-01' => -1]),
    'zero quantity' => $json(['MUG-01' => 0]),
    'huge quantity' => $json(['MUG-01' => 100]),
    'string quantity' => $json(['MUG-01' => '2']),
    'float quantity' => $json(['MUG-01' => 1.5]),
    'markup in sku' => $json(['<script>' => 1]),
    'lowercase sku' => $json(['mug-01' => 1]),
    'nested object' => $json(['MUG-01' => ['qty' => 1]]),
];
foreach ($bad as $what => $values) {
    foreach ($values as $value) {
        rejects($value, $what);
    }
}

foreach ([['<b>', 1], ['MUG-01', 0], ['MUG-01', -3], ['MUG-01', 100]] as [$sku, $qty]) {
    $thrown = false;
    try { (new Cart())->add($sku, $qty); } catch (InvalidArgumentException) { $thrown = true; }
    check($thrown, "Cart::add('$sku', $qty) rejected with InvalidArgumentException");
}
echo "ok\n";
