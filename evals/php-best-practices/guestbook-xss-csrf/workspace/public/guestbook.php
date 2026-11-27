<?php

require __DIR__ . '/../src/CommentBoard.php';

use Example\Guestbook\CommentBoard;

session_start();

$board = new CommentBoard(isset($_SESSION['comments']) ? $_SESSION['comments'] : array());

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    if ($board->handlePost($_SESSION, $_POST)) {
        $_SESSION['comments'] = $board->comments();
    }
    header('Location: /guestbook');
    exit;
}

echo "<h1>Guestbook</h1>\n";
echo $board->renderList();
echo $board->renderForm($_SESSION);
