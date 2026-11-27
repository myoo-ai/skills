<?php
declare(strict_types=1);
set_error_handler(static function (int $no, string $msg, string $file, int $line): never {
    throw new ErrorException($msg, 0, $no, $file, $line);
});
require getcwd() . '/src/UserStore.php';
use Example\Accounts\UserStore;
function check(bool $ok, string $what): void {
    if (!$ok) { fwrite(STDERR, "FAIL: $what\n"); exit(1); }
}
function hashOf(PDO $pdo, string $email): string {
    $stmt = $pdo->prepare('SELECT password_hash FROM users WHERE email = ?');
    $stmt->execute([$email]);
    return (string) $stmt->fetchColumn();
}
$pdo = new PDO('sqlite::memory:');
UserStore::createSchema($pdo);
$store = new UserStore($pdo);
$store->register('ann@example.com', 'Ann Example', 'correct horse');
$store->register('liam@example.com', "Liam O'Brien", 'battery staple');
$hash = hashOf($pdo, 'ann@example.com');
check(password_get_info($hash)['algo'] !== null && password_verify('correct horse', $hash), 'register stores a password_hash() hash');
check(($store->login('ann@example.com', 'correct horse')['email'] ?? null) === 'ann@example.com', 'login with the right password');
check($store->login('ann@example.com', 'wrong') === null, 'wrong password rejected');
check($store->login("' OR '1'='1' --", 'x') === null, 'injection in email rejected');
check($store->login("ann@example.com' --", 'x') === null, 'comment injection rejected');
$found = $store->search("O'Brien");
check(count($found) === 1 && $found[0]['email'] === 'liam@example.com', "search for O'Brien");
check($store->search("' OR '1'='1") === [], 'injection in search returns nothing');
$legacy = md5('hunter2');
$pdo->prepare('INSERT INTO users (email, name, password_hash) VALUES (?, ?, ?)')->execute(['old@example.com', 'Old Timer', $legacy]);
check($store->login('old@example.com', $legacy) === null, 'the md5 string itself is not a password');
check(($store->login('old@example.com', 'hunter2')['email'] ?? null) === 'old@example.com', 'legacy md5 login works');
$upgraded = hashOf($pdo, 'old@example.com');
check($upgraded !== $legacy && password_verify('hunter2', $upgraded) && !password_needs_rehash($upgraded, PASSWORD_DEFAULT), 'legacy hash upgraded');
check($store->login('old@example.com', 'hunter2') !== null, 'login after upgrade');
$weak = password_hash('tr0ub4dor', PASSWORD_BCRYPT, ['cost' => 4]);
$pdo->prepare('INSERT INTO users (email, name, password_hash) VALUES (?, ?, ?)')->execute(['weak@example.com', 'Weak Hash', $weak]);
check($store->login('weak@example.com', 'tr0ub4dor') !== null, 'login with an outdated hash');
$rehashed = hashOf($pdo, 'weak@example.com');
check($rehashed !== $weak && password_verify('tr0ub4dor', $rehashed) && !password_needs_rehash($rehashed, PASSWORD_DEFAULT), 'outdated hash rehashed');
echo "ok\n";
