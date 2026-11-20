---
name: rust-best-practices
description: "Applies current, officially sourced Rust 1.100 and edition 2024 best practices to write or review Rust code across naming, API design, ownership, errors, pattern matching, traits, concurrency, async, unsafe, docs, testing, Cargo, supply chain, and performance. Use when the user asks to write, refactor, review, or upgrade Rust code, mentions Cargo.toml, rustfmt, clippy, editions, MSRV, unsafe, or cargo audit, or works with .rs files or Cargo workspaces."
license: MIT
---

# Rust 1.100 best practices

Produces idiomatic, safe Rust that targets the crate's declared edition and `rust-version`. Rust 1.100.0 is the latest stable release (2026-11-12), and Rust 2024 (stabilized in 1.85) is the current edition. Stable releases ship every six weeks and only the latest stable gets fixes, so pin the MSRV on purpose instead of by accident.

## Steps

1. Detect the target. Read `edition` and `rust-version` in each `Cargo.toml` (and `[workspace.package]`), `rust-toolchain.toml`, and the toolchain pinned in CI or `Dockerfile`.
2. Detect project tooling: `[lints]`/`[workspace.lints]` tables, `clippy.toml`, `rustfmt.toml`, `deny.toml`, `.cargo/config.toml`, and CI jobs for fmt, clippy, test, doc, and audit.
3. Apply the practices below. Use version-tagged features only when `rust-version` is at least that version, and edition-tagged features only on that edition. Otherwise write compatible code and suggest the bump.
4. Follow existing project conventions and lint configs when they conflict with a non-safety rule. Never relax soundness, `unsafe` documentation, or error-handling rules for consistency.
5. Run `cargo fmt --all --check`, `cargo clippy --workspace --all-targets --all-features -- -D warnings`, `cargo test --workspace --all-features`, `cargo doc --no-deps`, and `cargo audit` or `cargo deny check`. Prefer the project's CI or `just`/`make` targets when they exist.
6. When upgrading the edition, run `cargo fix --edition`, set the new `edition`, then rerun the checks in step 5 and review the diff.

## Best practices

### Formatting, naming, lints

