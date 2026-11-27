<?php

require __DIR__ . '/../src/OrderImport.php';

use Example\Orders\OrderImport;

$import = new OrderImport(array('0100', 'TEST-1'));
$count = 0;
$cents = 0;
foreach ($import->readOrders($argv[1]) as $order) {
    $count++;
    $cents += $order['total_cents'];
}
printf("%d orders, %.2f total\n", $count, $cents / 100);
