---
name: csharp-best-practices
description: "Applies current, officially sourced C# 15 / .NET 11 best practices (with .NET 10 LTS as the baseline) to writing, reviewing, and modernizing C# code and .NET projects. Use when the user asks to write, review, refactor, or upgrade C# code, mentions .NET, C#, csproj, NuGet, async/await, nullable reference types, records, or unions, or works with *.cs, *.csproj, Directory.Build.props, Directory.Packages.props, or global.json files."
license: MIT
---

# C# 15 (.NET 11) best practices

Produces idiomatic, safe, and analyzer-clean C# for the latest release, C# 15 on .NET 11 (STS, GA November 10, 2026), while keeping code compatible with the project's actual target, typically .NET 10 LTS (C# 14).

## Steps

1. Detect the target: read `<TargetFramework>`/`<TargetFrameworks>`, `<LangVersion>`, `<Nullable>`, `<ImplicitUsings>`, `<TreatWarningsAsErrors>`, and `<AnalysisLevel>` in `*.csproj` and `Directory.Build.props`; package versions in `Directory.Packages.props`; the SDK pin in `global.json`; and style rules in `.editorconfig`. The default C# version follows the TFM: `net11.0` is C# 15, `net10.0` is C# 14.
2. Apply the practices below; use version-gated features only when the effective language version and runtime support them, otherwise keep compatible code and optionally suggest upgrading the TFM.
3. Follow existing `.editorconfig`, analyzer configuration, and project conventions when they conflict with a non-safety rule; never relax nullable, security, or async-safety rules to match legacy code.
4. Run `dotnet format --verify-no-changes`, `dotnet build` (warnings are findings, not noise), `dotnet test`, and `dotnet package list --vulnerable`; fix what they report before finishing.

## Best practices

### Style and naming

