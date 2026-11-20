---
name: python-best-practices
description: "Applies current, officially sourced Python 3.15 best practices to write, review, and modernize Python code, typing, packaging, async, testing, and security. Use when the user asks to write, review, refactor, or upgrade Python code, mentions Python versions, PEP 8, type hints, asyncio, pyproject.toml, or works with .py files, pyproject.toml, requirements files, or pylock.toml."
license: MIT
---

# Python 3.15 best practices

Produces idiomatic, typed, secure Python that targets Python 3.15 (released 2026-10-09) when possible and stays correct on the oldest supported release, Python 3.11 (security support until 2027-10). Python has no LTS line; every feature release gets five years of support.

## Steps

1. Detect the target version: read `[project] requires-python` in `pyproject.toml`, then `.python-version`, `setup.cfg` `python_requires`, `tox.ini`/`noxfile.py` env lists, CI matrices, and `target-version`/`python_version`/`pythonVersion` in `[tool.ruff]`, `[tool.black]`, `[tool.mypy]`, `[tool.pyright]` or `ruff.toml`, `mypy.ini`, `pyrightconfig.json`. The lowest version in `requires-python` is the floor for syntax and APIs.
2. Apply the practices below; use a version-tagged feature only when the floor supports it, otherwise write the compatible form and optionally suggest raising `requires-python`.
3. Follow the project's existing formatter, linter, and type-checker configuration when it conflicts with a non-safety rule; never relax a security rule for consistency.
4. Run the project's tools: the formatter (`ruff format` or `black .`), the linter (`ruff check .`), the type checker (`mypy .` or `pyright`), and the tests (`python -m pytest` or `python -m unittest`), using the commands the project already defines in CI or `[tool.*]` sections.
5. Run tests once with `python -X dev -W error` to surface resource leaks, unclosed files, and deprecation warnings before they become errors.

## Best practices

### Style and naming

