---
name: go-best-practices
description: "Applies current, officially sourced Go 1.27 best practices to write, review, and modernize Go code across style, errors, concurrency, generics, iterators, testing, modules, security, and performance. Use when the user asks to write, refactor, review, or upgrade Go code, mentions go.mod, gofmt, go vet, go fix, goroutines, generics, or govulncheck, or works with .go files or Go modules."
license: MIT
---

# Go 1.27 best practices

Produces idiomatic, safe, and maintainable Go that targets the module's declared Go version, using Go 1.27 (latest stable, released 2026-08-19) idioms when allowed. Go supports each major release until two newer ones ship, so Go 1.26 is the oldest supported release and the sensible baseline for libraries.

## Steps

1. Detect the target: read the `go` and `toolchain` lines in `go.mod` (and `go.work` if present), any `//go:build go1.N` constraints, `godebug` lines, and the Go version pinned in CI, `Dockerfile`, or `.tool-versions`.
2. Detect project tooling: `.golangci.yml`/`.golangci.yaml`/`.golangci.toml`, `tool` directives in `go.mod`, and `Makefile`/`Taskfile.yml`/`magefile.go` targets for fmt, lint, test, and generate.
3. Apply the practices below; use version-tagged features only when the `go` line is at least that version, otherwise write compatible code and optionally suggest raising the `go` line.
4. Follow existing project conventions and linter configs when they conflict with a non-safety rule; never relax security, error-handling, or race-safety rules for consistency.
5. Run `gofmt -l .` (or `goimports`), `go vet ./...`, the project linter (for example `golangci-lint run`), `go test -race ./...`, and `govulncheck ./...`; prefer the project's Makefile/task targets when they exist.
6. After a toolchain upgrade, run `go fix -diff ./...`, review, then `go fix ./...` and `go mod tidy`.

## Best practices

### Formatting, naming, and docs

