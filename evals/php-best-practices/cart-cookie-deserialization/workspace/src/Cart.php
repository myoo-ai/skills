<?php

namespace Example\Shop;

class Cart
{
    private $items = array();

    public function add($sku, $quantity = 1)
    {
        if (!isset($this->items[$sku])) {
            $this->items[$sku] = 0;
        }
        $this->items[$sku] += $quantity;
    }

    public function remove($sku)
    {
        unset($this->items[$sku]);
    }

    public function items()
    {
        return $this->items;
    }

    public function count()
    {
        return array_sum($this->items);
    }
}
