---
description: "PHP code follows the php-best-practices skill. Load it before changing .php or composer.json files."
globs: ["**/*.php", "**/composer.json"]
paths: ["**/*.php", "**/composer.json"]
applyTo: "**/*.php,**/composer.json"
alwaysApply: false
# omp: remind once per session, right after the first edit of a matching file
condition: ["**/*.php", "**/composer.json"]
interruptMode: never
repeatMode: once
---

# PHP best practices

- Load the `php-best-practices` skill before writing or changing PHP code, and follow it
- If PHP code was already changed without it, load it now and re-check those changes against it
