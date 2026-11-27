<?php
declare(strict_types=1);
set_error_handler(static function (int $no, string $msg, string $file, int $line): never {
    throw new ErrorException($msg, 0, $no, $file, $line);
});
require getcwd() . '/src/OrderImport.php';
use Example\Orders\OrderImport;
function check(bool $ok, string $what): void {
    if (!$ok) { fwrite(STDERR, "FAIL: $what\n"); exit(1); }
}
$dir = sys_get_temp_dir() . '/orders-' . bin2hex(random_bytes(4));
mkdir($dir);
register_shutdown_function(static function () use ($dir): void {
    array_map(unlink(...), glob("$dir/*"));
    rmdir($dir);
});

// order_id in the first column, ids that only differ in leading zeros or notation
file_put_contents("$dir/new.csv", implode("\n", [
    'order_id,total,email,shop',
    '0100,1.00,test@example.com,nl',
    '100,12.50,Ann@Example.com,nl',
    '1e2,3.00,cem@example.com,de',
    'TEST-1,9.99,qa@example.com,de',
    '00100,4.25,JÖRG@Example.com,de',
    '',
]));
$import = new OrderImport(['0100', 'TEST-1']);
$orders = [];
foreach ($import->readOrders("$dir/new.csv") as $order) {
    $orders[] = $order;
}
check(array_column($orders, 'id') === ['100', '1e2', '00100'], 'only the listed ids are skipped, got ' . json_encode(array_column($orders, 'id')));
check(array_column($orders, 'total_cents') === [1250, 300, 425], 'totals in cents');
check(array_column($orders, 'email') === ['ann@example.com', 'cem@example.com', 'jörg@example.com'], 'emails lowercased, including non-ASCII, got ' . json_encode(array_column($orders, 'email'), JSON_UNESCAPED_UNICODE));

// the old column order still works
file_put_contents("$dir/old.csv", "shop,order_id,email,total\nnl,0099,Ann@Example.com,12.50\nnl,0100,test@example.com,1.00\n");
$orders = [];
foreach ((new OrderImport(['0100']))->readOrders("$dir/old.csv") as $order) {
    $orders[] = $order;
}
check($orders === [['id' => '0099', 'email' => 'ann@example.com', 'total_cents' => 1250]], 'old column order');

// a missing column or a missing file throws an exception, without a PHP warning
file_put_contents("$dir/bad.csv", "order_id,email\n1,a@example.com\n");
foreach (['missing column' => "$dir/bad.csv", 'missing file' => "$dir/nope.csv"] as $what => $path) {
    $thrown = false;
    try {
        foreach ((new OrderImport())->readOrders($path) as $_) {}
    } catch (ErrorException $e) {
        check(false, "$what: PHP warning instead of an exception: " . $e->getMessage());
    } catch (Exception) {
        $thrown = true;
    }
    check($thrown, "$what throws an exception");
}

// memory stays flat for a large export
$big = fopen("$dir/big.csv", 'w');
fwrite($big, "shop,order_id,email,total\n");
for ($i = 0; $i < 300_000; $i++) {
    fwrite($big, sprintf("nl,%07d,customer%d@example.com,%d.%02d\n", $i, $i, $i % 500, $i % 100));
}
fclose($big);
gc_collect_cycles();
memory_reset_peak_usage();
$before = memory_get_usage();
$count = 0;
$cents = 0;
$result = (new OrderImport(['0000007']))->readOrders("$dir/big.csv");
check(!is_array($result), 'readOrders does not build the whole array');
foreach ($result as $order) {
    $count++;
    $cents += $order['total_cents'];
}
$grown = memory_get_peak_usage() - $before;
check($count === 299_999, "big export row count, got $count");
check($grown < 2 * 1024 * 1024, sprintf('memory grew by %.1f MB while importing a %.1f MB file', $grown / 1048576, filesize("$dir/big.csv") / 1048576));
echo "ok\n";
