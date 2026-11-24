---
description: "Go code follows the go-best-practices skill. Load it before changing .go or go.mod files."
globs: ["**/*.go", "**/go.mod"]
paths: ["**/*.go", "**/go.mod"]
applyTo: "**/*.go,**/go.mod"
alwaysApply: false
# omp: remind once per session, right after the first edit of a matching file
condition: ["**/*.go", "**/go.mod"]
interruptMode: never
repeatMode: once
---

# Go best practices

- Load the `go-best-practices` skill before writing or changing Go code, and follow it
- If Go code was already changed without it, load it now and re-check those changes against it