- Format every file with `gofmt`; never hand-align or argue style it decides ([Effective Go](https://go.dev/doc/effective_go#formatting)).
- Group imports: standard library first, then a blank line, then third-party; let `goimports` manage them ([CodeReviewComments](https://go.dev/wiki/CodeReviewComments#imports)).
- Put blank imports (`import _ "pkg"`) only in `main` packages or tests; never use dot imports outside the circular-test case ([CodeReviewComments](https://go.dev/wiki/CodeReviewComments#import-blank), [CodeReviewComments](https://go.dev/wiki/CodeReviewComments#import-dot)).
- Use `MixedCaps`/`mixedCaps`, never underscores; keep initialisms uniform case (`URL`, `ID`, `userID`, `ServeHTTP`) ([CodeReviewComments](https://go.dev/wiki/CodeReviewComments#initialisms)).
- Name packages short, lowercase, single-word, and not `util`, `common`, or `helper`; avoid stutter (`http.Server`, not `http.HTTPServer`) ([Effective Go](https://go.dev/doc/effective_go#package-names), [Google style](https://google.github.io/styleguide/go/decisions#package-names), [Google style](https://google.github.io/styleguide/go/decisions#repetition)).
- Use one- or two-letter receiver names derived from the type (`c` for `Client`), consistent across methods; never `this` or `self` ([CodeReviewComments](https://go.dev/wiki/CodeReviewComments#receiver-names)).
- Name getters `Owner()`, not `GetOwner()`; name one-method interfaces with `-er` (`Reader`) ([Effective Go](https://go.dev/doc/effective_go#Getters), [Effective Go](https://go.dev/doc/effective_go#interface-names)).
- Keep local names short in proportion to scope (`i`, `r`, `buf`); give exported and long-lived names descriptive names ([CodeReviewComments](https://go.dev/wiki/CodeReviewComments#variable-names)).
- Start doc comments on every exported identifier with its name as a full sentence; put the package comment in one file as `// Package foo ...` ([Go Doc Comments](https://go.dev/doc/comment)).
- Use doc-comment syntax for links (`[io.Reader]`), lists, and code blocks; mark deprecations with a `Deprecated:` paragraph ([Go Doc Comments](https://go.dev/doc/comment)).
- Use `//go:fix inline` on deprecated wrapper functions so callers can migrate with `go fix` (1.26+) ([go fix inliner](https://go.dev/blog/inliner)).

### Control flow and data

- Handle errors first and return early; keep the happy path unindented and drop `else` after a returning `if` ([CodeReviewComments](https://go.dev/wiki/CodeReviewComments#indent-error-flow)).
- Declare empty slices as `var s []T` (nil); use `[]T{}` only when the distinction matters, such as JSON `[]` vs `null` ([CodeReviewComments](https://go.dev/wiki/CodeReviewComments#declaring-empty-slices)).
- Preallocate with `make([]T, 0, n)` when the final size is known; use `append` and never index past `len` ([Effective Go](https://go.dev/doc/effective_go#allocation_make)).
- Use `for i := range n` to count and rely on per-iteration loop variables; drop `v := v` copies (1.22+) ([Go 1.22](https://go.dev/doc/go1.22)).
- Use the `min`, `max`, and `clear` built-ins and the `slices`/`maps` packages instead of hand-written loops (1.21+) ([Go 1.21](https://go.dev/doc/go1.21)).
- Use `new(expr)` to get a pointer to a computed value, for optional pointer fields (1.26+) ([Go 1.26](https://go.dev/doc/go1.26)).

```go
p := Person{Name: name, Age: new(yearsSince(born))} // Age is *int
```

- Use `strings.Cut`/`strings.CutLast` (and `bytes` equivalents) instead of `Index`/`LastIndex` plus slicing (`CutLast` 1.27+) ([Go 1.27](https://go.dev/doc/go1.27)).
- Avoid naked returns in anything but tiny functions; use named results only to document same-typed results or for a deferred modification ([CodeReviewComments](https://go.dev/wiki/CodeReviewComments#named-result-parameters)).
- Do not copy a value of type `T` whose methods are on `*T` (for example `bytes.Buffer`); the copy may alias internal state ([CodeReviewComments](https://go.dev/wiki/CodeReviewComments#copying)).

### Errors

- Return `error` as the last result and check it immediately; never discard it with `_` unless documented as impossible ([CodeReviewComments](https://go.dev/wiki/CodeReviewComments#handle-errors)).
- Write error strings lowercase without trailing punctuation; they are composed into longer messages ([CodeReviewComments](https://go.dev/wiki/CodeReviewComments#error-strings)).
- Add context that the callee did not already include, and place `%w` at the end: `fmt.Errorf("load config: %w", err)` ([Google style](https://google.github.io/styleguide/go/best-practices#placement-of-w-in-errors)).
- Wrap with `%w` only when callers should inspect the cause; use `%v` to hide implementation details ([Go blog](https://go.dev/blog/go1.13-errors)).
- Compare with `errors.Is`, never `==` or string matching; export sentinel errors as `var ErrX = errors.New("...")` ([errors](https://pkg.go.dev/errors)).
- Return an extra `ok bool` or `error` instead of in-band sentinel values such as `-1` or `""` ([CodeReviewComments](https://go.dev/wiki/CodeReviewComments#in-band-errors)).
- Extract typed errors with `errors.AsType` instead of `errors.As` plus a target variable (1.26+) ([Go 1.26](https://go.dev/doc/go1.26)).

```go
if pe, ok := errors.AsType[*fs.PathError](err); ok {
	log.Printf("failed path: %s", pe.Path)
}
```

- Wrap error values, not pointers to them, when `E` itself implements `error`; `go vet` flags `%w` with a `*E` operand (1.27+) ([Go 1.27](https://go.dev/doc/go1.27)).
- Combine independent failures with `errors.Join` ([errors](https://pkg.go.dev/errors)).
- Either return an error or log it, not both; let the caller decide ([Google style](https://google.github.io/styleguide/go/best-practices#logging-errors)).
- Do not panic for ordinary errors in libraries; reserve `panic` for programmer bugs and recover only inside the same package ([CodeReviewComments](https://go.dev/wiki/CodeReviewComments#dont-panic), [Effective Go](https://go.dev/doc/effective_go#panic)).

### Interfaces, types, and generics

- Define interfaces in the consuming package, keep them small, and return concrete types from constructors ([CodeReviewComments](https://go.dev/wiki/CodeReviewComments#interfaces)).
- Do not define interfaces on the implementor side "for mocking" or before a real use exists ([CodeReviewComments](https://go.dev/wiki/CodeReviewComments#interfaces)).
- Make the zero value useful so types work without a constructor where possible ([Effective Go](https://go.dev/doc/effective_go#allocation_new)).
- Use pointer receivers for mutation, large structs, or structs containing `sync.Mutex`; do not mix value and pointer receivers on one type ([CodeReviewComments](https://go.dev/wiki/CodeReviewComments#receiver-type)).
- Use type parameters when the same code would be written for several element types; keep interface parameters when only methods are called ([When to use generics](https://go.dev/blog/when-generics)).
- Declare type parameters on methods when the operation belongs to the type instead of a package-level function; interface methods cannot be generic and generic methods do not satisfy interfaces (1.27+) ([Go 1.27](https://go.dev/doc/go1.27), [Generic methods](https://go.dev/blog/generic-methods)).

```go
func (l List[E]) Map[R any](f func(E) R) List[R] { /* ... */ }
```

### Iterators

- Expose traversal as `iter.Seq[V]`/`iter.Seq2[K, V]` methods named `All`, `Keys`, or `Values` instead of callbacks or slice copies (1.23+) ([iter](https://pkg.go.dev/iter), [Range over function types](https://go.dev/blog/range-functions)).
- Stop yielding as soon as `yield` returns false; continuing panics at run time (1.23+) ([iter](https://pkg.go.dev/iter)).

```go
func (s *Set[E]) All() iter.Seq[E] {
	return func(yield func(E) bool) {
		for v := range s.m {
			if !yield(v) {
				return
			}
		}
	}
}
```

- Compose with `slices.Collect`, `slices.Sorted(maps.Keys(m))`, and `maps.All` instead of manual key-collection loops (1.23+) ([slices](https://pkg.go.dev/slices), [maps](https://pkg.go.dev/maps)).

### Context

- Pass `ctx context.Context` as the first parameter of any call that does I/O or may block; never store it in a struct ([context](https://pkg.go.dev/context), [CodeReviewComments](https://go.dev/wiki/CodeReviewComments#contexts)).
- Never pass a nil context; use `context.TODO()` while plumbing is incomplete ([context](https://pkg.go.dev/context)).
- Call the `cancel` function from `WithCancel`/`WithTimeout`/`WithDeadline` with `defer cancel()` on every path ([context](https://pkg.go.dev/context)).
- Record why work stopped with `WithCancelCause`/`WithTimeoutCause` and read it with `context.Cause` (1.21+) ([context](https://pkg.go.dev/context)).
- Use `context.WithoutCancel` for work that must outlive the request but keep its values (1.21+) ([context](https://pkg.go.dev/context)).
- Use context values only for request-scoped data crossing API boundaries, keyed by an unexported type, never for optional parameters ([context](https://pkg.go.dev/context)).
- Derive the root context for graceful shutdown from `signal.NotifyContext`; `context.Cause` reports which signal fired (cause 1.26+) ([Go 1.26](https://go.dev/doc/go1.26)).

### Concurrency

- Prefer synchronous APIs; let callers add goroutines ([CodeReviewComments](https://go.dev/wiki/CodeReviewComments#synchronous-functions)).
- Make every goroutine's exit condition obvious (context cancellation, closed channel, or `WaitGroup`); goroutines blocked on channels leak ([CodeReviewComments](https://go.dev/wiki/CodeReviewComments#goroutine-lifetimes)).
- Start counted goroutines with `wg.Go(f)` instead of `wg.Add(1)` plus `defer wg.Done()` (1.25+) ([sync](https://pkg.go.dev/sync), [Go 1.25](https://go.dev/doc/go1.25)).

```go
var wg sync.WaitGroup
for _, u := range urls {
	wg.Go(func() { fetch(ctx, u) })
}
wg.Wait()
```

- Use `golang.org/x/sync/errgroup` (`WithContext`, `SetLimit`) when goroutines return errors or need bounded parallelism ([errgroup](https://pkg.go.dev/golang.org/x/sync/errgroup)).
- Close a channel from the sending stage once all sends are done, so receivers ranging over it terminate ([Go blog: pipelines](https://go.dev/blog/pipelines)).
- Do not communicate by sharing memory; share memory by communicating, and use a mutex only for simple guarded state ([Effective Go](https://go.dev/doc/effective_go#sharing)).
- Run tests and representative workloads with `-race` in CI ([Race detector](https://go.dev/doc/articles/race_detector)).
- Check for leaked goroutines with the `goroutineleak` profile (`runtime/pprof` or `/debug/pprof/goroutineleak`) (1.27+) ([Go 1.27](https://go.dev/doc/go1.27)).
- Do not set `GOMAXPROCS` manually in containers; the runtime honors cgroup CPU limits and setting it disables that (1.25+) ([Go 1.25](https://go.dev/doc/go1.25)).

### Standard library choices

- Log with `log/slog` and a handler such as `slog.NewJSONHandler`; pass context with `InfoContext` and similar (1.21+) ([slog](https://pkg.go.dev/log/slog), [Go blog](https://go.dev/blog/slog)).
- Fan out to several log sinks with `slog.NewMultiHandler` (1.26+) ([Go 1.26](https://go.dev/doc/go1.26)).
- Use `encoding/json/v2` for new JSON code; it rejects invalid UTF-8 and duplicate names by default. Keep `encoding/json` in existing code; it is now backed by v2 (1.27+) ([encoding/json](https://pkg.go.dev/encoding/json), [Go 1.27](https://go.dev/doc/go1.27)).
- Use the `omitzero` struct tag instead of `omitempty` for zero structs and `time.Time` (1.24+) ([Go 1.24](https://go.dev/doc/go1.24)).
- Route with `net/http.ServeMux` method and wildcard patterns before adding a router dependency (1.22+) ([Routing enhancements](https://go.dev/blog/routing-enhancements)).

```go
mux := http.NewServeMux()
mux.HandleFunc("GET /items/{id}", func(w http.ResponseWriter, r *http.Request) {
	id := r.PathValue("id")
	// ...
})
```

- Generate UUIDs with the standard `uuid` package (`uuid.New()`) instead of a third-party module (1.27+) ([uuid](https://pkg.go.dev/uuid), [Go 1.27](https://go.dev/doc/go1.27)).
- Use `math/rand/v2` for non-security randomness in new code (1.22+) ([Go 1.22](https://go.dev/doc/go1.22)); never use it for keys or tokens ([CodeReviewComments](https://go.dev/wiki/CodeReviewComments#crypto-rand)).

### Testing

- Write table-driven tests with `t.Run` subtests named by case ([TableDrivenTests](https://go.dev/wiki/TableDrivenTests)).
- Report failures as `Func(input) = got; want want`, with got before want ([CodeReviewComments](https://go.dev/wiki/CodeReviewComments#useful-test-failures)).
- Use `t.Context()`, `t.Chdir()`, `t.TempDir()`, and `t.Cleanup()` instead of hand-managed setup and teardown (`Context`/`Chdir` 1.24+) ([testing](https://pkg.go.dev/testing), [Go 1.24](https://go.dev/doc/go1.24)).
- Write benchmarks with `for b.Loop() { ... }` instead of `b.N` loops and manual `ResetTimer` (1.24+) ([Go blog](https://go.dev/blog/testing-b-loop)).
- Test time- and goroutine-dependent code with `testing/synctest` instead of real sleeps (1.25+) ([synctest](https://pkg.go.dev/testing/synctest)).

```go
func TestExpiry(t *testing.T) {
	synctest.Test(t, func(t *testing.T) {
		c := NewCache(time.Minute)
		time.Sleep(2 * time.Minute) // fake clock, returns instantly
		synctest.Wait()
		// assert c has expired the entry
	})
}
```

- Use `httptest.NewTestServer` for HTTP tests inside `synctest` bubbles (1.27+) ([Go 1.27](https://go.dev/doc/go1.27)).
- Fuzz parsers and decoders of untrusted input with `func FuzzX(f *testing.F)` and `go test -fuzz=FuzzX` ([Go fuzzing](https://go.dev/doc/security/fuzz/)).
- Add runnable `Example` functions for exported APIs ([CodeReviewComments](https://go.dev/wiki/CodeReviewComments#examples)).
- Write test outputs to `t.ArtifactDir()` so `go test -artifacts` can keep them (1.26+) ([Go 1.26](https://go.dev/doc/go1.26)).

### Modules, tooling, and dependencies

- Set the `go` line to the oldest version the code needs; it is a mandatory minimum and gates language features ([go.mod reference](https://go.dev/doc/modules/gomod-ref#go)).
- Use the `toolchain` line only to suggest a newer toolchain for the main module; do not use it as a substitute for `go` ([go.mod reference](https://go.dev/doc/modules/gomod-ref#toolchain), [Go toolchains](https://go.dev/blog/toolchain)).
- Track developer tools with `tool` directives (`go get -tool pkg@version`, then `go tool name`) instead of a `tools.go` file (1.24+) ([go.mod reference](https://go.dev/doc/modules/gomod-ref#tool)).
- Exclude non-Go or generated directories from `./...` with the `ignore` directive (1.25+) ([go.mod reference](https://go.dev/doc/modules/gomod-ref#ignore)).
- Run `go mod tidy` after dependency changes and commit both `go.mod` and `go.sum` ([Managing dependencies](https://go.dev/doc/modules/managing-dependencies)).
- Follow the official layout: `cmd/<name>` for multiple commands and `internal/` for packages not meant for import by other modules ([Module layout](https://go.dev/doc/modules/layout)).
- Run `go fix ./...` after each toolchain upgrade to apply modernizers; it only proposes features the `go` line allows (1.26+) ([go fix](https://go.dev/blog/gofix)).
- Keep `go vet ./...` clean; `go test` also runs `stdversion` to catch standard library symbols newer than the `go` line (1.27+) ([Go 1.27](https://go.dev/doc/go1.27), [Security best practices](https://go.dev/security/best-practices#use-vet-to-examine-suspicious-constructs)).

### Security

- Scan source and binaries with `govulncheck ./...` in CI ([Security best practices](https://go.dev/security/best-practices#scan-source-code-and-binaries-for-vulnerabilities), [govulncheck tutorial](https://go.dev/doc/tutorial/govulncheck)).
- Keep Go and dependencies on supported, patched releases ([Security best practices](https://go.dev/security/best-practices#keep-your-go-version-and-dependencies-up-to-date), [Release policy](https://go.dev/doc/devel/release)).
- Generate keys, tokens, and secrets with `crypto/rand`; use `rand.Text()` for secret strings (`Text` 1.24+) ([crypto/rand](https://pkg.go.dev/crypto/rand), [CodeReviewComments](https://go.dev/wiki/CodeReviewComments#crypto-rand)).
- Pass SQL values as query parameters (`db.QueryContext(ctx, "... WHERE id = ?", id)`); never build SQL with `fmt.Sprintf` ([Avoiding SQL injection](https://go.dev/doc/database/sql-injection)).
- Render HTML with `html/template`, never `text/template`, for contextual autoescaping ([html/template](https://pkg.go.dev/html/template)).
- Open user-influenced paths through `os.OpenRoot`/`os.Root` to block `..` and symlink traversal (1.24+) ([Go blog](https://go.dev/blog/osroot), [os](https://pkg.go.dev/os)).
- Wrap cookie-authenticated handlers with `http.NewCrossOriginProtection().Handler(h)` for CSRF protection (1.25+) ([Go 1.25](https://go.dev/doc/go1.25), [net/http](https://pkg.go.dev/net/http)).
- Use `httputil.ReverseProxy.Rewrite`, not the deprecated `Director` hook ([Go 1.26](https://go.dev/doc/go1.26)).

### Performance and diagnostics

- Measure before optimizing: write `b.Loop` benchmarks and profile with `runtime/pprof` or `net/http/pprof` ([Diagnostics](https://go.dev/doc/diagnostics#profiling)).
- Serve `net/http/pprof` only on an internal listener; importing it registers handlers on `http.DefaultServeMux` ([Diagnostics](https://go.dev/doc/diagnostics)).
- Enable profile-guided optimization by committing a representative CPU profile as `default.pgo` in the main package directory (1.21+) ([PGO](https://go.dev/doc/pgo)).
- Build strings incrementally with `strings.Builder`, which minimizes copying, instead of repeated `+` in loops ([strings](https://pkg.go.dev/strings)).
- Use `runtime.AddCleanup` instead of `runtime.SetFinalizer` (1.24+) ([Go 1.24](https://go.dev/doc/go1.24)).

## Examples

Input: "Add an endpoint that fetches several URLs concurrently and returns the first error." (module declares `go 1.27`)
Output: A `GET /fetch` handler on `http.ServeMux` with method pattern; `errgroup.WithContext(r.Context())` with `SetLimit`; each fetch takes `ctx` first; errors wrapped as `fmt.Errorf("fetch %s: %w", u, err)`; JSON response via `encoding/json/v2`; a table-driven `httptest` test run with `go test -race`.

Input: "Review this library package." (module declares `go 1.22`)
Output: Findings citing consumer-side interfaces, lowercase error strings, `errors.Is` instead of `==`, removal of `v := v` copies, nil-slice declarations, and missing doc comments; suggestions for `wg.Go`, `errors.AsType`, and `b.Loop` are marked as requiring a `go` line bump, not applied.

Input: "We upgraded to Go 1.27; modernize the codebase."
Output: Run `go fix -diff ./...`, then `go fix ./...` and `go mod tidy`; replace `tools.go` with `tool` directives; migrate `b.N` benchmarks to `b.Loop`; switch `google/uuid` to `uuid` where only `New`/`Parse` are used; run `go vet ./...`, `go test -race ./...`, and `govulncheck ./...`.

## Edge cases

- `go` line older than a tagged feature: keep compatible code (for example `wg.Add(1)`/`defer wg.Done()`, `errors.As` with a target variable) and suggest raising the `go` line instead of adding a `//go:build` split.
- Library modules: keep the `go` line at the oldest supported release (currently 1.26) unless a newer feature is essential; note that `go mod init` on 1.27 already writes `go 1.26.0`.
- Experimental features: `simd`, `simd/archsimd`, and `runtime/secret` require `GOEXPERIMENT` and have unstable APIs; use them only on explicit request and behind build tags.
- JSON v2 migration: if `encoding/json` behavior changed after upgrading, prefer v1-compatibility options over `GOEXPERIMENT=nojsonv2`, which is a temporary opt-out.
- Benchmarks or tests assert exact `compress/flate`, `image/jpeg`, or closure symbol names: expect differences after 1.26/1.27 upgrades and compare semantics instead.
- Removed `GODEBUG` settings (for example `asynctimerchan`): delete old-value `godebug` lines from `go.mod` before upgrading to 1.27, or the build fails.
- Generated code (`// Code generated ... DO NOT EDIT.`): do not hand-edit or reformat; change the generator and rerun `go generate`. `go fix` skips generated files.
- Project conventions conflict (for example a mandated router, logger, or assertion library): follow the project, but still enforce error checking, context propagation, and race-free code.
- cgo or platform-specific files: run `go vet` and `go fix` under each relevant `GOOS`/`GOARCH`, since each run covers one build configuration.
- golangci-lint version predates the module's `go` line: upgrade the linter instead of disabling checks that fail to parse new syntax such as generic methods.
- `go` line 1.25 or 1.26 and JSON v2 wanted: `encoding/json/v2` there is experimental behind `GOEXPERIMENT=jsonv2`, and its API changed before 1.27; keep `encoding/json` until the module requires 1.27.
- `go` line 1.26 and leak detection wanted: the `goroutineleak` profile is experimental there (`GOEXPERIMENT=goroutineleakprofile`); use it only in tests or CI, not production builds.
- Multi-module repositories with `go.work`: run commands from the workspace root, keep each module's `go.mod` tidy independently, and do not commit `go.work` for published libraries unless the project already does.
- Vendored dependencies (`vendor/` present): run `go mod vendor` after `go mod tidy` and never edit files under `vendor/` by hand.

## Resources

- [Go 1.27 Release Notes](https://go.dev/doc/go1.27): read when using or reviewing any 1.27 language, tool, or library change.
- [Go 1.26 Release Notes](https://go.dev/doc/go1.26): read when targeting the 1.26 baseline (`new(expr)`, `errors.AsType`, `go fix`).
- [Release History](https://go.dev/doc/devel/release): read when checking supported versions and security patch releases.
- [Effective Go](https://go.dev/doc/effective_go): read when unsure of an idiom for naming, allocation, interfaces, or concurrency.
- [Go Code Review Comments](https://go.dev/wiki/CodeReviewComments): read when reviewing code for common style and correctness issues.
- [Google Go Style Guide](https://google.github.io/styleguide/go/guide): read when a style question is not covered by Effective Go.
- [Go Doc Comments](https://go.dev/doc/comment): read when writing package or API documentation.
- [go.mod reference](https://go.dev/doc/modules/gomod-ref): read when editing `go`, `toolchain`, `tool`, `ignore`, or `godebug` directives.
- [Security Best Practices](https://go.dev/security/best-practices): read when setting up CI checks or handling untrusted input.
- [Diagnostics](https://go.dev/doc/diagnostics): read when profiling, tracing, or debugging performance.
- [Using go fix](https://go.dev/blog/gofix): read when modernizing code after a toolchain upgrade.
