---
description: "C# code follows the csharp-best-practices skill. Load it before changing .cs or .csproj files."
globs: ["**/*.cs", "**/*.csproj"]
paths: ["**/*.cs", "**/*.csproj"]
applyTo: "**/*.cs,**/*.csproj"
alwaysApply: false
# omp: remind once per session, right after the first edit of a matching file
condition: ["**/*.cs", "**/*.csproj"]
interruptMode: never
repeatMode: once
---

# C# best practices

- Load the `csharp-best-practices` skill before writing or changing C# code, and follow it
- If C# code was already changed without it, load it now and re-check those changes against it
