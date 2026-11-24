---
description: "Python code follows the python-best-practices skill. Load it before changing .py or pyproject.toml files."
globs: ["**/*.py", "**/pyproject.toml"]
paths: ["**/*.py", "**/pyproject.toml"]
applyTo: "**/*.py,**/pyproject.toml"
alwaysApply: false
# omp: remind once per session, right after the first edit of a matching file
condition: ["**/*.py", "**/pyproject.toml"]
interruptMode: never
repeatMode: once
---

# Python best practices

- Load the `python-best-practices` skill before writing or changing Python code, and follow it
- If Python code was already changed without it, load it now and re-check those changes against it
