<?php

namespace Example\Billing;

class LineItem
{
    private $sku;
    private $description;
    private $unitPriceCents;
    private $quantity;

    public function __construct($sku, $description, $unitPriceCents, $quantity = 1)
    {
        if ($quantity < 1) {
            throw new \InvalidArgumentException('Quantity must be at least 1, got ' . $quantity);
        }
        $this->sku = $sku;
        $this->description = $description;
        $this->unitPriceCents = $unitPriceCents;
        $this->quantity = $quantity;
    }

    public function getSku()
    {
        return $this->sku;
    }

    public function getDescription()
    {
        return $this->description;
    }

    public function getUnitPriceCents()
    {
        return $this->unitPriceCents;
    }

    public function getQuantity()
    {
        return $this->quantity;
    }

    public function totalCents()
    {
        return $this->unitPriceCents * $this->quantity;
    }
}
