---
description: "JavaScript and TypeScript code follows the javascript-best-practices skill. Load it before changing JavaScript, TypeScript, Vue or package.json files."
globs: ["**/*.js", "**/*.mjs", "**/*.cjs", "**/*.jsx", "**/*.ts", "**/*.mts", "**/*.cts", "**/*.tsx", "**/*.vue", "**/package.json"]
paths: ["**/*.js", "**/*.mjs", "**/*.cjs", "**/*.jsx", "**/*.ts", "**/*.mts", "**/*.cts", "**/*.tsx", "**/*.vue", "**/package.json"]
applyTo: "**/*.js,**/*.mjs,**/*.cjs,**/*.jsx,**/*.ts,**/*.mts,**/*.cts,**/*.tsx,**/*.vue,**/package.json"
alwaysApply: false
# omp: remind once per session, right after the first edit of a matching file
condition: ["**/*.js", "**/*.mjs", "**/*.cjs", "**/*.jsx", "**/*.ts", "**/*.mts", "**/*.cts", "**/*.tsx", "**/*.vue", "**/package.json"]
interruptMode: never
repeatMode: once
---

# JavaScript and TypeScript best practices

- Load the `javascript-best-practices` skill before writing or changing JavaScript and TypeScript code, and follow it
- If JavaScript and TypeScript code was already changed without it, load it now and re-check those changes against it
