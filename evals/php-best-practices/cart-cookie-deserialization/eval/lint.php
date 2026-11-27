<?php
declare(strict_types=1);
// php lint.php at <dir>... fails on the @ operator, php lint.php empty-catch <dir>... on empty catch blocks.
$mode = $argv[1] ?? '';
if (!in_array($mode, ['at', 'empty-catch'], true)) {
    fwrite(STDERR, "usage: php lint.php at|empty-catch <dir>...\n");
    exit(2);
}
$found = 0;
foreach (array_slice($argv, 2) as $dir) {
    $files = new RecursiveIteratorIterator(new RecursiveDirectoryIterator($dir, FilesystemIterator::SKIP_DOTS));
    foreach ($files as $file) {
        if ($file->getExtension() !== 'php') {
            continue;
        }
        $tokens = array_values(array_filter(
            token_get_all((string) file_get_contents($file->getPathname())),
            static fn ($t): bool => !is_array($t) || !in_array($t[0], [T_WHITESPACE, T_COMMENT, T_DOC_COMMENT], true),
        ));
        foreach ($tokens as $i => $token) {
            if ($mode === 'at' && $token === '@') {
                fwrite(STDERR, "@ operator in {$file->getPathname()}\n");
                $found++;
            }
            if ($mode === 'empty-catch' && is_array($token) && $token[0] === T_CATCH) {
                for ($j = $i + 1; $j < count($tokens) && $tokens[$j] !== '{'; $j++);
                if (($tokens[$j + 1] ?? null) === '}') {
                    fwrite(STDERR, "empty catch in {$file->getPathname()} line {$token[2]}\n");
                    $found++;
                }
            }
        }
    }
}
exit($found === 0 ? 0 : 1);
