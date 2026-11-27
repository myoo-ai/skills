<?php
declare(strict_types=1);
set_error_handler(static function (int $no, string $msg, string $file, int $line): never {
    throw new ErrorException($msg, 0, $no, $file, $line);
});
require getcwd() . '/src/autoload.php';
use Example\Billing\{Invoice, InvoiceStatus, LineItem};
function check(bool $ok, string $what): void {
    if (!$ok) { fwrite(STDERR, "FAIL: $what\n"); exit(1); }
}
check(enum_exists(InvoiceStatus::class), 'InvoiceStatus is an enum');
check((string) new ReflectionEnum(InvoiceStatus::class)->getBackingType() === 'string', 'InvoiceStatus is string-backed');
$values = array_map(fn ($c) => $c->value, InvoiceStatus::cases());
sort($values);
check($values === ['draft', 'paid', 'sent', 'void'], 'enum values');
check(InvoiceStatus::from('paid')->label() === 'Paid', 'enum label');
$inv = Invoice::fromArray(['number' => 'INV-1', 'customer_email' => 'cem@example.com', 'status' => 'sent', 'lines' => [
    ['sku' => 'MUG-01', 'description' => 'Mug', 'unit_price_cents' => 1250, 'quantity' => 2],
    ['sku' => 'PEN-05', 'description' => 'Pen', 'unit_price_cents' => 299],
]]);
check($inv->getStatus() === InvoiceStatus::from('sent'), 'getStatus returns the enum');
check($inv->isPayable() && $inv->statusLabel() === 'Sent', 'sent invoice is payable');
check($inv->totalCents() === 2799, 'total');
$inv->setStatus(InvoiceStatus::from('paid'));
check(!$inv->isPayable() && $inv->statusLabel() === 'Paid', 'paid invoice');
$draft = new Invoice('INV-2', 'dee@example.com');
check($draft->getStatus() === InvoiceStatus::from('draft'), 'default status is draft');
$thrown = false;
try { Invoice::fromArray(['number' => 'X', 'customer_email' => 'x@example.com', 'status' => 'bogus', 'lines' => []]); } catch (Throwable) { $thrown = true; }
check($thrown, 'unknown status throws');
$item = new LineItem('CAP-03', 'Cap', 899);
check($item->sku === 'CAP-03' && $item->description === 'Cap' && $item->unitPriceCents === 899 && $item->quantity === 1, 'public line item properties');
$p = new ReflectionProperty(LineItem::class, 'quantity');
check($p->isPublic() && $p->isReadOnly() && $p->isPromoted(), 'quantity is promoted public readonly');
$thrown = false;
try { $item->quantity = 5; } catch (Error) { $thrown = true; }
check($thrown && $item->quantity === 1, 'line item is immutable');
$thrown = false;
try { new LineItem('CAP-03', 'Cap', 899, 0); } catch (InvalidArgumentException) { $thrown = true; }
check($thrown, 'quantity below 1 rejected');
check(json_encode($inv) === '{"number":"INV-1","customer_email":"cem@example.com","status":"paid","total_cents":2799,"lines":[{"sku":"MUG-01","quantity":2,"total_cents":2500},{"sku":"PEN-05","quantity":1,"total_cents":299}]}', 'json shape unchanged');
echo "ok\n";
