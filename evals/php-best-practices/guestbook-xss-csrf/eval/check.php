<?php
declare(strict_types=1);
set_error_handler(static function (int $no, string $msg, string $file, int $line): never {
    throw new ErrorException($msg, 0, $no, $file, $line);
});
require getcwd() . '/src/CommentBoard.php';
use Example\Guestbook\CommentBoard;
function check(bool $ok, string $what): void {
    if (!$ok) { fwrite(STDERR, "FAIL: $what\n"); exit(1); }
}
/** @return array<string, string> the hidden fields of the form */
function hiddenFields(string $form): array {
    $doc = new DOMDocument();
    $doc->loadHTML('<!doctype html><html><body>' . $form . '</body></html>', LIBXML_NOERROR);
    $fields = [];
    foreach ($doc->getElementsByTagName('input') as $input) {
        if (strtolower($input->getAttribute('type')) === 'hidden' && $input->getAttribute('name') !== '') {
            $fields[$input->getAttribute('name')] = $input->getAttribute('value');
        }
    }
    return $fields;
}
$comment = ['author' => 'Ann', 'body' => 'Lovely shop!', 'website' => ''];

// stored comments from before the fix are escaped on output
$board = new CommentBoard([
    ['author' => '<b>"Eve\'</b>', 'body' => '<script>alert(1)</script> & <img src=x onerror=alert(2)>', 'website' => "https://example.com/'onmouseover='alert(3)"],
    ['author' => 'Bob', 'body' => 'Tom & Jerry', 'website' => ''],
]);
$html = $board->renderList();
check(!str_contains($html, '<script') && !str_contains($html, '<img') && !str_contains($html, '<b>'), 'markup in author or body is escaped');
check(str_contains($html, '&lt;script&gt;alert(1)&lt;/script&gt;'), 'body text still shown, escaped');
check(!str_contains($html, "'onmouseover="), 'website cannot break out of the href attribute');
check(!str_contains($html, '"Eve'), 'double quote in author escaped');
check(str_contains($html, 'Tom &amp; Jerry'), 'ampersand escaped');

// the form carries a per-session token that handlePost requires
$session = [];
$form = $board->renderForm($session);
$fields = hiddenFields($form);
check($fields !== [], 'form has a hidden token field');
foreach ($fields as $value) {
    check(strlen($value) >= 22, 'token is long enough to be unguessable');
}
check($session !== [], 'token is kept in the session');
check(hiddenFields($board->renderForm($session)) === $fields, 'token stays stable within a session');
$other = [];
$otherFields = hiddenFields($board->renderForm($other));
check($otherFields !== $fields, 'each session gets its own token');

$board = new CommentBoard();
check($board->handlePost($session, $comment) === false, 'post without token rejected');
check($board->handlePost($session, $comment + array_map(fn (string $v): string => '', $fields)) === false, 'post with empty token rejected');
check($board->handlePost($session, $comment + array_map(fn (string $v): string => strrev($v) . 'x', $fields)) === false, 'post with wrong token rejected');
check($board->handlePost($session, $comment + $otherFields) === false, "another session's token rejected");
$empty = [];
check($board->handlePost($empty, $comment) === false, 'post into a session without token rejected');
check($board->handlePost($empty, $comment + array_map(fn (string $v): string => '', $fields)) === false, 'empty token into a session without token rejected');
check($board->comments() === [], 'rejected posts add nothing');
check($board->handlePost($session, $comment + $fields) === true, 'post with the form token accepted');
check(count($board->comments()) === 1, 'accepted post stored');

// only http(s) websites
check($board->handlePost($session, ['website' => 'javascript:alert(document.cookie)'] + $comment + $fields) === false, 'javascript: website rejected');
check($board->handlePost($session, ['website' => 'data:text/html,<script>alert(1)</script>'] + $comment + $fields) === false, 'data: website rejected');
check($board->handlePost($session, ['website' => 'https://ann.example/shop?a=1&b=2'] + $comment + $fields) === true, 'https website accepted');
check(count($board->comments()) === 2, 'only valid posts stored');
$html = $board->renderList();
check(!str_contains($html, 'javascript:') && !str_contains($html, 'data:'), 'no script URLs rendered');
check(str_contains($html, 'https://ann.example/shop?a=1&amp;b=2'), 'website link rendered, escaped');
echo "ok\n";
