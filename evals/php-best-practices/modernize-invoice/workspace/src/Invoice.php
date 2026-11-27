<?php

namespace Example\Billing;

class Invoice implements \JsonSerializable
{
    const STATUS_DRAFT = 'draft';
    const STATUS_SENT = 'sent';
    const STATUS_PAID = 'paid';
    const STATUS_VOID = 'void';

    private $number;
    private $customerEmail;
    private $status;
    private $lines = array();

    public function __construct($number, $customerEmail, $status = self::STATUS_DRAFT)
    {
        $this->number = $number;
        $this->customerEmail = $customerEmail;
        $this->setStatus($status);
    }

    public static function fromArray($row)
    {
        $invoice = new Invoice(
            $row['number'],
            $row['customer_email'],
            isset($row['status']) ? $row['status'] : self::STATUS_DRAFT
        );
        foreach ($row['lines'] as $line) {
            $invoice->addLine(new LineItem(
                $line['sku'],
                $line['description'],
                $line['unit_price_cents'],
                isset($line['quantity']) ? $line['quantity'] : 1
            ));
        }
        return $invoice;
    }

    public function addLine(LineItem $line)
    {
        $this->lines[] = $line;
    }

    public function getNumber()
    {
        return $this->number;
    }

    public function getCustomerEmail()
    {
        return $this->customerEmail;
    }

    public function getLines()
    {
        return $this->lines;
    }

    public function getStatus()
    {
        return $this->status;
    }

    public function setStatus($status)
    {
        $known = array(self::STATUS_DRAFT, self::STATUS_SENT, self::STATUS_PAID, self::STATUS_VOID);
        if (!in_array($status, $known)) {
            throw new \InvalidArgumentException('Unknown invoice status ' . $status);
        }
        $this->status = $status;
    }

    public function statusLabel()
    {
        switch ($this->status) {
            case self::STATUS_DRAFT:
                return 'Draft';
            case self::STATUS_SENT:
                return 'Sent';
            case self::STATUS_PAID:
                return 'Paid';
            case self::STATUS_VOID:
                return 'Void';
        }
        return 'Unknown';
    }

    public function isPayable()
    {
        return $this->status == self::STATUS_SENT;
    }

    public function totalCents()
    {
        return array_sum(array_map(array($this, 'lineTotal'), $this->lines));
    }

    private function lineTotal($line)
    {
        return $line->totalCents();
    }

    public function jsonSerialize()
    {
        return array(
            'number' => $this->number,
            'customer_email' => $this->customerEmail,
            'status' => $this->status,
            'total_cents' => $this->totalCents(),
            'lines' => array_map(function ($line) {
                return array(
                    'sku' => $line->getSku(),
                    'quantity' => $line->getQuantity(),
                    'total_cents' => $line->totalCents(),
                );
            }, $this->lines),
        );
    }
}
