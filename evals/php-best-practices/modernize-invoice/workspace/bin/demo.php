<?php

require __DIR__ . '/../src/autoload.php';

use Example\Billing\Invoice;

$invoice = Invoice::fromArray(array(
    'number' => 'INV-2026-0042',
    'customer_email' => 'ann@example.com',
    'status' => 'sent',
    'lines' => array(
        array('sku' => 'MUG-01', 'description' => 'Enamel mug', 'unit_price_cents' => 1250, 'quantity' => 2),
        array('sku' => 'BAG-04', 'description' => 'Canvas tote', 'unit_price_cents' => 3450),
    ),
));

echo $invoice->getNumber() . ' for ' . $invoice->getCustomerEmail() . "\n";
echo 'Status: ' . $invoice->statusLabel() . ($invoice->isPayable() ? ' (payable)' : '') . "\n";
foreach ($invoice->getLines() as $line) {
    printf("  %-8s %-12s %d x %s\n", $line->getSku(), $line->getDescription(), $line->getQuantity(), number_format($line->getUnitPriceCents() / 100, 2));
}
echo 'Total: ' . number_format($invoice->totalCents() / 100, 2) . "\n";
echo json_encode($invoice) . "\n";
