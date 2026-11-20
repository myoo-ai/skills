---
name: javascript-best-practices
description: "Applies current, officially sourced JavaScript (ECMAScript 2026) and Node.js/browser runtime best practices to write, review, and modernize code. Use when the user asks to write, review, refactor, or modernize JavaScript, mentions ECMAScript, ES modules, Node.js, npm, package.json, async/await, or browser DOM scripting, or works with .js, .mjs, or .cjs files."
license: MIT
---

# JavaScript (ECMAScript 2026) best practices

Produces modern, safe, maintainable JavaScript for browsers and Node.js, targeting ECMAScript 2026 (17th edition, June 2026) and Node.js 26 "Lithium", the latest LTS line, while staying compatible with the project's declared baseline (oldest supported LTS: Node.js 22).

## Steps

1. Detect the target runtimes: read `package.json` `engines.node` and `type` (`"module"` or `"commonjs"`), `.nvmrc` / `.node-version`, the browserslist config (`.browserslistrc` or `package.json` `browserslist`), and any bundler/transpiler target.
2. Detect tool configs and conventions: `eslint.config.js` (or legacy `.eslintrc*`), `.prettierrc*` / `prettier.config.js`, `biome.json`, `.editorconfig`, and the lockfile in use (`package-lock.json`, `pnpm-lock.yaml`, `yarn.lock`).
3. Apply the practices below; use version-tagged features only when every target runtime supports them (check MDN Baseline status for browsers and the Node.js version for servers), otherwise keep the compatible form and suggest upgrading.
4. Follow existing project conventions and tool configs when they conflict with a non-safety rule; never relax a security rule for consistency.
5. Run the project's checks: the formatter (`npx prettier --check .` or `npx biome check .`), the linter (`npx eslint .`), type checking if configured (`npx tsc --noEmit` for JSDoc/`checkJs` projects), and the tests (`npm test`, or `node --test`).

## Best practices

### Declarations and style

- Declare with `const` by default and `let` only when reassigning; never use `var`, which is function-scoped and hoisted ([MDN const](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Statements/const)).
- Remember that `const` prevents rebinding, not mutation; use `Object.freeze()` (shallow) when a value must be immutable ([MDN Object.freeze](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Object/freeze)).
- Compare with `===` / `!==`; reserve `== null` only if the project's lint config allows it as the null-or-undefined check ([MDN strict equality](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/Strict_equality)).
- Use `Number.isNaN()` instead of the coercing global `isNaN()` ([MDN Number.isNaN](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Number/isNaN)).
- Write code as modules or with `"use strict"` in classic scripts; module and class bodies are strict automatically ([MDN strict mode](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Strict_mode)).
- Use `?.` for optional access and `??` for defaults so that `0`, `''`, and `false` are preserved, unlike `||` ([MDN optional chaining](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/Optional_chaining), [MDN nullish coalescing](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/Nullish_coalescing)).
- Use `#private` class fields and methods for real encapsulation instead of `_underscore` conventions (ES2022+) ([MDN private elements](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Classes/Private_elements)).
- Use `Object.hasOwn(obj, key)` instead of `obj.hasOwnProperty(key)`; it also works on null-prototype objects (ES2022+) ([MDN Object.hasOwn](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Object/hasOwn)).
- Use `BigInt` for integers beyond `Number.MAX_SAFE_INTEGER` (IDs, 64-bit values); never mix it with `Number` in arithmetic ([MDN BigInt](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/BigInt)).
- Use destructuring and default parameters instead of manual `arguments`/`options.x || default` handling ([MDN destructuring](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/Destructuring), [MDN default parameters](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Functions/Default_parameters)).
- Build strings with template literals instead of `+` concatenation ([MDN template literals](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Template_literals)).
- Iterate arrays and other iterables with `for...of`; reserve `for...in` for object keys, and prefer `Object.entries()` over it ([MDN for...of](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Statements/for...of), [MDN Object.entries](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Object/entries)).

### Modules and packages