- Follow PEP 8: 4-space indents, `snake_case` functions and variables, `CapWords` classes, `UPPER_CASE` module constants, `_leading_underscore` for internals ([PEP 8](https://peps.python.org/pep-0008/#naming-conventions)).
- Compare to singletons with `is`/`is not` (`if x is not None`), never `==` or truthiness when `None` is distinct from empty ([PEP 8](https://peps.python.org/pep-0008/#programming-recommendations)).
- Use `isinstance()` for type checks and `str.startswith()`/`endswith()` instead of slicing ([PEP 8](https://peps.python.org/pep-0008/#programming-recommendations)).
- Group imports as standard library, third party, local; avoid wildcard imports ([PEP 8](https://peps.python.org/pep-0008/#imports)).
- Make return statements consistent: if any branch returns a value, every branch returns explicitly, including `return None` ([PEP 8](https://peps.python.org/pep-0008/#programming-recommendations)).
- Write docstrings for public modules, classes, and functions with a one-line summary, a blank line, then details ([PEP 257](https://peps.python.org/pep-0257/)).
- Use f-strings for ordinary string building; nested same-type quotes inside replacement fields are legal (3.12+) ([What's new 3.12](https://docs.python.org/3/whatsnew/3.12.html)).
- Use `pathlib.Path` for filesystem paths instead of `os.path` string juggling; use `Path.copy()`/`Path.move()` for recursive copy and move (3.14+) ([pathlib](https://docs.python.org/3/library/pathlib.html), [What's new 3.14](https://docs.python.org/3/whatsnew/3.14.html)).
- Pass `encoding="utf-8"` to `open()`, `Path.read_text()`, and `write_text()`; 3.15 defaults to UTF-8 (3.15+), but explicit encodings keep behavior identical on older targets ([What's new 3.15](https://docs.python.org/3/whatsnew/3.15.html), [io](https://docs.python.org/3/library/io.html#io-encoding-warning)).

### Data modeling

- Use `@dataclass` for record types; add `slots=True` to cut memory and catch typos, `frozen=True` for value objects, `kw_only=True` when fields exceed about three (3.10+) ([dataclasses](https://docs.python.org/3/library/dataclasses.html)).

  ```python
  from dataclasses import dataclass

  @dataclass(frozen=True, slots=True, kw_only=True)
  class User:
      id: int
      email: str
      active: bool = True
  ```

- Create modified copies of frozen dataclasses and named tuples with `copy.replace(obj, field=value)` (3.13+) ([What's new 3.13](https://docs.python.org/3/whatsnew/3.13.html)).
- Use `field(default_factory=list)` for mutable defaults; never use a mutable literal as a default ([dataclasses](https://docs.python.org/3/library/dataclasses.html)).
- Use `enum.Enum` for closed sets of values and `StrEnum` when members must compare equal to strings (3.11+) ([Enum HOWTO](https://docs.python.org/3/howto/enum.html)).
- Use `frozendict` for immutable, hashable mappings such as constant lookup tables and cache keys (3.15+); accept `collections.abc.Mapping` in signatures so both `dict` and `frozendict` work ([What's new 3.15](https://docs.python.org/3/whatsnew/3.15.html), [PEP 814](https://peps.python.org/pep-0814/)).
- Use the `sentinel` builtin for "argument not supplied" markers instead of `object()` (3.15+); compare with `is` ([Built-in functions](https://docs.python.org/3/builtins/functions.html), [PEP 661](https://peps.python.org/pep-0661/)).

  ```python
  MISSING = sentinel("MISSING")

  def get(key: str, default: object = MISSING) -> object:
      if default is MISSING:
          ...
  ```

- Use `match` for structural dispatch on shapes (tuples, dataclasses, mappings), not as a replacement for a simple `if`/`elif` on one value ([PEP 636](https://peps.python.org/pep-0636/)).
- Use `*`/`**` unpacking in comprehensions to flatten iterables or merge mappings (3.15+) ([What's new 3.15](https://docs.python.org/3/whatsnew/3.15.html)).

  ```python
  flat = [*row for row in rows]           # avoid: [x for row in rows for x in row]
  merged = {**cfg for cfg in layers}
  ```

### Type hints

- Annotate all public functions, methods, and module-level constants; prefer abstract parameter types (`Iterable`, `Mapping`, `Sequence` from `collections.abc`) and concrete return types (`list`, `dict`) ([Typing best practices](https://typing.python.org/en/latest/reference/best_practices.html)).
- Use built-in generics (`list[int]`, `type[C]`) and `X | None`, never `typing.List`, `Optional`, or `Union`; put `None` last in unions ([Typing best practices](https://typing.python.org/en/latest/reference/best_practices.html)).
- Use `object`, not `Any`, for parameters that accept anything; reserve `Any` for types the type system cannot express ([Typing best practices](https://typing.python.org/en/latest/reference/best_practices.html)).
- Declare generics and aliases with PEP 695 syntax instead of `TypeVar` and `TypeAlias` (3.12+) ([PEP 695](https://peps.python.org/pep-0695/), [typing](https://docs.python.org/3/library/typing.html)).

  ```python
  type JSON = dict[str, JSON] | list[JSON] | str | int | float | bool | None

  def first[T](items: Sequence[T]) -> T:
      return items[0]

  class Box[T]:
      def __init__(self, value: T) -> None:
          self.value = value
  ```

- Write forward references unquoted and drop `from __future__ import annotations` in code targeting 3.14+; annotations are evaluated lazily (3.14+) and the future import is deprecated ([What's new 3.14](https://docs.python.org/3/whatsnew/3.14.html)).
- Read annotations at runtime with `annotationlib.get_annotations()` (3.14+) or `inspect.get_annotations()` on 3.10-3.13, never `obj.__annotations__` directly ([Annotations best practices](https://docs.python.org/3/howto/annotations.html)).
- Use `typing.Self` for methods returning their own class (3.11+) and `@typing.override` on overriding methods so checkers catch renamed bases (3.12+) ([typing](https://docs.python.org/3/library/typing.html)).
- Use `TypeIs` for user-defined narrowing functions instead of `TypeGuard` (3.13+) ([What's new 3.13](https://docs.python.org/3/whatsnew/3.13.html)).
- Type `TypedDict` keys with `Required`/`NotRequired` (3.11+) and `ReadOnly` (3.13+); use `closed=True` or `extra_items=` to describe extra keys (3.15+) ([typing](https://docs.python.org/3/library/typing.html), [What's new 3.15](https://docs.python.org/3/whatsnew/3.15.html)).
- Mark deprecated APIs with `@warnings.deprecated("use X")` so both type checkers and runtime report them (3.13+) ([warnings](https://docs.python.org/3/library/warnings.html)).
- Prefer `typing.Protocol` for structural interfaces that callers satisfy without inheriting; reserve ABCs for shared implementation ([typing](https://docs.python.org/3/library/typing.html)).

### Errors and exceptions

- Catch the narrowest exception types; never use bare `except:`, and catch `Exception` only at process or request boundaries where you log and re-raise or translate ([PEP 8](https://peps.python.org/pep-0008/#programming-recommendations)).
- Keep `try` bodies minimal so unrelated failures are not swallowed ([PEP 8](https://peps.python.org/pep-0008/#programming-recommendations)).
- Translate exceptions with `raise NewError(...) from exc`; use `from None` only to deliberately hide an irrelevant cause ([Tutorial: errors](https://docs.python.org/3/tutorial/errors.html#exception-chaining)).
- Derive custom exceptions from `Exception` (never `BaseException`) and give each package one base error class ([Built-in exceptions](https://docs.python.org/3/builtins/exceptions.html), [Tutorial: errors](https://docs.python.org/3/tutorial/errors.html#user-defined-exceptions)).
- Add context with `err.add_note(...)` instead of wrapping when the type should not change (3.11+) ([Tutorial: errors](https://docs.python.org/3/tutorial/errors.html#enriching-exceptions-with-notes)).
- Handle `ExceptionGroup` (raised by `TaskGroup` and similar APIs) with `except*` (3.11+) ([Tutorial: errors](https://docs.python.org/3/tutorial/errors.html#raising-and-handling-multiple-unrelated-exceptions)).
- Omit parentheses around multiple exception types only when there is no `as` clause (3.14+); keep `except (A, B) as e:` otherwise ([What's new 3.14](https://docs.python.org/3/whatsnew/3.14.html)).
- Never `return`, `break`, or `continue` out of a `finally` block; it silently discards in-flight exceptions and emits `SyntaxWarning` (3.14+) ([What's new 3.14](https://docs.python.org/3/whatsnew/3.14.html)).

### Resources and context managers

- Open files, sockets, locks, and connections with `with` so they close on every path ([Tutorial: errors](https://docs.python.org/3/tutorial/errors.html#predefined-clean-up-actions)).
- Write custom managers with `contextlib.contextmanager`; manage a variable number of resources with `ExitStack` ([contextlib](https://docs.python.org/3/library/contextlib.html)).
- Use `contextlib.suppress(SomeError)` only for one expected, ignorable exception, never `Exception` ([contextlib](https://docs.python.org/3/library/contextlib.html)).
- Use timezone-aware datetimes: `datetime.now(UTC)` (3.11+) and `zoneinfo.ZoneInfo` for local zones; `utcnow()` and `utcfromtimestamp()` are deprecated (3.12+) ([datetime](https://docs.python.org/3/library/datetime.html), [zoneinfo](https://docs.python.org/3/library/zoneinfo.html)).

### Async and concurrency

- Start async programs with one `asyncio.run(main())`; select a loop with `loop_factory=` (3.12+), not event-loop policies, which are deprecated (3.14+) and removed in 3.16 ([Runners](https://docs.python.org/3/library/asyncio-runner.html), [What's new 3.15](https://docs.python.org/3/whatsnew/3.15.html)).
- Run concurrent tasks in `asyncio.TaskGroup` instead of bare `create_task()` or `gather()`; it cancels siblings on failure (3.11+) ([Coroutines and tasks](https://docs.python.org/3/library/asyncio-task.html#taskgroups)).
- Bound waits with `async with asyncio.timeout(seconds):` instead of `wait_for` (3.11+) ([Coroutines and tasks](https://docs.python.org/3/library/asyncio-task.html#timeouts)).
- End a task group early with `tg.cancel()` instead of raising a sentinel exception (3.15+) ([Coroutines and tasks](https://docs.python.org/3/library/asyncio-task.html#asyncio.TaskGroup.cancel)).

  ```python
  async with asyncio.TaskGroup() as tg:
      for url in mirrors:
          tg.create_task(fetch_first(url, tg))  # calls tg.cancel() on success
  ```

- Keep a strong reference to any task created outside a `TaskGroup`; the loop holds only weak references and may collect it mid-run ([Coroutines and tasks](https://docs.python.org/3/library/asyncio-task.html)).
- Never call blocking I/O in a coroutine; offload it with `await asyncio.to_thread(func, ...)` ([Coroutines and tasks](https://docs.python.org/3/library/asyncio-task.html)).
- Use `ThreadPoolExecutor` for blocking I/O and `ProcessPoolExecutor` or `InterpreterPoolExecutor` (3.14+) for CPU-bound work on GIL builds; always use executors as context managers ([concurrent.futures](https://docs.python.org/3/library/concurrent.futures.html), [concurrent.interpreters](https://docs.python.org/3/library/concurrent.interpreters.html)).
- Protect shared mutable state with `threading.Lock` or other primitives; do not rely on built-in types' internal locking, especially on free-threaded builds (3.14+ supported) ([Free threading HOWTO](https://docs.python.org/3/howto/free-threading-python.html)).

### Modules and imports

- Mark heavy, optional imports `lazy` at module top level to cut startup time while keeping imports visible (3.15+); `lazy` is invalid inside functions, classes, and `try` blocks ([What's new 3.15](https://docs.python.org/3/whatsnew/3.15.html), [PEP 810](https://peps.python.org/pep-0810/)).

  ```python
  lazy import json
  lazy from decimal import Decimal
  ```

- When supporting versions older than 3.15, declare `__lazy_modules__ = ["pkg.heavy"]` instead of the keyword; older interpreters import eagerly ([Simple statements](https://docs.python.org/3/reference/simple_stmts.html)).
- Measure import cost with `python -X importtime` before optimizing startup ([What's new 3.14](https://docs.python.org/3/whatsnew/3.14.html)).
- Expose a package's public API explicitly via `__all__`; treat underscore names as private ([PEP 8](https://peps.python.org/pep-0008/#public-and-internal-interfaces)).

### Packaging and dependencies

- Declare metadata in `pyproject.toml`: always include `[build-system]`, put runtime deps and `requires-python` in `[project]` ([Writing pyproject.toml](https://packaging.python.org/en/latest/guides/writing-pyproject-toml/)).
- Put test, lint, and docs dependencies in `[dependency-groups]`, not in optional extras or loose `requirements-dev.txt` ([Dependency groups](https://packaging.python.org/en/latest/specifications/dependency-groups/)).

  ```toml
  [project]
  requires-python = ">=3.12"
  dependencies = ["httpx>=0.27"]

  [dependency-groups]
  test = ["pytest>=8"]
  ```

- Read TOML configuration with the stdlib `tomllib` (3.11+) instead of a third-party parser ([What's new 3.11](https://docs.python.org/3/whatsnew/3.11.html)).
- Use a `src/` layout for libraries so tests run against the installed package, not the working tree ([src layout](https://packaging.python.org/en/latest/discussions/src-layout-vs-flat-layout/)).
- Create one virtual environment per project with `python -m venv .venv`; never commit it, recreate instead of moving it ([venv](https://docs.python.org/3/library/venv.html)).
- Commit a `pylock.toml` lock file for applications and deployments to make installs reproducible; libraries publish ranges, not locks ([pylock.toml spec](https://packaging.python.org/en/latest/specifications/pylock-toml/), [PEP 751](https://peps.python.org/pep-0751/)).
- Replace `import` lines in `.pth` files with `.start` entry-point files when shipping startup hooks (3.15+) ([What's new 3.15](https://docs.python.org/3/whatsnew/3.15.html)).

### Logging

- Create loggers with `logger = logging.getLogger(__name__)`; never log through the root logger in library code ([Logging HOWTO](https://docs.python.org/3/howto/logging.html#configuring-logging-for-a-library)).
- Pass arguments separately (`logger.info("user %s", uid)`), not as f-strings, so formatting is deferred until a record is emitted ([Logging HOWTO](https://docs.python.org/3/howto/logging.html)).
- Guard expensive argument computation with `logger.isEnabledFor(logging.DEBUG)` ([Logging HOWTO](https://docs.python.org/3/howto/logging.html)).
- Libraries attach only `logging.NullHandler()`; configure handlers and levels once at the application entry point ([Logging HOWTO](https://docs.python.org/3/howto/logging.html#configuring-logging-for-a-library)).
- Use `logger.exception(...)` inside `except` blocks to record the traceback ([Logging HOWTO](https://docs.python.org/3/howto/logging.html)).

### Testing

- Write tests with the stdlib `unittest` (`python -m unittest`) or the common third-party `pytest`; follow whichever the project already uses ([unittest](https://docs.python.org/3/library/unittest.html)).
- Keep runnable examples in docstrings verifiable with `doctest` ([doctest](https://docs.python.org/3/library/doctest.html)).
- Run test suites in Python Development Mode (`-X dev`) to enable extra runtime checks and `ResourceWarning`s ([Development mode](https://docs.python.org/3/library/devmode.html)).
- Opt in to `EncodingWarning` with `-X warn_default_encoding` to find `open()` calls that rely on the default encoding ([io](https://docs.python.org/3/library/io.html#io-encoding-warning)).

### Security

- Call `subprocess.run([...], check=True)` with an argument list; avoid `shell=True`, and if a shell is unavoidable, quote every untrusted value with `shlex.quote()` ([subprocess](https://docs.python.org/3/library/subprocess.html#security-considerations), [shlex](https://docs.python.org/3/library/shlex.html)).
- Generate tokens, passwords, and nonces with `secrets`, never `random` ([secrets](https://docs.python.org/3/library/secrets.html)).
- Never unpickle, `eval()`, or `exec()` untrusted data; use `json` for data interchange ([pickle](https://docs.python.org/3/library/pickle.html), [Security considerations](https://docs.python.org/3/library/security_warnings.html)).
- Bind SQL values with placeholders (`cur.execute("... WHERE id = ?", (uid,))`), never string formatting ([sqlite3](https://docs.python.org/3/library/sqlite3.html)).
- Pass `filter="data"` to `tarfile` `extract()`/`extractall()` when supporting 3.13 or lower; it is the default from 3.14, and still extract untrusted archives into a fresh directory ([tarfile](https://docs.python.org/3/library/tarfile.html#extraction-filters)).
- Use t-strings to build SQL, HTML, or shell fragments through a processing function that escapes each interpolation (3.14+); never pass untrusted input through plain f-strings into those sinks ([What's new 3.14](https://docs.python.org/3/whatsnew/3.14.html), [string.templatelib](https://docs.python.org/3/library/string.templatelib.html)).

  ```python
  from html import escape
  from string.templatelib import Interpolation, Template

  def html(t: Template) -> str:
      return "".join(
          escape(str(p.value)) if isinstance(p, Interpolation) else p
          for p in t
      )
  ```

- Use SHA-256 or stronger from `hashlib`; pass `usedforsecurity=False` when MD5/SHA-1 is needed for non-security checksums; hash files with `hashlib.file_digest()` (3.11+) ([hashlib](https://docs.python.org/3/library/hashlib.html)).

### Performance

- Profile before optimizing: use `python -m profiling.sampling run script.py` or `attach PID` for low-overhead sampling (3.15+), and `profiling.tracing`/`cProfile` for deterministic call counts ([profiling.sampling](https://docs.python.org/3/library/profiling.sampling.html), [profiling](https://docs.python.org/3/library/profiling.html)).
- Use `python -m profiling.sampling dump PID` to inspect a hung process (3.15+), or `python -m asyncio pstree PID` for stuck tasks (3.14+) ([What's new 3.15](https://docs.python.org/3/whatsnew/3.15.html), [What's new 3.14](https://docs.python.org/3/whatsnew/3.14.html)).
- Prefer generator expressions and iterators over building intermediate lists when results are consumed once ([Functional programming HOWTO](https://docs.python.org/3/howto/functional.html#generator-expressions-and-list-comprehensions)).
- Memoize pure functions with `functools.cache` (unbounded) or `lru_cache(maxsize=...)`, and per-instance computed attributes with `cached_property` ([functools](https://docs.python.org/3/library/functools.html)).
- Chunk iterables with `itertools.batched(iterable, n)` instead of manual index slicing (3.12+) ([What's new 3.12](https://docs.python.org/3/whatsnew/3.12.html)).
- Import compression codecs from the `compression` package (`compression.gzip`, `compression.zstd`) in code targeting 3.14+; prefer Zstandard for new formats (3.14+) ([What's new 3.14](https://docs.python.org/3/whatsnew/3.14.html)).
- Return `buffer.take_bytes()` instead of `bytes(buffer)` to avoid copying a `bytearray` (3.15+) ([What's new 3.15](https://docs.python.org/3/whatsnew/3.15.html)).

## Examples

Input: "Add a function that downloads several URLs concurrently with a 10 s limit each."
Output: An `async def` using `asyncio.TaskGroup` with `asyncio.timeout(10)` per task, typed `list[str] -> dict[str, bytes]`, no blocking calls in coroutines, `logger = logging.getLogger(__name__)` with %-style args, and a single `asyncio.run(main())` entry point. Rules applied: TaskGroup, timeout, logging, type hints.

Input: "Modernize this module; pyproject says requires-python >= 3.12."
Output: Replace `List`/`Optional`/`TypeVar` with built-in generics, `X | None`, and PEP 695 `def f[T]` / `type` aliases; add `@override` on overrides; keep string forward references (3.12 floor lacks lazy annotations); do not add `lazy` imports, `frozendict`, or `sentinel` (3.15-only); add `encoding="utf-8"` to `open()` calls.

Input: "Review this script that extracts uploaded tarballs and runs `subprocess.run(f'convert {name}', shell=True)`."
Output: Flag shell injection and switch to `subprocess.run(["convert", name], check=True)`; add `filter="data"` to `extractall()` and extract into a new temp directory; replace `random` token generation with `secrets.token_urlsafe()`; cite each rule.

## Edge cases

- Floor below 3.11 (EOL versions such as 3.10): write compatible code (no `TaskGroup`, `except*`, `Self`), and recommend raising `requires-python` since the version receives no security fixes ([Status of Python versions](https://devguide.python.org/versions/)).
- Floor below 3.14 with forward references: keep quoted annotations or `from __future__ import annotations`; the future import stays supported until after 3.13 reaches end of life.
- Floor below 3.15: use `__lazy_modules__` instead of the `lazy` keyword, `MappingProxyType` instead of `frozendict`, and a private `object()` instead of `sentinel`.
- `re.match()` is soft-deprecated in favor of `re.prefixmatch()` (3.15+): use `prefixmatch` only when the floor is 3.15; soft deprecation means no removal, so do not churn existing code.
- Experimental features: the JIT compiler (`PYTHON_JIT=1`) is experimental and not for production; do not enable it or depend on its performance.
- Free-threaded builds (`python3.15t`): supported but optional; confirm every C-extension dependency supports it before recommending it, and check `sys._is_gil_enabled()` at runtime when behavior depends on the GIL.
- Project conventions conflict (line length, quote style, `Optional[...]` enforced by an older linter config): follow the configured tools and suggest updating the config separately.
- Generated code (protobuf/gRPC stubs, Alembic migrations, `_version.py`): do not hand-edit or restyle; change the generator input instead, and exclude the files from formatters.
- Type checker lag: newly added typing features (`TypedDict` `closed`/`extra_items`, `TypeForm`) may not be supported by the project's mypy/pyright version yet; verify before adopting.
- Notebooks and scripts without `pyproject.toml`: use inline script metadata or a `requirements` file the user already has; do not invent a package layout.
- Upgrading to 3.15: removed APIs (for example `typing.ByteString`, `sre_*` modules) and asyncio policy deprecations must be fixed first; consult the porting section of the release notes.
- Libraries spanning several versions: gate version-specific code with `if sys.version_info >= (3, 15):` so type checkers analyze each branch for the right target.
- Third-party async frameworks (Trio, AnyIO): use their structured-concurrency primitives instead of `asyncio.TaskGroup`.

## Resources

- [What's new in Python 3.15](https://docs.python.org/3/whatsnew/3.15.html): read when using or reviewing any 3.15 feature or porting code.
- [What's new in Python 3.14](https://docs.python.org/3/whatsnew/3.14.html): read for t-strings, lazy annotations, `concurrent.interpreters`, and tarfile defaults.
- [Status of Python versions](https://devguide.python.org/versions/): read when choosing or validating a `requires-python` floor.
- [PEP 8](https://peps.python.org/pep-0008/): read when resolving style or naming questions.
- [typing module](https://docs.python.org/3/library/typing.html): read when choosing typing constructs and their minimum versions.
- [Typing best practices](https://typing.python.org/en/latest/reference/best_practices.html): read when annotating public APIs.
- [Coroutines and tasks](https://docs.python.org/3/library/asyncio-task.html): read when writing asyncio code.
- [Logging HOWTO](https://docs.python.org/3/howto/logging.html): read when adding or configuring logging.
- [Writing pyproject.toml](https://packaging.python.org/en/latest/guides/writing-pyproject-toml/): read when creating or editing project metadata.
- [Security considerations](https://docs.python.org/3/library/security_warnings.html): read when reviewing code that handles untrusted input.
- [Annotations best practices](https://docs.python.org/3/howto/annotations.html): read when code introspects annotations at runtime.
- [Free threading HOWTO](https://docs.python.org/3/howto/free-threading-python.html): read before writing threaded code for free-threaded builds.
