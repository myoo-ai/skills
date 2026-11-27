<?php

require __DIR__ . '/../src/UserStore.php';

use Example\Accounts\UserStore;

$pdo = new PDO('sqlite::memory:');
UserStore::createSchema($pdo);
$store = new UserStore($pdo);

$store->register('ann@example.com', 'Ann Example', 'correct horse');
$store->register('bob@example.com', 'Bob Sample', 'battery staple');

foreach ($store->search('a') as $user) {
    echo $user['id'] . ' ' . $user['email'] . ' ' . $user['name'] . "\n";
}