- Use PascalCase for types, namespaces, public members, and constants; camelCase for parameters and locals; `_camelCase` for private instance fields; prefix interfaces with `I` ([Identifier names](https://learn.microsoft.com/en-us/dotnet/csharp/fundamentals/coding-style/identifier-names)).
- Suffix asynchronous methods with `Async` ([Async scenarios](https://learn.microsoft.com/en-us/dotnet/csharp/asynchronous-programming/async-scenarios)).
- Use file-scoped namespaces and place `using` directives outside the namespace ([Coding conventions](https://learn.microsoft.com/en-us/dotnet/csharp/fundamentals/coding-style/coding-conventions)).
- Use `var` only when the type is obvious from the right side (`new`, cast, literal); never infer it from a method name ([Coding conventions](https://learn.microsoft.com/en-us/dotnet/csharp/fundamentals/coding-style/coding-conventions)).
- Use language keywords (`string`, `int`) instead of runtime type names, and prefer `int` over unsigned types unless the domain requires them ([Coding conventions](https://learn.microsoft.com/en-us/dotnet/csharp/fundamentals/coding-style/coding-conventions)).
- Prefer raw string literals over escape sequences or verbatim strings for multi-line or quote-heavy text; use string interpolation for short concatenations and `StringBuilder` in loops ([Coding conventions](https://learn.microsoft.com/en-us/dotnet/csharp/fundamentals/coding-style/coding-conventions)).
- Use `Func<>`/`Action<>` instead of declaring custom delegate types ([Coding conventions](https://learn.microsoft.com/en-us/dotnet/csharp/fundamentals/coding-style/coding-conventions)).
- Encode style preferences in `.editorconfig` and enforce them in the build with `<EnforceCodeStyleInBuild>true</EnforceCodeStyleInBuild>` ([Code style rule options](https://learn.microsoft.com/en-us/dotnet/fundamentals/code-analysis/code-style-rule-options), [Code analysis](https://learn.microsoft.com/en-us/dotnet/fundamentals/code-analysis/overview)).

### Types and data modeling

- Enable nullable reference types (`<Nullable>enable</Nullable>`), annotate intent with `?`, and fix warnings instead of silencing them with `!` ([Nullable reference types](https://learn.microsoft.com/en-us/dotnet/csharp/nullable-references)).
- Use `record` types for data whose identity is its values; they provide value equality, `ToString`, and `with` expressions ([Records](https://learn.microsoft.com/en-us/dotnet/csharp/fundamentals/types/records)).
- Use `required` properties to force initialization through object initializers instead of long constructors ([required](https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/keywords/required), [Coding conventions](https://learn.microsoft.com/en-us/dotnet/csharp/fundamentals/coding-style/coding-conventions)).
- Use primary constructors for classes that only need injected dependencies; remember the parameters stay assignable, so copy them into `readonly` fields or properties when immutability matters (12+) ([Primary constructors tutorial](https://learn.microsoft.com/en-us/dotnet/csharp/whats-new/tutorials/primary-constructors), [Instance constructors](https://learn.microsoft.com/en-us/dotnet/csharp/programming-guide/classes-and-structs/instance-constructors)).

  ```csharp
  public sealed class OrderService(IOrderRepository repository)
  {
      private readonly IOrderRepository _repository = repository;
  }
  ```

- Name primary constructor parameters in PascalCase on records and camelCase on classes and structs ([Coding conventions](https://learn.microsoft.com/en-us/dotnet/csharp/fundamentals/coding-style/coding-conventions)).
- Use the `field` keyword for properties that need validation or normalization in one accessor instead of declaring a manual backing field (14+) ([What's new in C# 14](https://learn.microsoft.com/en-us/dotnet/csharp/whats-new/csharp-14), [field keyword](https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/keywords/field)).

  ```csharp
  public string Name
  {
      get;
      set => field = value ?? throw new ArgumentNullException(nameof(value));
  }
  ```

- Declare a `union` when a value is exactly one of a fixed set of existing types, such as result-or-error returns or message dispatch; the compiler adds implicit conversions and checks `switch` exhaustiveness (15+, requires the .NET 11 runtime) ([Union types](https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/builtin-types/union), [What's new in C# 15](https://learn.microsoft.com/en-us/dotnet/csharp/whats-new/csharp-15)).

  ```csharp
  public union LookupResult(Product, NotFound);

  string Describe(LookupResult r) => r switch
  {
      Product p => p.Name,
      NotFound => "missing",
  };
  ```

- Mark a base class `closed` when you own the hierarchy and want exhaustive `switch` expressions without a discard arm; mark intermediate descendants `closed` too, because the restriction is not transitive (15+) ([closed modifier](https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/keywords/closed)).
- Prefer a union to compose types you do not own, and a closed hierarchy when you control the inheritance relationship ([Announcing .NET 11](https://devblogs.microsoft.com/dotnet/announcing-dotnet-11/)).
- Group related extensions in an `extension(...)` block to declare extension properties, static extension members, and operators (14+) ([Extension members](https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/keywords/extension)).
- Convert existing `this`-parameter extension methods to block syntax freely; both forms are binary and source compatible (14+) ([Extension members](https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/keywords/extension)).

  ```csharp
  public static class SequenceExtensions
  {
      extension<T>(IEnumerable<T> source)
      {
          public bool IsEmpty => !source.Any();
      }
  }
  ```

- Declare extension indexers in an extension block with a named receiver when a type needs indexing it does not own (15+) ([What's new in C# 15](https://learn.microsoft.com/en-us/dotnet/csharp/whats-new/csharp-15)).

### Pattern matching and control flow

- Use `switch` expressions with property, positional, relational, and list patterns instead of chained `if`/`is` casts ([Pattern matching](https://learn.microsoft.com/en-us/dotnet/csharp/fundamentals/functional/pattern-matching)).
- Test the contents of a union with type patterns and `is not null`; do not write `pet is Pet` (compile error) and remember an untyped `{ }` pattern tests the union instance, not its value (15+) ([Union types](https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/builtin-types/union)).
- Use `&&` and `||` (short-circuit) for conditions, never `&`/`|` on booleans ([Coding conventions](https://learn.microsoft.com/en-us/dotnet/csharp/fundamentals/coding-style/coding-conventions)).
- Replace Boolean exit flags and `goto` in nested loops with labeled `break`/`continue` (15+) ([What's new in C# 15](https://learn.microsoft.com/en-us/dotnet/csharp/whats-new/csharp-15)).

  ```csharp
  outer: foreach (var row in grid)
  {
      foreach (var cell in row)
      {
          if (cell.IsGoal) break outer;
      }
  }
  ```

- Use null-conditional assignment instead of an `if (x is not null)` guard around a single assignment; the right side is evaluated only when the target is non-null (14+) ([What's new in C# 14](https://learn.microsoft.com/en-us/dotnet/csharp/whats-new/csharp-14)).

  ```csharp
  customer?.Order = GetCurrentOrder();
  ```

### Collections and LINQ

- Initialize collections with collection expressions and spread elements (`[]`, `[a, .. rest]`) (12+) ([Collection expressions](https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/operators/collection-expressions), [Coding conventions](https://learn.microsoft.com/en-us/dotnet/csharp/fundamentals/coding-style/coding-conventions)).
- Pass capacity or comparers with a leading `with(...)` element instead of falling back to constructor syntax (15+) ([What's new in C# 15](https://learn.microsoft.com/en-us/dotnet/csharp/whats-new/csharp-15)).

  ```csharp
  HashSet<string> tags = [with(StringComparer.OrdinalIgnoreCase), .. input];
  List<Order> buffer = [with(capacity: count)];
  ```

- Materialize a LINQ query with `ToList`/`ToArray` before enumerating it more than once; deferred execution reruns the query each time ([CA1851](https://learn.microsoft.com/en-us/dotnet/fundamentals/code-analysis/quality-rules/ca1851)).
- Keep `IQueryable<T>` typed until the query is complete; switching to `IEnumerable<T>` moves filtering from the database into memory ([Coding conventions](https://learn.microsoft.com/en-us/dotnet/csharp/fundamentals/coding-style/coding-conventions)).
- Use `FrozenDictionary`/`FrozenSet` for lookup tables built once (for example at startup) and read many times; construction is expensive, so never use them for frequently rebuilt data ([FrozenDictionary](https://learn.microsoft.com/en-us/dotnet/api/system.collections.frozen.frozendictionary-2)).
- Pass an explicit `StringComparison` (usually `Ordinal` or `OrdinalIgnoreCase`) to string comparison, search, and equality methods ([String comparison best practices](https://learn.microsoft.com/en-us/dotnet/standard/base-types/best-practices-strings)).

### Async and concurrency

- Use `async`/`await` for I/O-bound work and `Task.Run` only for CPU-bound work, never to wrap I/O ([Async scenarios](https://learn.microsoft.com/en-us/dotnet/csharp/asynchronous-programming/async-scenarios)).
- Go async all the way; never block with `.Result`, `.Wait()`, or `GetAwaiter().GetResult()` in request or UI paths, which causes deadlocks and thread-pool starvation ([ASP.NET Core best practices](https://learn.microsoft.com/en-us/aspnet/core/fundamentals/best-practices), [Async scenarios](https://learn.microsoft.com/en-us/dotnet/csharp/asynchronous-programming/async-scenarios)).
- Return `Task`/`Task<T>`; use `async void` only for event handlers, because its exceptions cannot be caught by callers ([Async scenarios](https://learn.microsoft.com/en-us/dotnet/csharp/asynchronous-programming/async-scenarios)).
- Accept a `CancellationToken` in async APIs and pass it to every downstream call ([TAP implementation](https://learn.microsoft.com/en-us/dotnet/standard/asynchronous-programming-patterns/implementing-the-task-based-asynchronous-pattern)).

  ```csharp
  public async Task<Order?> FindAsync(int id, CancellationToken cancellationToken = default)
  {
      using HttpResponseMessage response = await _http.GetAsync($"orders/{id}", cancellationToken);
      return await response.Content.ReadFromJsonAsync<Order>(cancellationToken);
  }
  ```

- Use `ConfigureAwait(false)` in general-purpose library code; omit it in app code that needs its context (UI) ([ConfigureAwait FAQ](https://devblogs.microsoft.com/dotnet/configureawait-faq/)).
- Default to `Task<T>`; return `ValueTask<T>` only when profiling proves it helps, and never await a `ValueTask` more than once ([ValueTask<TResult>](https://learn.microsoft.com/en-us/dotnet/api/system.threading.tasks.valuetask-1)).
- Start independent operations first and await them together with `Task.WhenAll`; when projecting tasks with LINQ, materialize with `ToArray`/`ToList` so they actually start ([Async scenarios](https://learn.microsoft.com/en-us/dotnet/csharp/asynchronous-programming/async-scenarios)).
- Stream large or paged results as `IAsyncEnumerable<T>` with `await foreach`, marking the token parameter `[EnumeratorCancellation]` and passing tokens via `WithCancellation` ([Async streams](https://learn.microsoft.com/en-us/dotnet/csharp/asynchronous-programming/generate-consume-asynchronous-stream)).
- Lock on a dedicated `private readonly Lock _gate = new();` instead of `object` or `this` (13+, .NET 9+) ([lock statement](https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/statements/lock)).
- Never access `HttpContext` from multiple threads in parallel; copy the needed values first ([ASP.NET Core best practices](https://learn.microsoft.com/en-us/aspnet/core/fundamentals/best-practices)).

### Errors and exceptions

- Validate arguments with throw helpers such as `ArgumentNullException.ThrowIfNull`, `ArgumentException.ThrowIfNullOrWhiteSpace`, and `ArgumentOutOfRangeException.ThrowIfZero` ([Exception best practices](https://learn.microsoft.com/en-us/dotnet/standard/exceptions/best-practices-for-exceptions), [ThrowIfNull](https://learn.microsoft.com/en-us/dotnet/api/system.argumentnullexception.throwifnull)).
- Catch only exceptions you can handle, most-derived first; never catch `System.Exception` without an exception filter ([Coding conventions](https://learn.microsoft.com/en-us/dotnet/csharp/fundamentals/coding-style/coding-conventions), [Exception best practices](https://learn.microsoft.com/en-us/dotnet/standard/exceptions/best-practices-for-exceptions)).

  ```csharp
  catch (HttpRequestException ex) when (ex.StatusCode == HttpStatusCode.NotFound)
  {
      return null;
  }
  ```

- Rethrow with `throw;`, not `throw ex;`, to keep the stack trace (CA2200) ([Exception best practices](https://learn.microsoft.com/en-us/dotnet/standard/exceptions/best-practices-for-exceptions)).
- Use `Try*` methods (`int.TryParse`, `TryGetValue`) for expected failures instead of exception-driven control flow ([Exception best practices](https://learn.microsoft.com/en-us/dotnet/standard/exceptions/best-practices-for-exceptions)).
- Throw predefined exception types with meaningful messages and never throw from `finally` blocks ([Exception best practices](https://learn.microsoft.com/en-us/dotnet/standard/exceptions/best-practices-for-exceptions)).

### Resources and disposal

- Dispose `IDisposable` objects with `using` declarations or statements instead of `try`/`finally` ([Coding conventions](https://learn.microsoft.com/en-us/dotnet/csharp/fundamentals/coding-style/coding-conventions), [Exception best practices](https://learn.microsoft.com/en-us/dotnet/standard/exceptions/best-practices-for-exceptions)).
- Use `await using` for `IAsyncDisposable` resources; implement both `IDisposable` and `IAsyncDisposable` when a type owns both kinds ([Implement DisposeAsync](https://learn.microsoft.com/en-us/dotnet/standard/garbage-collection/implementing-disposeasync)).
- Make `Dispose` idempotent and follow the standard pattern (`Dispose(bool)`, `GC.SuppressFinalize(this)`); wrap unmanaged handles in `SafeHandle` rather than writing finalizers ([Implement Dispose](https://learn.microsoft.com/en-us/dotnet/standard/garbage-collection/implementing-dispose)).
- Obtain `HttpClient` from `IHttpClientFactory` instead of creating and disposing instances per call, which exhausts sockets ([ASP.NET Core best practices](https://learn.microsoft.com/en-us/aspnet/core/fundamentals/best-practices)).
- Dispose or transfer ownership of every `IMemoryOwner<T>`, and never use a `Memory<T>` argument after the method or its task completes ([Memory<T> and Span<T> guidelines](https://learn.microsoft.com/en-us/dotnet/standard/memory-and-spans/memory-t-usage-guidelines)).

### Dependency injection, configuration, and logging

- Inject dependencies through constructors; avoid the service locator pattern, static service access, and calling `BuildServiceProvider` during registration ([DI guidelines](https://learn.microsoft.com/en-us/dotnet/core/extensions/dependency-injection/guidelines)).
- Enable scope validation so singletons cannot capture scoped services ([DI guidelines](https://learn.microsoft.com/en-us/dotnet/core/extensions/dependency-injection/guidelines)).
- Bind settings to strongly typed options classes, validate them, and call `ValidateOnStart` to fail fast on bad configuration ([Options pattern](https://learn.microsoft.com/en-us/dotnet/core/extensions/options)).

  ```csharp
  services.AddOptions<SmtpOptions>()
      .Bind(configuration.GetSection("Smtp"))
      .ValidateDataAnnotations()
      .ValidateOnStart();
  ```

- Inject `TimeProvider` instead of reading `DateTime.Now`/`UtcNow` directly, and use `FakeTimeProvider` in tests ([TimeProvider](https://learn.microsoft.com/en-us/dotnet/standard/datetime/timeprovider-overview)).
- Log with message templates and named placeholders, never string interpolation, so providers can store structured values ([Logging](https://learn.microsoft.com/en-us/dotnet/core/extensions/logging)).
- Use `[LoggerMessage]` on `static partial` or instance `partial` methods for hot-path logging; the source generator avoids boxing and allocations ([LoggerMessage generator](https://learn.microsoft.com/en-us/dotnet/core/extensions/logger-message-generator)).

  ```csharp
  [LoggerMessage(Level = LogLevel.Warning, Message = "Order {OrderId} rejected")]
  static partial void OrderRejected(ILogger logger, int orderId);
  ```

### Performance and source generation

- Accept `Span<T>`/`ReadOnlySpan<T>` in synchronous APIs and `Memory<T>`/`ReadOnlyMemory<T>` in async ones; use the read-only form when the buffer is not written ([Memory<T> and Span<T> guidelines](https://learn.microsoft.com/en-us/dotnet/standard/memory-and-spans/memory-t-usage-guidelines)).
- Write helpers and extension methods over `ReadOnlySpan<T>`/`Span<T>`; C# 14 converts arrays and spans implicitly, including for extension receivers and generic inference (14+) ([What's new in C# 14](https://learn.microsoft.com/en-us/dotnet/csharp/whats-new/csharp-14)).
- Use `System.Text.Json` source generation (`JsonSerializerContext` with `[JsonSerializable]`) for hot paths, trimming, and Native AOT ([JSON source generation](https://learn.microsoft.com/en-us/dotnet/standard/serialization/system-text-json/source-generation)).
- Use `[GeneratedRegex]` on a `partial` method or property instead of constructing `Regex` at run time ([Regex source generators](https://learn.microsoft.com/en-us/dotnet/standard/base-types/regular-expression-source-generators)).
- Return async results with `ToListAsync` (or stream them) rather than synchronously enumerated `IEnumerable<T>`, and use no-tracking EF Core queries for read-only data ([ASP.NET Core best practices](https://learn.microsoft.com/en-us/aspnet/core/fundamentals/best-practices)).

### Project settings and dependencies

- Do not set `<LangVersion>latest</LangVersion>`; let the TFM pick the language version, and never select a language version newer than the TFM supports ([Configure language version](https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/configure-language-version)).
- Put shared properties (`Nullable`, `TreatWarningsAsErrors`, `AnalysisLevel`) in `Directory.Build.props` ([Configure language version](https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/configure-language-version)).
- Enable `TreatWarningsAsErrors` for new projects and raise analyzer coverage with `<AnalysisLevel>latest-Recommended</AnalysisLevel>`; pin a numeric `AnalysisLevel` if SDK upgrades must not add warnings ([Code analysis](https://learn.microsoft.com/en-us/dotnet/fundamentals/code-analysis/overview), [Errors and warnings options](https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/compiler-options/errors-warnings)).
- Manage versions centrally with `Directory.Packages.props` and `<ManagePackageVersionsCentrally>true</ManagePackageVersionsCentrally>`; keep `Version` off `PackageReference` items ([Central Package Management](https://learn.microsoft.com/en-us/nuget/consume-packages/central-package-management)).

  ```xml
  <Project>
    <PropertyGroup>
      <ManagePackageVersionsCentrally>true</ManagePackageVersionsCentrally>
    </PropertyGroup>
    <ItemGroup>
      <PackageVersion Include="PackageA" Version="1.0.0" />
    </ItemGroup>
  </Project>
  ```

- Keep NuGet Audit on; it audits transitive packages by default for `net10.0`+ targets. If all warnings are errors, list `NU1901`-`NU1904` in `WarningsNotAsErrors` so new advisories don't break unrelated builds, and fix with `dotnet package update --vulnerable` (10+) ([NuGet auditing](https://learn.microsoft.com/en-us/nuget/concepts/auditing-packages)).
- Enable `RestorePackagesWithLockFile` and restore with `--locked-mode` in CI for reproducible dependency graphs ([PackageReference in project files](https://learn.microsoft.com/en-us/nuget/consume-packages/package-references-in-project-files)).
- Pin the SDK in `global.json` with a `rollForward` policy (for example `latestFeature`) for consistent CI builds ([global.json](https://learn.microsoft.com/en-us/dotnet/core/tools/global-json)).

### Testing

- Name tests after the method under test, the scenario, and the expected behavior, and structure them as Arrange-Act-Assert with a single Act ([Unit testing best practices](https://learn.microsoft.com/en-us/dotnet/core/testing/unit-testing-best-practices)).
- Keep unit tests free of infrastructure (databases, file system, network) and logic such as loops or conditionals; test private behavior through public methods ([Unit testing best practices](https://learn.microsoft.com/en-us/dotnet/core/testing/unit-testing-best-practices)).
- Use the project's existing framework (MSTest, NUnit, TUnit, or xUnit.net) and run it with `dotnet test` ([Testing in .NET](https://learn.microsoft.com/en-us/dotnet/core/testing/)).

### Security

- Pass user input to SQL only as parameters; in EF Core use `FromSql`/`FromSqlInterpolated`, and never build `FromSqlRaw` strings by concatenation ([EF Core SQL queries](https://learn.microsoft.com/en-us/ef/core/querying/sql-queries)).
- Never use `BinaryFormatter` or related formatters; it throws on .NET 9+ and cannot be made safe ([BinaryFormatter security guide](https://learn.microsoft.com/en-us/dotnet/standard/serialization/binaryformatter-security-guide), [Secure coding guidelines](https://learn.microsoft.com/en-us/dotnet/standard/security/secure-coding-guidelines)).
- Do not rely on Code Access Security, partial trust, .NET Remoting, or DCOM as security boundaries ([Secure coding guidelines](https://learn.microsoft.com/en-us/dotnet/standard/security/secure-coding-guidelines)).
- Use `RandomNumberGenerator` for tokens, keys, and passwords; `System.Random` is not cryptographically secure ([Random class](https://learn.microsoft.com/en-us/dotnet/fundamentals/runtime-libraries/system-random)).
- Keep secrets out of source and `appsettings.json`; use `dotnet user-secrets` in development and a managed store such as Azure Key Vault in production ([App secrets](https://learn.microsoft.com/en-us/aspnet/core/security/app-secrets)).
- Avoid reading entire large request or response bodies into memory, which enables denial of service ([ASP.NET Core best practices](https://learn.microsoft.com/en-us/aspnet/core/fundamentals/best-practices)).
- Initialize `FrozenDictionary`/`FrozenSet` only with trusted keys, because key contents affect construction time ([FrozenDictionary](https://learn.microsoft.com/en-us/dotnet/api/system.collections.frozen.frozendictionary-2)).

## Examples

Input: "Review this ASP.NET Core service method that calls `_repo.GetOrdersAsync().Result` and logs with `$\"Loaded {count} orders\"`."
Output: The method rewritten as `async Task<IReadOnlyList<Order>> GetOrdersAsync(CancellationToken ct)` that awaits the repository and forwards `ct`, plus a `[LoggerMessage]` method with an `{Count}` placeholder; review notes cite async-all-the-way, cancellation propagation, and structured logging.

Input: "Model a payment result that is either `Approved`, `Declined`, or `Failed` in our `net11.0` project."
Output: Three `record` case types and `public union PaymentResult(Approved, Declined, Failed);` with an exhaustive `switch` expression and no discard arm (C# 15 unions). For a `net10.0` target, the agent instead uses an abstract base record with a `switch` that includes a discard arm and notes unions need .NET 11.

Input: "Modernize this `net10.0` class library's project setup."
Output: `Directory.Build.props` with `Nullable`, `TreatWarningsAsErrors`, and `AnalysisLevel` set to `latest-Recommended`; `Directory.Packages.props` with Central Package Management; lock files enabled; `NU1901`-`NU1904` excluded from warnings-as-errors; `global.json` pinning the SDK; library code using `ConfigureAwait(false)`, file-scoped namespaces, collection expressions, and `field`-backed properties (C# 14), with no C# 15 syntax.

## Edge cases

- Target is `net10.0` (C# 14) or older: do not use unions, closed hierarchies, collection expression arguments, extension indexers, or labeled `break`/`continue`; suggest moving to `net11.0` only if the team accepts STS support (two years) over LTS (three years).
- Target is .NET Framework or `netstandard2.0`: the language version is tied to the TFM and raising `LangVersion` beyond it is unsupported ([Configure language version](https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/configure-language-version)); avoid features needing runtime types (`Lock`, unions), keep `object`-based locks, and get `TimeProvider` from the `Microsoft.Bcl.TimeProvider` package ([TimeProvider](https://learn.microsoft.com/en-us/dotnet/standard/datetime/timeprovider-overview)).
- Multi-targeted libraries (`<TargetFrameworks>`): write to the lowest target's language and API level or guard newer APIs with symbols such as `NET11_0_OR_GREATER` ([Preprocessor directives](https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/preprocessor-directives)).
- Memory safety rules (`unsafe` expressions, pointer relaxations, `updated-memory-safety-rules`) are a C# 15 preview feature requiring `<LangVersion>preview</LangVersion>`: never use them in production code unless the project already opts in to preview.
- Runtime Async is enabled by default for `net11.0` with no code changes; do not add `EnablePreviewFeatures` for it, and expect different async stack traces when diagnosing.
- An identifier named `field` inside a property accessor now binds to the keyword in C# 14+: rename it or use `@field`/`this.field`.
- Existing `.editorconfig` mandates `s_` static field prefixes, block-scoped namespaces, or explicit types: follow the file; it overrides the defaults above for style-only rules.
- Generated code (`*.g.cs`, `*.Designer.cs`, source generator output, EF migrations): do not hand-edit or reformat; change the generator input instead.
- `TreatWarningsAsErrors` would break a large legacy solution: enable it per project or fix warnings incrementally rather than adding blanket `NoWarn` entries.
- Library consumed by UI frameworks with a synchronization context: keep `ConfigureAwait(false)` throughout library code; in app-level UI code, omit it where the continuation touches UI state.
- Hot paths where profiling shows `Task<T>` allocations matter: switch to `ValueTask<T>` and document that callers must await once and not cache it.

## Resources

- [What's new in C# 15](https://learn.microsoft.com/en-us/dotnet/csharp/whats-new/csharp-15): read when using unions, closed hierarchies, collection expression arguments, extension indexers, or labeled jumps.
- [What's new in C# 14](https://learn.microsoft.com/en-us/dotnet/csharp/whats-new/csharp-14): read when targeting the .NET 10 LTS baseline.
- [The history of C#](https://learn.microsoft.com/en-us/dotnet/csharp/whats-new/csharp-version-history): read when checking which version introduced a feature.
- [.NET support policy](https://dotnet.microsoft.com/en-us/platform/support/policy/dotnet-core): read when choosing between LTS and STS targets or checking end-of-support dates.
- [C# coding conventions](https://learn.microsoft.com/en-us/dotnet/csharp/fundamentals/coding-style/coding-conventions): read when settling style questions.
- [Identifier names](https://learn.microsoft.com/en-us/dotnet/csharp/fundamentals/coding-style/identifier-names): read when naming types, members, and fields.
- [Framework Design Guidelines](https://learn.microsoft.com/en-us/dotnet/standard/design-guidelines/): read when designing public library APIs.
- [Asynchronous programming scenarios](https://learn.microsoft.com/en-us/dotnet/csharp/asynchronous-programming/async-scenarios): read when writing or reviewing async code.
- [Best practices for exceptions](https://learn.microsoft.com/en-us/dotnet/standard/exceptions/best-practices-for-exceptions): read when designing error handling.
- [Code analysis in .NET](https://learn.microsoft.com/en-us/dotnet/fundamentals/code-analysis/overview): read when configuring analyzers, `AnalysisLevel`, or build-time style enforcement.
- [Auditing package dependencies](https://learn.microsoft.com/en-us/nuget/concepts/auditing-packages): read when handling NuGet vulnerability warnings.
- [Unit testing best practices](https://learn.microsoft.com/en-us/dotnet/core/testing/unit-testing-best-practices): read when writing or reviewing tests.
