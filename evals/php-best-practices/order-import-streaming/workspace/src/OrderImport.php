<?php

namespace Example\Orders;

class OrderImport
{
    private $skipIds;

    public function __construct($skipIds = array())
    {
        $this->skipIds = $skipIds;
    }

    /**
     * Reads an order export (CSV with a header row containing order_id, email and total).
     */
    public function readOrders($path)
    {
        $lines = file($path);
        $header = str_getcsv(trim(array_shift($lines)), ',', '"', '');
        $idCol = array_search('order_id', $header);
        $emailCol = array_search('email', $header);
        $totalCol = array_search('total', $header);
        if (!$idCol || !$emailCol || !$totalCol) {
            throw new \Exception('missing column in ' . $path);
        }

        $orders = array();
        foreach ($lines as $line) {
            $line = trim($line);
            if ($line == '') {
                continue;
            }
            $row = str_getcsv($line, ',', '"', '');
            if (in_array($row[$idCol], $this->skipIds)) {
                continue;
            }
            $orders[] = array(
                'id' => $row[$idCol],
                'email' => strtolower($row[$emailCol]),
                'total_cents' => (int) round($row[$totalCol] * 100),
            );
        }
        return $orders;
    }
}