- Write ES modules (`import`/`export`) for new code; set `"type": "module"` in `package.json` or use `.mjs` so Node.js treats `.js` as ESM ([Node.js packages](https://nodejs.org/api/packages.html), [MDN modules](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Modules)).
- Import Node.js built-ins with the `node:` prefix (`import fs from 'node:fs/promises'`); some modules such as `node:test` exist only under that scheme ([Node.js ESM](https://nodejs.org/api/esm.html), [Node.js test runner](https://nodejs.org/api/test.html)).
- Use full relative specifiers with file extensions in ESM (`'./util.js'`); Node.js ESM does not resolve extensionless or directory imports ([Node.js ESM](https://nodejs.org/api/esm.html)).
- Define a package's public API with `"exports"` (with `"import"`/`"require"`/`"default"` conditions when needed) so internal files cannot be deep-imported ([Node.js packages](https://nodejs.org/api/packages.html)).
- Use `"imports"` subpath mappings starting with `#` instead of long `../../` chains or bundler-only aliases ([Node.js packages](https://nodejs.org/api/packages.html)).
- Import JSON with import attributes rather than `fs` + `JSON.parse` at startup (ES2025+, Node.js 22.12+) ([MDN import attributes](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Statements/import/with), [Node.js ESM](https://nodejs.org/api/esm.html)).

  ```js
  import config from './config.json' with { type: 'json' };
  ```

- Use `import.meta.dirname` / `import.meta.filename` in ESM instead of reconstructing `__dirname` from `import.meta.url` (Node.js 22.16+/24+) ([Node.js ESM](https://nodejs.org/api/esm.html)).
- When CommonJS code must consume ESM, use `require(esm)` only on targets that support it unflagged (Node.js 20.19+/22.12+); otherwise use dynamic `import()` ([Node.js modules](https://nodejs.org/api/modules.html)).
- Declare supported runtimes in `"engines"` and keep it in sync with CI and `.nvmrc` ([npm package.json](https://docs.npmjs.com/cli/v11/configuring-npm/package-json)).

### Asynchronous code

- Prefer `async`/`await` over `.then()` chains; always `await` or `return` every promise so rejections propagate ([MDN using promises](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Using_promises)).
- Run independent work concurrently with `Promise.all()` instead of sequential `await` in a loop ([MDN Promise.all](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Promise/all)).
- Use `Promise.allSettled()` when every outcome matters and `Promise.any()` for first-success semantics ([MDN Promise.allSettled](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Promise/allSettled), [MDN Promise.any](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Promise/any)).
- Make every network or long-running call cancellable: accept an `AbortSignal`, and use `AbortSignal.timeout()` and `AbortSignal.any()` instead of hand-rolled `setTimeout` races ([MDN AbortSignal.timeout](https://developer.mozilla.org/en-US/docs/Web/API/AbortSignal/timeout_static), [MDN AbortSignal.any](https://developer.mozilla.org/en-US/docs/Web/API/AbortSignal/any_static)).

  ```js
  const res = await fetch(url, {
    signal: AbortSignal.any([callerSignal, AbortSignal.timeout(5_000)]),
  });
  if (!res.ok) throw new Error(`HTTP ${res.status}`, { cause: res });
  ```

- Use `Promise.withResolvers()` instead of capturing `resolve`/`reject` from a constructor closure (ES2024+) ([MDN Promise.withResolvers](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Promise/withResolvers)).
- Use `Promise.try(fn)` to start a promise chain from a function that may throw synchronously or return a value (ES2025+) ([MDN Promise.try](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Promise/try)).
- Use `Array.fromAsync()` to collect an async iterable instead of a manual `for await` push loop (ES2026+) ([MDN Array.fromAsync](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Array/fromAsync)).
- Use top-level `await` only in entry-point modules; it delays every importer of that module ([MDN await](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/await)).
- Keep the Node.js event loop unblocked: avoid sync `fs`/`crypto`/`zlib` calls in request paths, bound the size of `JSON.parse` input, and move CPU-heavy work to worker threads ([Node.js don't block the event loop](https://nodejs.org/en/learn/asynchronous-work/dont-block-the-event-loop)); in browsers use Web Workers ([MDN web workers](https://developer.mozilla.org/en-US/docs/Web/API/Web_Workers_API/Using_web_workers)).
- Treat `'unhandledRejection'` as a crash signal, not a recovery path; fix the missing handler instead of silencing it ([Node.js process](https://nodejs.org/api/process.html)).

### Errors

- Throw only `Error` instances (or subclasses), never strings or plain objects, so stack traces and `instanceof` work ([MDN Error](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Error)).
- Wrap lower-level failures with `new Error(message, { cause })` instead of losing or string-concatenating the original (ES2022+) ([MDN Error cause](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Error/cause), [Node.js errors](https://nodejs.org/api/errors.html)).

  ```js
  try {
    return JSON.parse(text);
  } catch (err) {
    throw new ConfigError(`Invalid config at ${path}`, { cause: err });
  }
  ```

- Subclass `Error` for domain errors, set `this.name`, and add a stable `code` property for programmatic checks rather than matching on `message` ([MDN Error](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Error), [Node.js errors](https://nodejs.org/api/errors.html)).
- Catch only where you can handle, add context, or translate the error; never swallow with an empty `catch` ([MDN using promises](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Using_promises)).
- Use `Error.isError(value)` for cross-realm error checks where supported (ES2026+, Node.js 24+; not yet Baseline in browsers) ([MDN Error.isError](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Error/isError)).

### Resource management

- Release resources with `try...finally` (or `await using` where supported) so files, handles, and locks close on every path ([MDN await using](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Statements/await_using)).
- Use `using` / `await using` with objects that implement `[Symbol.dispose]()` / `[Symbol.asyncDispose]()`; it is TC39 stage 4 (ES2027) and shipped in Node.js 24+, but not yet in all browsers, so gate it on targets ([MDN using](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Statements/using), [TC39 finished proposals](https://github.com/tc39/proposals/blob/main/finished-proposals.md), [Node.js 24 release](https://nodejs.org/en/blog/release/v24.0.0)).

  ```js
  import { open } from 'node:fs/promises';
  await using file = await open(path, 'r');
  const text = await file.readFile('utf8');
  // file is closed when the block exits, even on throw
  ```

- Aggregate several disposables with `DisposableStack` / `AsyncDisposableStack` instead of nested `try...finally` (same gating as `using`) ([MDN DisposableStack](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/DisposableStack)).
- Use `WeakMap` for per-object metadata so entries do not keep their keys alive ([MDN WeakMap](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/WeakMap)).

### Collections and data

- Use non-mutating array methods `toSorted()`, `toReversed()`, `toSpliced()`, and `with()` instead of copying then mutating (ES2023+) ([MDN toSorted](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Array/toSorted), [MDN toReversed](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Array/toReversed), [MDN toSpliced](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Array/toSpliced), [MDN with](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Array/with)).
- Use `at(-1)` for end-relative indexing and `findLast()` / `findLastIndex()` instead of reversing (ES2022+/ES2023+) ([MDN at](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Array/at), [MDN findLast](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Array/findLast)).
- Group with `Object.groupBy()` (string keys) or `Map.groupBy()` (any keys) instead of hand-written `reduce` (ES2024+) ([MDN Object.groupBy](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Object/groupBy), [MDN Map.groupBy](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Map/groupBy)).
- Use `Map` for dynamic keys and `Set` for membership instead of plain objects and arrays ([MDN Map](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Map)); use `union()`, `intersection()`, `difference()`, `isSubsetOf()` instead of manual loops (ES2025+) ([MDN Set.union](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Set/union), [MDN Set.intersection](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Set/intersection)).
- Use `map.getOrInsert(key, value)` / `getOrInsertComputed(key, fn)` instead of `has` + `set` + `get` (ES2026+) ([MDN Map.getOrInsert](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Map/getOrInsert)).

  ```js
  const byTag = new Map();
  for (const post of posts) {
    for (const tag of post.tags) byTag.getOrInsertComputed(tag, () => []).push(post);
  }
  ```

- Process large or lazy sequences with iterator helpers (`map`, `filter`, `take`, `drop`, `flatMap`, `toArray`) instead of materializing intermediate arrays (ES2025+) ([MDN Iterator](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Iterator), [MDN Iterator.map](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Iterator/map)); chain sources with `Iterator.concat()` (ES2026+) ([MDN Iterator.concat](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Iterator/concat)).

  ```js
  const firstTen = Iterator.from(readLines())
    .filter((line) => line.trim() !== '')
    .take(10)
    .toArray();
  ```

- Deep-copy with `structuredClone()` instead of `JSON.parse(JSON.stringify(x))`, which drops `Date`, `Map`, `Set`, and `undefined` ([MDN structuredClone](https://developer.mozilla.org/en-US/docs/Web/API/Window/structuredClone), [Node.js globals](https://nodejs.org/api/globals.html)).
- Sum floating-point values with `Math.sumPrecise()` when intermediate rounding matters (ES2026+) ([MDN Math.sumPrecise](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Math/sumPrecise)).
- Encode binary data with `Uint8Array.prototype.toBase64()` / `Uint8Array.fromBase64()` instead of `btoa`/`atob` string tricks (ES2026+) ([MDN toBase64](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Uint8Array/toBase64), [MDN fromBase64](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Uint8Array/fromBase64)).
- Use `Float16Array` only for half-precision interchange (GPU, ML buffers), not general math (ES2025+) ([MDN Float16Array](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Float16Array)).

### Strings, dates, and regular expressions

- Build regexes from user input with `RegExp.escape()` instead of ad-hoc replace patterns (ES2025+) ([MDN RegExp.escape](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/RegExp/escape)).
- Avoid regexes with nested or overlapping quantifiers on untrusted input; they can backtrack exponentially (ReDoS) and block the event loop ([Node.js don't block the event loop](https://nodejs.org/en/learn/asynchronous-work/dont-block-the-event-loop)).
- Format dates, numbers, and lists with `Intl` APIs instead of manual string assembly ([MDN Intl](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Intl), [MDN Intl.DateTimeFormat](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Intl/DateTimeFormat)).
- Prefer `Temporal` over `Date` for time zones, calendar arithmetic, and durations where targets support it; it is TC39 stage 4 (ES2027), enabled by default in Node.js 26+, and not yet in all browsers ([MDN Temporal](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Temporal), [Node.js 26 release](https://nodejs.org/en/blog/release/v26.0.0), [TC39 finished proposals](https://github.com/tc39/proposals/blob/main/finished-proposals.md)).

  ```js
  const due = Temporal.Now.plainDateISO('Europe/Amsterdam').add({ days: 30 });
  ```

- When `Date` is required, store and transmit instants as ISO 8601 UTC strings or epoch milliseconds ([MDN Date](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Date)).

### Security

- Never pass untrusted strings to `eval()`, `new Function()`, or string-form `setTimeout`/`setInterval`; they are injection sinks ([MDN eval](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/eval), [OWASP Node.js](https://cheatsheetseries.owasp.org/cheatsheets/Nodejs_Security_Cheat_Sheet.html)).
- Render untrusted data with `textContent`, `setAttribute` on safe attributes, or DOM construction; never with `innerHTML`, `outerHTML`, `insertAdjacentHTML`, or `document.write` ([MDN innerHTML](https://developer.mozilla.org/en-US/docs/Web/API/Element/innerHTML), [MDN textContent](https://developer.mozilla.org/en-US/docs/Web/API/Node/textContent), [OWASP DOM XSS](https://cheatsheetseries.owasp.org/cheatsheets/DOM_based_XSS_Prevention_Cheat_Sheet.html)).
- Enforce sink safety in browsers with a Content Security Policy and `require-trusted-types-for 'script'` (Trusted Types: Baseline 2026) ([MDN Trusted Types](https://developer.mozilla.org/en-US/docs/Web/API/Trusted_Types_API), [MDN CSP](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/CSP)).
- Prevent prototype pollution: store untrusted keys in `Map`/`Set` or `Object.create(null)` objects, and never deep-merge parsed JSON into ordinary objects without rejecting `__proto__`, `constructor`, and `prototype` ([OWASP prototype pollution](https://cheatsheetseries.owasp.org/cheatsheets/Prototype_Pollution_Prevention_Cheat_Sheet.html), [MDN prototype pollution](https://developer.mozilla.org/en-US/docs/Web/Security/Attacks/Prototype_pollution), [MDN Object.create](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Object/create)).
- Generate tokens and IDs with `crypto.randomUUID()` / `crypto.getRandomValues()`, never `Math.random()` ([MDN randomUUID](https://developer.mozilla.org/en-US/docs/Web/API/Crypto/randomUUID), [MDN getRandomValues](https://developer.mozilla.org/en-US/docs/Web/API/Crypto/getRandomValues)).
- Spawn processes with `execFile`/`spawn` and an argument array; never interpolate user input into `exec` or a `shell: true` command string ([Node.js child_process](https://nodejs.org/api/child_process.html), [OWASP Node.js](https://cheatsheetseries.owasp.org/cheatsheets/Nodejs_Security_Cheat_Sheet.html)).
- Restrict what a Node.js process can touch with the Permission Model (`--permission`, `--allow-fs-read`, `--allow-fs-write`, `--allow-child-process`) for scripts and tools handling untrusted input (Node.js 22.13+) ([Node.js permissions](https://nodejs.org/api/permissions.html)).
- Load third-party scripts with Subresource Integrity (`integrity` + `crossorigin`) when served from a CDN ([MDN SRI](https://developer.mozilla.org/en-US/docs/Web/Security/Subresource_Integrity)).
- Read secrets from the environment, never from source; for local development use `node --env-file=.env` or `process.loadEnvFile()` instead of a dotenv dependency (Node.js 22.21+/24.10+ stable) ([Node.js CLI](https://nodejs.org/api/cli.html), [Node.js process](https://nodejs.org/api/process.html), [Node.js env vars](https://nodejs.org/en/learn/command-line/how-to-read-environment-variables-from-nodejs)).

### Dependencies

- Commit the lockfile and install in CI with `npm ci`, which fails if `package.json` and the lockfile disagree ([npm ci](https://docs.npmjs.com/cli/v11/commands/npm-ci), [npm package-lock.json](https://docs.npmjs.com/cli/v11/configuring-npm/package-lock-json)).
- Run `npm audit` in CI with an `--audit-level` threshold, and `npm audit signatures` to verify registry signatures and provenance ([npm audit](https://docs.npmjs.com/cli/v11/commands/npm-audit)).
- Disable install scripts (`--ignore-scripts` or `ignore-scripts=true` in `.npmrc`) unless a dependency genuinely needs them; review lockfile diffs for unexpected sources ([Node.js security best practices](https://nodejs.org/en/learn/getting-started/security-best-practices), [OWASP NPM](https://cheatsheetseries.owasp.org/cheatsheets/NPM_Security_Cheat_Sheet.html)).
- Prefer platform built-ins (`fetch`, `structuredClone`, `node:test`, `--env-file`, `--watch`, `AbortSignal.timeout`) over adding packages for the same job ([Node.js globals](https://nodejs.org/api/globals.html), [Node.js fetch](https://nodejs.org/en/learn/getting-started/fetch)).
- Publish packages with `npm publish --provenance` from CI so consumers can verify their origin ([npm provenance](https://docs.npmjs.com/generating-provenance-statements)).

### Node.js runtime and tooling

- Use the global `fetch` (stable since Node.js 21) and check `res.ok` before reading the body; it does not reject on HTTP errors ([Node.js globals](https://nodejs.org/api/globals.html), [Node.js fetch](https://nodejs.org/en/learn/getting-started/fetch)).
- Use `node --watch` for local development restarts instead of nodemon (stable since Node.js 22) ([Node.js CLI](https://nodejs.org/api/cli.html)).
- Use promise-based APIs (`node:fs/promises`, `node:timers/promises`, `events.once`, `stream/promises` `pipeline`) instead of callbacks or `util.promisify` wrappers ([Node.js fs](https://nodejs.org/api/fs.html), [Node.js timers](https://nodejs.org/api/timers.html), [Node.js events](https://nodejs.org/api/events.html), [Node.js stream](https://nodejs.org/api/stream.html)).
- Compose streams with `pipeline()` so errors and cleanup propagate; never chain `.pipe()` without error handling ([Node.js stream](https://nodejs.org/api/stream.html)).
- Check `node --pending-deprecation` output and the deprecations list before upgrading majors; replace runtime-deprecated APIs ([Node.js deprecations](https://nodejs.org/api/deprecations.html)).
- Set `process.exitCode` and let the event loop drain instead of calling `process.exit()`, which can truncate pending I/O such as stdout writes ([Node.js process](https://nodejs.org/api/process.html)).

### Browser and DOM

- Load browser code with `<script type="module">` so it gets module scope, strict mode, and `import`/`export` ([MDN modules](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Modules)); map bare specifiers with `<script type="importmap">` instead of rewriting import paths ([MDN importmap](https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/script/type/importmap)).
- Check `response.ok` after `fetch()`; it rejects only on network failure, not on HTTP 4xx/5xx ([MDN fetch](https://developer.mozilla.org/en-US/docs/Web/API/Window/fetch), [MDN Response.ok](https://developer.mozilla.org/en-US/docs/Web/API/Response/ok)).
- Pass `{ signal }` to `addEventListener()` and abort one controller to remove a group of listeners on teardown, instead of tracking handler references ([MDN addEventListener](https://developer.mozilla.org/en-US/docs/Web/API/EventTarget/addEventListener)).

  ```js
  const controller = new AbortController();
  window.addEventListener('resize', onResize, { signal: controller.signal });
  button.addEventListener('click', onClick, { signal: controller.signal });
  // on unmount:
  controller.abort();
  ```

- Move CPU-heavy work (parsing, image processing, crypto) off the main thread into a Web Worker ([MDN web workers](https://developer.mozilla.org/en-US/docs/Web/API/Web_Workers_API/Using_web_workers)).

### Testing

- Use the built-in `node:test` runner with `node:assert/strict` for libraries and services that do not already use another runner (stable since Node.js 20) ([Node.js test runner](https://nodejs.org/api/test.html), [Node.js learn: test runner](https://nodejs.org/en/learn/test-runner/using-test-runner)).

  ```js
  import { test } from 'node:test';
  import assert from 'node:assert/strict';
  import { slugify } from '../src/slugify.js';

  test('slugify lowercases and joins words', () => {
    assert.equal(slugify('Hello World'), 'hello-world');
  });
  ```

- Run tests with `node --test`; name files `*.test.js` (or another default pattern) so discovery works without config ([Node.js test runner](https://nodejs.org/api/test.html)).
- Use `mock.fn()`, `mock.method()`, and `mock.timers` from `node:test` instead of hand-patching globals ([Node.js test runner](https://nodejs.org/api/test.html)).
- Await every async assertion (`await assert.rejects(...)`) so failures are not reported after the test ends ([Node.js test runner](https://nodejs.org/api/test.html)).

## Examples

Input: "Add a function that fetches a user profile and fails after 3 seconds."
Output: An `async` function taking an optional `signal`, calling `fetch` with `AbortSignal.any([signal, AbortSignal.timeout(3_000)])`, checking `res.ok`, and throwing `new Error(..., { cause })` on failure; plus a `node:test` test using `mock.method(globalThis, 'fetch', ...)`. Rules applied: cancellable async, Error `cause`, built-in fetch and test runner.

Input: "Review this Express handler that merges `req.body` into the default settings object and renders `settings.title` with `innerHTML`."
Output: Review flagging prototype pollution (recommend a `Map` or `Object.create(null)` plus rejecting `__proto__`/`constructor`/`prototype` keys), XSS via `innerHTML` (use `textContent`), and suggesting Trusted Types/CSP; each finding cites the OWASP and MDN rules.

Input: "Modernize this CommonJS utility for Node.js 26."
Output: Converted to ESM with `"type": "module"`, `node:` imports, `.js` extensions on relative specifiers, `"exports"` in `package.json`, `toSorted()`/`Object.groupBy()` replacing mutate-and-reduce code, `engines.node` set to `">=22"` only if 22 must stay supported (otherwise `">=26"`), and `node --test` added to `npm test`.

## Edge cases

- Older targets (browserslist includes pre-2024 browsers, or `engines.node` below 22): avoid version-tagged features above the target, or rely on the project's existing transpiler/polyfill setup; never add a polyfill dependency without asking.
- Limited-availability features (`using`/`await using`, `DisposableStack`, `Temporal`, `Error.isError`, ES2026 additions in browsers): use them in Node.js code whose `engines` guarantees support; in browser code gate behind feature detection or keep the older form.
- Stage 3 proposals and experimental runtime flags (for example Import Defer, Source Phase Imports, `Iterator.zip`, the HTML Sanitizer API `setHTML()`, `--frozen-intrinsics`, `--experimental-test-coverage` as a gate): do not use in production code; mention only as optional, explicitly labelled experimental.
- CommonJS project (`"type": "commonjs"` or no `type` with `require` everywhere): keep CommonJS for consistency unless asked to migrate; still use `node:` prefixes, `const`, and modern built-ins.
- Conflicting conventions (Prettier/Biome/ESLint configs, a different test runner such as Jest or Vitest): follow the project's tools and style; only security and correctness rules override them.
- Generated or vendored code (`dist/`, `build/`, minified files, `node_modules/`, codegen output): do not hand-edit or reformat; change the source or generator instead.
- TypeScript or framework projects (React, Vue, Angular, Svelte, Next.js): framework and TypeScript conventions take precedence; apply only the language-level rules here that do not conflict.
- Node.js type stripping (`.ts` files run directly, stable in Node.js 24.12+/25.2+): it performs no type checking and refuses files under `node_modules`, so still run `tsc` and publish JavaScript.
- Monorepos and workspaces: detect the workspace tool (npm/pnpm/Yarn workspaces) and run checks per package from the root lockfile; never create a second lockfile.
- Browser scripts without a bundler: use `<script type="module">` and full URLs/relative paths with extensions; bare specifiers need an import map.
- Other runtimes (Deno, Bun, Cloudflare Workers, edge functions): keep the language-level rules, but replace Node.js-specific APIs, flags, and `package.json` fields with that runtime's documented equivalents.
- Node.js 22 (oldest supported LTS) still required: check each Node-gated rule's minimum minor version (for example `--env-file` stable only from 22.21) and pin `engines.node` accordingly.

## Resources

- [MDN JavaScript reference](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference): read when checking syntax, semantics, or Baseline browser availability of a built-in.
- [MDN Baseline compatibility](https://developer.mozilla.org/en-US/docs/Glossary/Baseline/Compatibility): read when deciding whether a feature is safe for the project's browser targets.
- [ECMAScript 2026 specification](https://tc39.es/ecma262/2026/): read when exact language semantics matter.
- [TC39 finished proposals](https://github.com/tc39/proposals/blob/main/finished-proposals.md): read when checking whether a feature is stage 4 and which edition includes it.
- [Node.js releases](https://nodejs.org/en/about/previous-releases): read when choosing `engines.node` or checking LTS status.
- [Node.js packages](https://nodejs.org/api/packages.html) and [Node.js ESM](https://nodejs.org/api/esm.html): read when configuring `type`, `exports`, `imports`, or module interop.
- [Node.js test runner](https://nodejs.org/api/test.html): read when writing or running tests with `node:test`.
- [Node.js security best practices](https://nodejs.org/en/learn/getting-started/security-best-practices): read when hardening a Node.js service or its supply chain.
- [OWASP Node.js Security Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Nodejs_Security_Cheat_Sheet.html): read when reviewing server-side code for injection and DoS risks.
- [OWASP DOM based XSS Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/DOM_based_XSS_Prevention_Cheat_Sheet.html): read when code writes untrusted data into the DOM.
- [npm CLI documentation](https://docs.npmjs.com/cli/v11): read when configuring installs, audits, or publishing.