- Format every file with `rustfmt` and configure it only through `rustfmt.toml`, never by hand-aligning code ([Style Guide](https://doc.rust-lang.org/style-guide/index.html), [rustfmt](https://rust-lang.github.io/rustfmt/)).
- Use `UpperCamelCase` for types and traits, `snake_case` for functions, modules, locals, and fields, and `SCREAMING_SNAKE_CASE` for constants and statics. Treat acronyms as one word (`Uuid`, not `UUID`) ([API Guidelines C-CASE](https://rust-lang.github.io/api-guidelines/naming.html#c-case)).
- Name conversions by cost and ownership: `as_` is free and borrowed, `to_` is expensive or owned from borrowed, `into_` consumes `self` ([C-CONV](https://rust-lang.github.io/api-guidelines/naming.html#c-conv)).
- Name getters after the field (`fn name(&self)`), not `get_name`. Reserve `get` for a single obvious item such as `Cell::get` ([C-GETTER](https://rust-lang.github.io/api-guidelines/naming.html#c-getter)).
- Name iterator methods `iter`, `iter_mut`, and `into_iter`, and name the iterator types after the method (`IntoIter`) ([C-ITER](https://rust-lang.github.io/api-guidelines/naming.html#c-iter), [C-ITER-TY](https://rust-lang.github.io/api-guidelines/naming.html#c-iter-ty)).
- Name feature flags after what they enable (`serde`, not `use-serde` or `with-serde`) ([C-FEATURE](https://rust-lang.github.io/api-guidelines/naming.html#c-feature)).
- Silence a lint with `#[expect(lint, reason = "...")]` instead of `#[allow]`, so the attribute warns once it is no longer needed (1.81+) ([Reference](https://doc.rust-lang.org/reference/attributes/diagnostics.html#the-expect-attribute), [Rust 1.81](https://blog.rust-lang.org/2024/09/05/Rust-1.81.0/)).

```rust
#[expect(clippy::cast_possible_truncation, reason = "len is checked to fit in u32 above")]
let n = len as u32;
```

- Configure lints once in `[workspace.lints]` and opt in with `lints.workspace = true` in each member, instead of `#![deny]` blocks at crate roots (1.74+) ([Cargo lints](https://doc.rust-lang.org/cargo/reference/manifest.html#the-lints-section), [Workspaces](https://doc.rust-lang.org/cargo/reference/workspaces.html#the-lints-table)).

```toml
[workspace.lints.rust]
unsafe_op_in_unsafe_fn = "deny"
missing_docs = "warn"

[workspace.lints.clippy]
pedantic = { level = "warn", priority = -1 }
undocumented_unsafe_blocks = "deny"
```

- Deny warnings in CI with `CARGO_BUILD_WARNINGS=deny` (or `build.warnings = "deny"`) instead of `RUSTFLAGS=-Dwarnings`, which invalidates the build cache (1.97+) ([Rust 1.97](https://blog.rust-lang.org/2026/07/09/Rust-1.97.0/), [Cargo config](https://doc.rust-lang.org/cargo/reference/config.html#buildwarnings)).
- Treat Clippy's default groups as required and enable `pedantic` lints selectively. Never enable the `restriction` group wholesale ([Clippy](https://doc.rust-lang.org/clippy/lints.html)).

### API design

- Eagerly implement the common traits that apply: `Debug`, `Clone`, `Copy`, `PartialEq`, `Eq`, `Hash`, `PartialOrd`, `Ord`, `Default`, and `Display` for user-facing types ([C-COMMON-TRAITS](https://rust-lang.github.io/api-guidelines/interoperability.html#c-common-traits), [C-DEBUG](https://rust-lang.github.io/api-guidelines/debuggability.html#c-debug)).
- Implement `From` for conversions and let callers use `Into`. Implement `TryFrom` for fallible ones. Never implement `Into` or `TryInto` directly ([C-CONV-TRAITS](https://rust-lang.github.io/api-guidelines/interoperability.html#c-conv-traits), [std::convert::From](https://doc.rust-lang.org/std/convert/trait.From.html)).
- Make types `Send` and `Sync` where possible, and assert it in a test so a field change does not silently remove it ([C-SEND-SYNC](https://rust-lang.github.io/api-guidelines/interoperability.html#c-send-sync)).
- Wrap primitives in newtypes to give them meaning and to hide representation (`struct Meters(f64)`) ([C-NEWTYPE](https://rust-lang.github.io/api-guidelines/type-safety.html#c-newtype), [Book](https://doc.rust-lang.org/book/ch20-02-advanced-traits.html#using-the-newtype-pattern-to-implement-external-traits)).
- Use enums or dedicated types instead of `bool` or `Option` arguments that make call sites unreadable (`Compression::Fast`, not `true`) ([C-CUSTOM-TYPE](https://rust-lang.github.io/api-guidelines/type-safety.html#c-custom-type)).
- Use a builder for types with many optional parameters ([C-BUILDER](https://rust-lang.github.io/api-guidelines/type-safety.html#c-builder)).
- Mark public enums and structs that will grow with `#[non_exhaustive]` so new variants or fields are not breaking changes ([Reference](https://doc.rust-lang.org/reference/attributes/type_system.html#the-non_exhaustive-attribute), [C-STRUCT-PRIVATE](https://rust-lang.github.io/api-guidelines/future-proofing.html#c-struct-private)).
- Keep struct fields private and expose methods. Public fields freeze the representation ([C-STRUCT-PRIVATE](https://rust-lang.github.io/api-guidelines/future-proofing.html#c-struct-private)).
- Add `#[must_use]` to functions and types whose result is a mistake to ignore, such as pure methods returning a new value or guards ([Reference](https://doc.rust-lang.org/reference/attributes/diagnostics.html#the-must_use-attribute), [Clippy must_use_candidate](https://rust-lang.github.io/rust-clippy/master/index.html#must_use_candidate)).
- Seal traits that downstream crates should use but not implement, with a private supertrait ([C-SEALED](https://rust-lang.github.io/api-guidelines/future-proofing.html#c-sealed)).

```rust
mod private { pub trait Sealed {} }
pub trait Shape: private::Sealed { fn area(&self) -> f64; }
```

- Accept the most general input that costs nothing: `impl AsRef<Path>` for paths, `impl Into<String>` when the function stores the string ([C-GENERIC](https://rust-lang.github.io/api-guidelines/flexibility.html#c-generic), [std::convert::AsRef](https://doc.rust-lang.org/std/convert/trait.AsRef.html)).
- Let the caller decide where to copy and allocate. Take owned values only when the function stores them ([C-CALLER-CONTROL](https://rust-lang.github.io/api-guidelines/flexibility.html#c-caller-control)).
- Follow SemVer for public items and check releases with the Cargo SemVer reference before publishing ([SemVer Compatibility](https://doc.rust-lang.org/cargo/reference/semver.html)).

### Ownership and borrowing

- Take `&str`, `&[T]`, and `&Path` parameters instead of `&String`, `&Vec<T>`, and `&PathBuf` ([Book](https://doc.rust-lang.org/book/ch04-03-slices.html#string-slices-as-parameters), [Clippy ptr_arg](https://rust-lang.github.io/rust-clippy/master/index.html#ptr_arg)).
- Borrow instead of cloning to satisfy the borrow checker. Restructure scopes first, and clone only when shared ownership is the real intent ([Book](https://doc.rust-lang.org/book/ch04-02-references-and-borrowing.html), [Clippy redundant_clone](https://rust-lang.github.io/rust-clippy/master/index.html#redundant_clone)).
- Return `Cow<'_, str>` when a function usually returns its input unchanged and only sometimes allocates ([std::borrow::Cow](https://doc.rust-lang.org/std/borrow/enum.Cow.html)).
- Use `Rc` for shared ownership in one thread and `Arc` across threads. Break cycles with `Weak` ([Book](https://doc.rust-lang.org/book/ch15-06-reference-cycles.html)).
- Prefer compile-time borrowing to `RefCell`. Use interior mutability only when the design needs it, and keep borrows short to avoid runtime panics ([Book](https://doc.rust-lang.org/book/ch15-05-interior-mutability.html)).
- Use `std::mem::take` or `replace` to move out of a `&mut` field instead of cloning ([std::mem::take](https://doc.rust-lang.org/std/mem/fn.take.html)).
- Use `core::mem::DropGuard` to run cleanup on every exit path, and `DropGuard::dismiss` to commit (1.100+) ([Rust 1.100](https://blog.rust-lang.org/2026/11/12/Rust-1.100.0/), [DropGuard](https://doc.rust-lang.org/stable/core/mem/struct.DropGuard.html)).
- Use `LazyLock` and `LazyCell` for lazily initialized globals instead of `lazy_static` or `once_cell` (1.80+) ([Rust 1.80](https://blog.rust-lang.org/2024/07/25/Rust-1.80.0/), [std::sync::LazyLock](https://doc.rust-lang.org/std/sync/struct.LazyLock.html)).

### Errors and panics

- Return `Result` for recoverable errors and propagate with `?`. Reserve `panic!` for bugs and broken invariants ([Book](https://doc.rust-lang.org/book/ch09-03-to-panic-or-not-to-panic.html)).
- Do not call `unwrap` in library code. Use `expect("why this cannot fail")` when a failure is a bug, and state the invariant in the message ([std::option::Option::expect](https://doc.rust-lang.org/std/option/enum.Option.html#recommended-message-style), [Clippy unwrap_used](https://rust-lang.github.io/rust-clippy/master/index.html#unwrap_used)).
- Give library errors a concrete type that implements `std::error::Error`, `Debug`, `Display`, `Send`, and `Sync`. Never use `()` as an error type ([C-GOOD-ERR](https://rust-lang.github.io/api-guidelines/interoperability.html#c-good-err)).
- Write error `Display` messages lowercase without trailing punctuation, and expose the cause through `source()` instead of formatting it into the message ([std::error::Error](https://doc.rust-lang.org/std/error/trait.Error.html)).
- Use an enum error for libraries so callers can match on the cause. Use a boxed `dyn Error + Send + Sync` (or a crate built on it) in binaries where callers only report ([Book](https://doc.rust-lang.org/book/ch09-02-recoverable-errors-with-result.html#propagating-errors), [Rust by Example](https://doc.rust-lang.org/rust-by-example/error/multiple_error_types/boxing_errors.html)).
- Implement `From<SourceError>` for your error type so `?` converts it ([std::convert::From](https://doc.rust-lang.org/std/convert/trait.From.html#examples)).
- Write `-> Result<T, !>` or match `let Ok(v) = res;` when a path cannot fail. `Infallible` is now an alias for `!` (1.100+) ([Rust 1.100](https://blog.rust-lang.org/2026/11/12/Rust-1.100.0/), [never type](https://doc.rust-lang.org/stable/std/primitive.never.html)).
- Validate arguments at the API boundary and return an error, or document the panic in a `# Panics` section ([C-VALIDATE](https://rust-lang.github.io/api-guidelines/dependability.html#c-validate), [C-FAILURE](https://rust-lang.github.io/api-guidelines/documentation.html#c-failure)).
- Never panic or fail in `Drop`. Offer an explicit `close` method that returns `Result` for fallible cleanup ([C-DTOR-FAIL](https://rust-lang.github.io/api-guidelines/dependability.html#c-dtor-fail)).

### Pattern matching and control flow

- Use `let ... else` to bind or return early instead of a `match` with a diverging arm (1.65+) ([Reference](https://doc.rust-lang.org/reference/statements.html#let-else-statements)).

```rust
let Some(user) = users.get(id) else {
    return Err(Error::NotFound(id));
};
```

- Chain `if let` conditions with `&&` instead of nesting (1.88+, edition 2024 only) ([Rust 1.88](https://blog.rust-lang.org/2025/06/26/Rust-1.88.0/), [Reference](https://doc.rust-lang.org/reference/expressions/if-expr.html#chains-of-conditions)).

```rust
if let Some(cfg) = load() && cfg.enabled && let Ok(port) = cfg.port.parse::<u16>() {
    serve(port);
}
```

- Use `if let` guards in `match` arms when a guard needs a pattern match. They do not count toward exhaustiveness (1.95+) ([Rust 1.95](https://blog.rust-lang.org/2026/04/16/Rust-1.95.0/)).
- Match exhaustively on your own enums and avoid `_` arms there, so adding a variant breaks every site that must handle it ([Book](https://doc.rust-lang.org/book/ch06-02-match.html#matches-are-exhaustive), [Clippy wildcard_enum_match_arm](https://rust-lang.github.io/rust-clippy/master/index.html#wildcard_enum_match_arm)).
- Use `matches!` for boolean pattern tests and `assert_matches!` in tests, imported from `std` because it is not in the prelude (`assert_matches!` 1.96+) ([std::matches](https://doc.rust-lang.org/std/macro.matches.html), [Rust 1.96](https://blog.rust-lang.org/2026/05/28/Rust-1.96.0/)).
- Use the `Option` and `Result` combinators (`map`, `and_then`, `ok_or_else`, `unwrap_or_default`) when they are shorter than a `match` ([std::option](https://doc.rust-lang.org/std/option/index.html)).
- Use `cfg_select!` instead of chains of mutually exclusive `#[cfg]` items (1.95+) ([Rust 1.95](https://blog.rust-lang.org/2026/04/16/Rust-1.95.0/)).

### Iterators and collections

- Prefer iterator chains (`filter`, `map`, `collect`) to index loops. They skip bounds checks and state intent ([Book](https://doc.rust-lang.org/book/ch13-04-performance.html), [Clippy needless_range_loop](https://rust-lang.github.io/rust-clippy/master/index.html#needless_range_loop)).
- Collect into `Result<Vec<_>, _>` or `Option<Vec<_>>` to stop on the first failure ([std::iter::Iterator::collect](https://doc.rust-lang.org/std/iter/trait.Iterator.html#method.collect)).
- Return `impl Iterator<Item = T>` instead of building a `Vec` when callers only iterate ([Reference](https://doc.rust-lang.org/reference/types/impl-trait.html#abstract-return-types)).
- Use the `entry` API to insert or update map values with one lookup ([std::collections::hash_map::Entry](https://doc.rust-lang.org/std/collections/hash_map/enum.Entry.html)).
- Pick the collection by access pattern: `Vec` by default, `VecDeque` for queues, `HashMap` for lookups, `BTreeMap` for ordered keys ([std::collections](https://doc.rust-lang.org/std/collections/index.html#when-should-you-use-which-collection)).
- Use `get_disjoint_mut` to borrow several elements of a slice or map mutably at once instead of `split_at_mut` gymnastics or `unsafe` (1.86+) ([Rust 1.86](https://blog.rust-lang.org/2025/04/03/Rust-1.86.0/)).
- Use `array_windows` for fixed-size sliding windows over slices (1.94+) ([Rust 1.94](https://blog.rust-lang.org/2026/03/05/Rust-1.94.0/)).
- Use `str::trim_prefix`/`trim_suffix` when the affix is optional, and `strip_prefix` when its absence matters (1.100+) ([Rust 1.100](https://blog.rust-lang.org/2026/11/12/Rust-1.100.0/), [str](https://doc.rust-lang.org/stable/std/primitive.str.html#method.trim_prefix)).

### Traits and generics

- Use generics or `impl Trait` arguments for static dispatch by default. Use `dyn Trait` when you need heterogeneous collections or want to cut code size ([Book](https://doc.rust-lang.org/book/ch18-02-trait-objects.html), [Reference](https://doc.rust-lang.org/reference/types/impl-trait.html)).
- Use associated types when each implementor has exactly one natural choice (`Iterator::Item`), and generic parameters when a type may implement the trait many times ([Book](https://doc.rust-lang.org/book/ch20-02-advanced-traits.html#associated-types)).
- Put trait bounds in `where` clauses once they no longer fit on one line ([Book](https://doc.rust-lang.org/book/ch10-02-traits.html#clearer-trait-bounds-with-where-clauses)).
- Do not put bounds on struct definitions. Add them on the `impl` blocks that need them ([C-STRUCT-BOUNDS](https://rust-lang.github.io/api-guidelines/future-proofing.html#c-struct-bounds)).
- Upcast `&dyn Sub` to `&dyn Super` directly instead of adding `as_super` helper methods (1.86+) ([Rust 1.86](https://blog.rust-lang.org/2025/04/03/Rust-1.86.0/)).
- Write elided lifetimes consistently, such as `Iter<'_, u8>` instead of a bare `Iter`. The `mismatched_lifetime_syntaxes` lint warns by default (1.89+) ([Rust 1.89](https://blog.rust-lang.org/2025/08/07/Rust-1.89.0/)).
- Rely on edition 2024 return-position `impl Trait` capturing all in-scope lifetimes, and narrow it with `use<..>` bounds when needed (1.82+ for `use<..>`) ([Edition Guide](https://doc.rust-lang.org/edition-guide/rust-2024/rpit-lifetime-capture.html)).

### Concurrency and async

- Share state across threads with `Arc<Mutex<T>>` or `Arc<RwLock<T>>`, and prefer message passing with channels when ownership can move ([Book](https://doc.rust-lang.org/book/ch16-03-shared-state.html), [Book](https://doc.rust-lang.org/book/ch16-02-message-passing.html)).
- Use `std::thread::scope` to borrow local data in spawned threads instead of `Arc`-wrapping it (1.63+) ([std::thread::scope](https://doc.rust-lang.org/std/thread/fn.scope.html)).
- Use atomics for single counters and flags, with `Ordering::SeqCst` unless you can justify a weaker ordering ([std::sync::atomic](https://doc.rust-lang.org/std/sync/atomic/index.html), [Nomicon](https://doc.rust-lang.org/nomicon/atomics.html)).
- Keep lock guards in small scopes and never hold a `std::sync::Mutex` guard across an `.await` ([Clippy await_holding_lock](https://rust-lang.github.io/rust-clippy/master/index.html#await_holding_lock), [Tokio](https://docs.rs/tokio/latest/tokio/sync/struct.Mutex.html#which-kind-of-mutex-should-you-use)).
- Never block in async code. Move blocking I/O and CPU-heavy work to `spawn_blocking` or a thread pool ([Tokio](https://docs.rs/tokio/latest/tokio/task/fn.spawn_blocking.html), [Async Book](https://rust-lang.github.io/async-book/)).
- Use `async fn` in traits and async closures (`async || {}`) instead of boxing futures by hand (1.75+ and 1.85+) ([Rust 1.75](https://blog.rust-lang.org/2023/12/28/Rust-1.75.0/), [Rust 1.85](https://blog.rust-lang.org/2025/02/20/Rust-1.85.0/)).
- Keep spawned futures `Send + 'static` and bound public async trait methods with `Send` where executors require it ([Book](https://doc.rust-lang.org/book/ch17-00-async-await.html), [Rust blog](https://blog.rust-lang.org/2023/12/21/async-fn-rpit-in-traits/)).

### Unsafe code

- Avoid `unsafe` unless a safe API cannot express the operation or measurement shows the need. Wrap it in a small safe abstraction that upholds the invariants ([Nomicon](https://doc.rust-lang.org/nomicon/meet-safe-and-unsafe.html), [Book](https://doc.rust-lang.org/book/ch20-01-unsafe-rust.html)).
- Precede every `unsafe` block with a `// SAFETY:` comment that explains why each precondition holds ([Clippy undocumented_unsafe_blocks](https://rust-lang.github.io/rust-clippy/master/index.html#undocumented_unsafe_blocks), [std-dev guide](https://std-dev-guide.rust-lang.org/policy/safety-comments.html)).

```rust
// SAFETY: `idx < self.len` was checked above, so the pointer is in bounds.
let item = unsafe { self.ptr.add(idx).read() };
```

- Document the caller's obligations in a `# Safety` section on every `unsafe fn` and `unsafe trait` ([C-FAILURE](https://rust-lang.github.io/api-guidelines/documentation.html#c-failure), [rustdoc](https://doc.rust-lang.org/rustdoc/how-to-write-documentation.html#documenting-components)).
- Write explicit `unsafe {}` blocks inside `unsafe fn`. Edition 2024 warns by default through `unsafe_op_in_unsafe_fn` ([Edition Guide](https://doc.rust-lang.org/edition-guide/rust-2024/unsafe-op-in-unsafe-fn.html)).
- Write `unsafe extern "C" { ... }` blocks and `#[unsafe(no_mangle)]`/`#[unsafe(export_name)]`, which edition 2024 requires ([Edition Guide](https://doc.rust-lang.org/edition-guide/rust-2024/unsafe-extern.html), [Edition Guide](https://doc.rust-lang.org/edition-guide/rust-2024/unsafe-attributes.html)).
- Use `&raw const`/`&raw mut` to create raw pointers without an intermediate reference, and never take references to `static mut` (1.82+, a deny lint in edition 2024) ([Reference](https://doc.rust-lang.org/reference/expressions/operator-expr.html#raw-borrow-operators), [Edition Guide](https://doc.rust-lang.org/edition-guide/rust-2024/static-mut-references.html)).
- Use `MaybeUninit` for uninitialized memory. Never call `mem::uninitialized` or `assume_init` on memory that is not initialized ([std::mem::MaybeUninit](https://doc.rust-lang.org/std/mem/union.MaybeUninit.html)).
- Run tests that touch `unsafe` under Miri (`cargo +nightly miri test`) to catch undefined behavior ([Miri](https://github.com/rust-lang/miri), [Unsafe Code Guidelines](https://rust-lang.github.io/unsafe-code-guidelines/)).

### Documentation

- Document every public item, starting with a one-line summary sentence, and enable `missing_docs` for libraries ([rustdoc](https://doc.rust-lang.org/rustdoc/how-to-write-documentation.html), [C-CRATE-DOC](https://rust-lang.github.io/api-guidelines/documentation.html#c-crate-doc)).
- Add `# Errors`, `# Panics`, and `# Safety` sections where they apply ([C-FAILURE](https://rust-lang.github.io/api-guidelines/documentation.html#c-failure), [Clippy missing_errors_doc](https://rust-lang.github.io/rust-clippy/master/index.html#missing_errors_doc)).
- Give examples that use `?` rather than `unwrap` in doc tests ([C-QUESTION-MARK](https://rust-lang.github.io/api-guidelines/documentation.html#c-question-mark)).

```rust
/// Parses a port number.
///
/// # Errors
///
/// Returns [`ParseIntError`] if `s` is not a number in `0..=65535`.
///
/// ```
/// let port = mycrate::parse_port("8080")?;
/// assert_eq!(port, 8080);
/// # Ok::<(), std::num::ParseIntError>(())
/// ```
pub fn parse_port(s: &str) -> Result<u16, ParseIntError> { s.parse() }
```

- Link items with intra-doc links (``[`Vec::push`]``) instead of URLs, and check them with `cargo doc` and `rustdoc::broken_intra_doc_links` ([rustdoc](https://doc.rust-lang.org/rustdoc/write-documentation/linking-to-items-by-name.html)).
- Document feature-gated items and list features in the crate docs ([rustdoc](https://doc.rust-lang.org/rustdoc/unstable-features.html#doccfg-recording-what-platforms-or-features-are-required-for-code-to-be-present), [Cargo features](https://doc.rust-lang.org/cargo/reference/features.html#feature-documentation-and-discovery)).

### Testing

- Put unit tests in a `#[cfg(test)] mod tests` inside the module, integration tests in `tests/`, and examples in `examples/` ([Book](https://doc.rust-lang.org/book/ch11-03-test-organization.html), [Cargo targets](https://doc.rust-lang.org/cargo/reference/cargo-targets.html)).
- Return `Result<(), E>` from tests to use `?`, and use `#[should_panic(expected = "...")]` only for panics that the API documents ([Book](https://doc.rust-lang.org/book/ch11-01-writing-tests.html#using-resultt-e-in-tests)).
- Keep doc examples compiling and running. `cargo test` runs them, and `cargo test --doc` covers library-only crates ([rustdoc](https://doc.rust-lang.org/rustdoc/write-documentation/documentation-tests.html)).
- Test public behavior through the public API in integration tests, which compile as a separate crate ([Book](https://doc.rust-lang.org/book/ch11-03-test-organization.html#integration-tests)).
- Test with `--all-features` and with `--no-default-features` so every feature combination you support builds ([Cargo features](https://doc.rust-lang.org/cargo/reference/features.html#feature-unification)).

### Cargo, MSRV, supply chain

- Set `edition = "2024"` for new crates and `rust-version` to the oldest toolchain you test in CI. Cargo then refuses older toolchains with a clear error ([Cargo manifest](https://doc.rust-lang.org/cargo/reference/manifest.html#the-rust-version-field), [Edition Guide](https://doc.rust-lang.org/edition-guide/rust-2024/index.html)).
- Use resolver 3, the edition 2024 default, so dependency resolution respects `rust-version` (1.84+) ([Cargo resolver](https://doc.rust-lang.org/cargo/reference/resolver.html#rust-version), [Rust 1.84](https://blog.rust-lang.org/2025/01/09/Rust-1.84.0/)).
- Share versions and metadata through `[workspace.dependencies]` and `[workspace.package]`, inherited with `workspace = true` ([Workspaces](https://doc.rust-lang.org/cargo/reference/workspaces.html#the-dependencies-table)).
- Keep features additive. Enabling a feature must never remove an API or break another feature, because Cargo unifies them across the graph ([Cargo features](https://doc.rust-lang.org/cargo/reference/features.html#feature-unification)).
- Commit `Cargo.lock` for all packages and test against the latest compatible versions in a separate CI job ([Cargo FAQ](https://doc.rust-lang.org/cargo/faq.html#why-have-cargolock-in-version-control)).
- Remove dependencies that Cargo reports as unused through `cargo::unused_dependencies` (1.100+) ([Rust 1.100](https://blog.rust-lang.org/2026/11/12/Rust-1.100.0/), [Cargo lints](https://doc.rust-lang.org/stable/cargo/reference/lints.html)).
- Set `registry.global-min-publish-age` in `.cargo/config.toml` to delay new dependency versions by a few days (1.100+) ([Rust 1.100](https://blog.rust-lang.org/2026/11/12/Rust-1.100.0/), [Cargo config](https://doc.rust-lang.org/cargo/reference/config.html#registryglobal-min-publish-age)).
- Scan the lockfile in CI with `cargo audit` against the RustSec database, or with `cargo deny check` for advisories, licenses, bans, and sources ([RustSec](https://rustsec.org/), [cargo-deny](https://embarkstudios.github.io/cargo-deny/)).
- Publish workspaces with `cargo publish --workspace`, which orders crates by dependency (1.90+) ([Rust 1.90](https://blog.rust-lang.org/2025/09/18/Rust-1.90.0/)).

### Performance

- Measure before optimizing. Benchmark with `cargo bench` and profile release builds with debug symbols enabled in the profile ([Cargo profiles](https://doc.rust-lang.org/cargo/reference/profiles.html), [The Rust Performance Book](https://nnethercote.github.io/perf-book/)).
- Preallocate with `Vec::with_capacity` or `String::with_capacity` when the size is known, and reuse buffers in loops with `clear` ([std::vec::Vec](https://doc.rust-lang.org/std/vec/struct.Vec.html#capacity-and-reallocation)).
- Avoid allocating in hot paths. Write into `&mut impl fmt::Write` or `io::Write` instead of returning a new `String` per call ([std::fmt::Write](https://doc.rust-lang.org/std/fmt/trait.Write.html)).
- Wrap `File` and sockets in `BufReader`/`BufWriter`, and lock `stdout` once for many writes ([std::io::BufWriter](https://doc.rust-lang.org/std/io/struct.BufWriter.html), [std::io::Stdout](https://doc.rust-lang.org/std/io/struct.Stdout.html#method.lock)).
- Use `std::hint::black_box` in benchmarks so the optimizer does not remove the measured work ([std::hint::black_box](https://doc.rust-lang.org/std/hint/fn.black_box.html)).
- Tune release profiles with `lto`, `codegen-units = 1`, and `panic = "abort"` only after measuring the gain ([Cargo profiles](https://doc.rust-lang.org/cargo/reference/profiles.html)).

## Examples

Input: "Add a function that loads a TOML config and returns typed settings." (crate declares `edition = "2024"`, `rust-version = "1.88"`)
Output: A `Config` struct with private fields and getters, `#[non_exhaustive]` `ConfigError` enum implementing `Error` with `source()`, `From<io::Error>` for `?`, a `load(path: impl AsRef<Path>)` function using `let ... else` and let chains, rustdoc with `# Errors` and a doc test, and unit tests returning `Result`.

Input: "Review this library crate." (crate declares `edition = "2021"`, no `rust-version`)
Output: Findings citing `&String` parameters, `unwrap` in library code, missing `Debug` impls, `#[allow]` without reason, and undocumented `unsafe` blocks. Let chains and `#[unsafe(no_mangle)]` are marked as requiring edition 2024, and adding `rust-version` is recommended.

Input: "Upgrade the workspace to edition 2024."
Output: Run `cargo fix --edition --workspace --all-targets --all-features`, set `edition = "2024"` in `[workspace.package]`, wrap `extern` blocks in `unsafe extern`, add `unsafe {}` blocks inside `unsafe fn`, replace `static mut` references with `&raw` or atomics, review `impl Trait` capture changes, then run fmt, clippy, test, and doc.

## Edge cases

- If `rust-version` is older than a tagged feature, keep compatible code (`once_cell`, `#[allow]`, nested `if let`) and suggest raising `rust-version` instead of adding `cfg` version checks.
- On edition 2021 or older, let chains, `unsafe extern` requirements, and the `impl Trait` capture rules do not apply. Do not write edition 2024 syntax without migrating.
- In `no_std` crates, use `core` and `alloc` paths, avoid `std::sync` and threads, and gate `std` behind an additive `std` feature.
- If the project already uses an error crate (`thiserror`, `anyhow`, `snafu`), follow that choice, but keep library errors matchable and avoid exposing a dependency's error type in public APIs.
- If an async runtime is already chosen, follow its primitives (for example `tokio::sync::Mutex` across `.await`) and do not mix runtimes.
- In FFI and `-sys` crates, keep raw bindings in the `-sys` crate and the safe wrapper in a separate crate, with `SAFETY` comments at every call.
- Do not hand-edit generated code (`build.rs` output, `bindgen`, macros). Change the generator and mark the module with `#[expect]` or `#[allow]` reasons for lints it cannot satisfy.
- Never type fallback changed in 1.100 for editions before 2024. If a dependency stops compiling with never type errors, update it before patching code.
- Run nightly-only tools (Miri, `rustfmt` unstable options) in a separate CI job and keep the main build on stable.

## Resources

- [Rust 1.100.0 announcement](https://blog.rust-lang.org/2026/11/12/Rust-1.100.0/): read when using the never type, `DropGuard`, unused dependency lint, or dependency cooldowns.
- [Release notes](https://doc.rust-lang.org/stable/releases.html): read when checking which version stabilized a feature.
- [The Rust Programming Language](https://doc.rust-lang.org/book/): read when unsure of a core idiom.
- [The Rust Reference](https://doc.rust-lang.org/reference/): read when a syntax or semantic question needs a precise answer.
- [Rust API Guidelines](https://rust-lang.github.io/api-guidelines/checklist.html): read when designing or reviewing a public API.
- [Edition Guide](https://doc.rust-lang.org/edition-guide/rust-2024/index.html): read when migrating editions or using edition-gated syntax.
- [The Cargo Book](https://doc.rust-lang.org/cargo/): read when editing manifests, workspaces, features, profiles, or lints.
- [Clippy lints](https://rust-lang.github.io/rust-clippy/master/index.html): read when configuring or explaining a lint.
- [The Rustonomicon](https://doc.rust-lang.org/nomicon/): read before writing or reviewing `unsafe` code.
- [The rustdoc book](https://doc.rust-lang.org/rustdoc/): read when writing docs or doc tests.
- [RustSec](https://rustsec.org/): read when triaging a security advisory for a dependency.
