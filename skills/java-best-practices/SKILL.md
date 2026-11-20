---
name: java-best-practices
description: "Applies current, officially sourced Java (JDK 27, LTS 25) best practices to write, review, and modernize Java code. Use when the user asks to write, review, refactor, or upgrade Java code, mentions JDK versions, records, sealed types, pattern matching, virtual threads, or Javadoc, or works with .java files, pom.xml, or build.gradle(.kts)."
license: MIT
---

# Java 27 best practices

Produces idiomatic, safe, version-correct Java for JDK 27 (GA 2026-09-15), while staying compatible with the LTS release the project actually targets (JDK 25 is the latest LTS; many projects still target JDK 21 or 17).

## Steps

1. Detect the target release: `maven.compiler.release` or the `maven-compiler-plugin` `<release>` in `pom.xml`; `java { toolchain { languageVersion = JavaLanguageVersion.of(N) } }`, `options.release`, or `sourceCompatibility` in `build.gradle(.kts)`; `.java-version`, `.sdkmanrc`, `.tool-versions`, or the CI JDK setup; and any `--enable-preview` in compiler/test/runtime args.
2. Apply the practices below; use a version-tagged feature only when the target release is at or above the tag, otherwise write the compatible form (and optionally suggest upgrading to JDK 25 LTS).
3. Follow the project's existing conventions and tool configs (Checkstyle, Spotless, Error Prone, logging framework, test framework) when they conflict with a non-safety rule; never relax a security or correctness rule for style.
4. Treat code that relies on preview features as pinned to one exact JDK release; do not introduce preview features unless the project already enables them.
5. Run the build's formatter, compiler with lint warnings, static analysis, and tests: `./mvnw verify` or `./gradlew check` (fall back to `mvn`/`gradle`), and fix new `-Xlint` warnings.

## Best practices

### Style and naming

- Name packages in lowercase reverse-domain form, types in UpperCamelCase nouns, methods in lowerCamelCase verbs, and constants in UPPER_SNAKE_CASE ([JLS 6.1](https://docs.oracle.com/javase/specs/jls/se27/html/jls-6.html#jls-6.1)).
- Use `var` only when the initializer makes the type obvious (constructor or well-named factory); keep explicit types when the reader would otherwise need an IDE (10+) ([LVTI style guide](https://openjdk.org/projects/amber/guides/lvti-style-guide)).
- Keep the scope of `var` locals small and give them descriptive names, since the name now carries the type information ([LVTI G1/G2](https://openjdk.org/projects/amber/guides/lvti-style-guide#G2)).
- Never combine `var` with diamond or argument-less generic factories (`var list = new ArrayList<>()` infers `ArrayList<Object>`) ([LVTI G6](https://openjdk.org/projects/amber/guides/lvti-style-guide#G6)).
- Avoid `var` with integer literals meant to be `byte`, `short`, or `long`; they infer `int` ([LVTI G7](https://openjdk.org/projects/amber/guides/lvti-style-guide#G7)).
- Use text blocks for multi-line SQL, JSON, HTML, and similar literals instead of concatenation (15+) ([Text blocks guide](https://docs.oracle.com/en/java/javase/27/language/text-blocks.html)).
- Use `_` for variables and pattern components that are intentionally unused (catch parameters, lambda parameters, record pattern parts) (22+) ([JEP 456](https://openjdk.org/jeps/456)).

```java
try { Integer.parseInt(s); return true; }
catch (NumberFormatException _) { return false; }
map.forEach((_, value) -> process(value));
```

### Data modeling: records, sealed types, immutability

- Model plain immutable data carriers as records; they get canonical constructor, accessors, `equals`, `hashCode`, and `toString` for free (16+) ([Record classes](https://docs.oracle.com/en/java/javase/27/language/records.html)).
- Validate and normalize record state in a compact constructor; records are only shallowly immutable, so defensively copy mutable components (for example `List.copyOf`) (16+) ([Record API](https://docs.oracle.com/en/java/javase/27/docs/api/java.base/java/lang/Record.html), [Secure Coding 6-3](https://www.oracle.com/java/technologies/javase/seccodeguide.html)).

```java
record Order(String id, List<Line> lines) {
    Order {
        Objects.requireNonNull(id, "id");
        lines = List.copyOf(lines); // unmodifiable, rejects nulls
    }
}
```

- Use `sealed` interfaces or classes with an explicit `permits` list for closed hierarchies so `switch` can be checked for exhaustiveness (17+) ([Sealed classes guide](https://docs.oracle.com/en/java/javase/27/language/sealed-classes-interfaces.html)).
- Prefer immutable value types; make fields `private final` and do not expose internal mutable state ([Secure Coding 6-1](https://www.oracle.com/java/technologies/javase/seccodeguide.html)).
- Return unmodifiable collections or copies from accessors, never the internal mutable collection ([Secure Coding 6-12](https://www.oracle.com/java/technologies/javase/seccodeguide.html)).
- Validate arguments before calling `super(...)`/`this(...)` and initialize fields there instead of using static helper methods (25+) ([JEP 513](https://openjdk.org/jeps/513), [Flexible constructor bodies guide](https://docs.oracle.com/en/java/javase/27/language/flexible-constructor-bodies.html)).

```java
class PositiveBig extends BigInteger {
    PositiveBig(long value) {
        if (value <= 0) throw new IllegalArgumentException("non-positive: " + value);
        super(Long.toString(value));
    }
}
```

- Never call overridable methods from constructors; a subclass may observe a partially initialized object ([Secure Coding 7-4](https://www.oracle.com/java/technologies/javase/seccodeguide.html)).
- Give classes, members, and fields the smallest accessibility that works, and make classes `final` (or sealed) unless designed for extension ([Secure Coding 4-1, 4-5](https://www.oracle.com/java/technologies/javase/seccodeguide.html)).
- Make `public static` fields `final` and hold only true constants; never expose mutable statics such as arrays ([Secure Coding 6-9, 6-10, 6-11](https://www.oracle.com/java/technologies/javase/seccodeguide.html)).

### Pattern matching and switch

- Use pattern matching for `instanceof` instead of a test followed by a cast (16+) ([JEP 394](https://openjdk.org/jeps/394)).
- Use arrow-form `switch` expressions to compute values; they do not fall through and must be exhaustive (14+) ([Switch guide](https://docs.oracle.com/en/java/javase/27/language/switch-expressions-statements.html)).
- Switch over sealed hierarchies with type and record patterns and omit `default`, so adding a subtype becomes a compile error instead of a silent fallthrough (21+) ([JEP 441](https://openjdk.org/jeps/441), [JEP 440](https://openjdk.org/jeps/440)).

```java
sealed interface Shape permits Circle, Square {}
record Circle(double r) implements Shape {}
record Square(double side) implements Shape {}

static double area(Shape s) {
    return switch (s) {
        case Circle(var r) -> Math.PI * r * r;
        case Square(var side) -> side * side;
    };
}
```

- Use `when` guards for conditions on a pattern rather than nested `if` inside the case body (21+) ([Pattern matching for switch guide](https://docs.oracle.com/en/java/javase/27/language/pattern-matching-switch.html)).
- Handle `null` explicitly with `case null` when the selector can be null; otherwise a pattern `switch` throws `NullPointerException` (21+) ([JEP 441](https://openjdk.org/jeps/441)).
- Use nested record patterns to destructure only as deep as the logic needs (21+) ([Record patterns guide](https://docs.oracle.com/en/java/javase/27/language/record-patterns.html)).

### Collections and streams

- Create fixed collections with `List.of`, `Set.of`, `Map.of`, and copies with `List.copyOf`; they are unmodifiable and reject `null` (10+) ([Unmodifiable collections guide](https://docs.oracle.com/en/java/javase/27/core/creating-immutable-lists-sets-and-maps.html)).
- Do not rely on the iteration order of `Set.of`/`Map.of`; it is randomized ([Unmodifiable collections guide](https://docs.oracle.com/en/java/javase/27/core/creating-immutable-lists-sets-and-maps.html)).
- Use `Stream.toList()` for an unmodifiable result instead of `collect(Collectors.toList())` when no mutation is needed (16+) ([Stream API](https://docs.oracle.com/en/java/javase/27/docs/api/java.base/java/util/stream/Stream.html)).
- Use `getFirst()`, `getLast()`, `removeFirst()`, and `reversed()` on lists, deques, and linked sets/maps instead of index arithmetic or `descendingIterator()` (21+) ([JEP 431](https://openjdk.org/jeps/431), [SequencedCollection](https://docs.oracle.com/en/java/javase/27/docs/api/java.base/java/util/SequencedCollection.html)).
- Use `Stream.gather` with built-in `Gatherers` (`windowFixed`, `windowSliding`, `fold`, `scan`, `mapConcurrent`) for custom intermediate operations instead of stateful lambdas or collector workarounds (24+) ([JEP 485](https://openjdk.org/jeps/485), [Gatherers](https://docs.oracle.com/en/java/javase/27/docs/api/java.base/java/util/stream/Gatherers.html)).

```java
List<List<Integer>> pairs = Stream.of(1, 2, 3, 4, 5)
        .gather(Gatherers.windowFixed(2))
        .toList(); // [[1, 2], [3, 4], [5]]
```

- Keep stream behavioral parameters non-interfering (never modify the source) and stateless; use a plain loop when the logic needs mutation or checked exceptions ([Stream API](https://docs.oracle.com/en/java/javase/27/docs/api/java.base/java/util/stream/Stream.html)).

### Object contracts and null handling

- Override `equals` and `hashCode` together; equal objects must have equal hash codes, and `hashCode` must not change while fields used in `equals` are unchanged ([Object API](https://docs.oracle.com/en/java/javase/27/docs/api/java.base/java/lang/Object.html)).
- Keep `compareTo` consistent with `equals`, and throw `NullPointerException` for `compareTo(null)`; build comparators with `Comparator.comparing(...).thenComparing(...)` ([Comparable API](https://docs.oracle.com/en/java/javase/27/docs/api/java.base/java/lang/Comparable.html)).
- Prefer a record over a hand-written class when equality should be based on all components (16+) ([Record API](https://docs.oracle.com/en/java/javase/27/docs/api/java.base/java/lang/Record.html)).
- Do not use mutable objects or untrusted input as hash keys where an attacker controls collisions ([Secure Coding 1-5](https://www.oracle.com/java/technologies/javase/seccodeguide.html)).
- Use `Optional` only as a method return type for "no result"; never return `null` from an `Optional`-returning method, and do not use it for fields or parameters ([Optional API note](https://docs.oracle.com/en/java/javase/27/docs/api/java.base/java/util/Optional.html)).
- Do not synchronize on or compare `Optional` by identity; it is a value-based class ([Optional](https://docs.oracle.com/en/java/javase/27/docs/api/java.base/java/util/Optional.html)).
- Fail fast on illegal `null` arguments with `Objects.requireNonNull(arg, "name")` at API boundaries ([Secure Coding 5-1](https://www.oracle.com/java/technologies/javase/seccodeguide.html)).

### Errors and exceptions

- Throw checked exceptions only when the caller can reasonably recover; use unchecked exceptions for programming errors ([dev.java: Unchecked exceptions](https://dev.java/learn/language/annotations-exceptions/exceptions/unchecked-exception-controversy/)).
- Throw and catch the most specific exception type; never catch `Throwable`, `Error`, or broad `Exception` except at a top-level boundary that logs and translates ([Secure Coding 1-4](https://www.oracle.com/java/technologies/javase/seccodeguide.html)).
- Never swallow exceptions; when translating, pass the original as the cause (`new ServiceException("load failed", e)`) to keep the chain ([Throwable API](https://docs.oracle.com/en/java/javase/27/docs/api/java.base/java/lang/Throwable.html), [dev.java: Throwing exceptions](https://dev.java/learn/language/annotations-exceptions/exceptions/throwing/)).
- Restore the interrupt flag (`Thread.currentThread().interrupt()`) when catching `InterruptedException` without rethrowing ([Thread API](https://docs.oracle.com/en/java/javase/27/docs/api/java.base/java/lang/Thread.html)).
- Strip secrets, file paths, and internal details from exception messages that cross a trust boundary ([Secure Coding 2-1](https://www.oracle.com/java/technologies/javase/seccodeguide.html)).

### Resources, I/O, and HTTP

- Manage every `AutoCloseable` (streams, channels, JDBC objects, lock wrappers) with try-with-resources; it closes in reverse order and records close failures as suppressed exceptions (7+) ([dev.java: Catching and handling](https://dev.java/learn/language/annotations-exceptions/exceptions/catching-handling/), [Secure Coding 1-2](https://www.oracle.com/java/technologies/javase/seccodeguide.html)).
- Close `ExecutorService` instances with try-with-resources; `close()` waits for submitted tasks (19+) ([ExecutorService API](https://docs.oracle.com/en/java/javase/27/docs/api/java.base/java/util/concurrent/ExecutorService.html)).
- Never override `finalize()`; use try-with-resources for deterministic cleanup and `java.lang.ref.Cleaner` only as a safety net (finalization deprecated for removal, 18+) ([JEP 421](https://openjdk.org/jeps/421), [Object.finalize](https://docs.oracle.com/en/java/javase/27/docs/api/java.base/java/lang/Object.html)).
- Make a `Cleaner` action a static nested class or lambda that does not reference the registered object, or it will never run ([Cleaner API](https://docs.oracle.com/en/java/javase/27/docs/api/java.base/java/lang/ref/Cleaner.html)).
- Pass an explicit `StandardCharsets.UTF_8` when the code must behave identically on JDKs before 18; on 18+ the default charset is UTF-8 except console I/O ([JEP 400](https://openjdk.org/jeps/400)).
- Build one `HttpClient` per configuration and reuse it; it is immutable and owns its connection pools ([HttpClient API](https://docs.oracle.com/en/java/javase/27/docs/api/java.net.http/java/net/http/HttpClient.html)).
- Close `HttpClient` instances you create for a bounded scope with try-with-resources (21+) ([HttpClient API](https://docs.oracle.com/en/java/javase/27/docs/api/java.net.http/java/net/http/HttpClient.html)).
- Opt in to HTTP/3 with `.version(HttpClient.Version.HTTP_3)` only when the server supports it; the client otherwise downgrades to HTTP/2 (26+) ([JEP 517](https://openjdk.org/jeps/517)).

### Concurrency

- Run blocking, I/O-bound tasks on virtual threads with one thread per task via `Executors.newVirtualThreadPerTaskExecutor()` (21+) ([JEP 444](https://openjdk.org/jeps/444)).

```java
try (var executor = Executors.newVirtualThreadPerTaskExecutor()) {
    List<Future<String>> results = urls.stream()
            .map(url -> executor.submit(() -> fetch(url)))
            .toList();
    // close() waits for all tasks to finish
}
```

- Never pool virtual threads; limit concurrency to a scarce resource with a `Semaphore` instead (21+) ([Virtual threads guide](https://docs.oracle.com/en/java/javase/27/core/virtual-threads.html)).
- Do not cache expensive objects in `ThreadLocal` when running on virtual threads; each task gets a fresh thread, so the cache never hits (21+) ([Virtual threads guide](https://docs.oracle.com/en/java/javase/27/core/virtual-threads.html)).
- Use `Gatherers.mapConcurrent(maxConcurrency, mapper)` for bounded, order-preserving concurrent mapping inside a stream; it runs the mapper on virtual threads (24+) ([Gatherers](https://docs.oracle.com/en/java/javase/27/docs/api/java.base/java/util/stream/Gatherers.html)).
- Keep `synchronized` on 24+, where blocking inside it no longer pins the carrier thread; on 21-23 replace `synchronized` that guards frequent, long blocking I/O with `ReentrantLock` (24+) ([JEP 491](https://openjdk.org/jeps/491), [JEP 444](https://openjdk.org/jeps/444)).
- Use `ScopedValue` instead of `ThreadLocal` to pass immutable per-request context to callees and child threads (25+) ([JEP 506](https://openjdk.org/jeps/506), [ScopedValue API](https://docs.oracle.com/en/java/javase/27/docs/api/java.base/java/lang/ScopedValue.html)).

```java
static final ScopedValue<User> CURRENT_USER = ScopedValue.newInstance();

void serve(Request req) {
    ScopedValue.where(CURRENT_USER, authenticate(req)).run(() -> handle(req));
}
```

- Keep CPU-bound parallel work on platform-thread pools sized to cores; virtual threads add throughput only for tasks that block ([Virtual threads guide](https://docs.oracle.com/en/java/javase/27/core/virtual-threads.html)).
- Use `java.time` types, which are immutable and thread-safe, and inject a `Clock` instead of calling `Instant.now()` directly so time is testable (8+) ([java.time](https://docs.oracle.com/en/java/javase/27/docs/api/java.base/java/time/package-summary.html), [Clock API](https://docs.oracle.com/en/java/javase/27/docs/api/java.base/java/time/Clock.html)).
- Never use `java.util.Date`, `Calendar`, or `SimpleDateFormat` in new code; use `Instant`, `LocalDate`, `ZonedDateTime`, `Duration`, and `DateTimeFormatter` ([java.time](https://docs.oracle.com/en/java/javase/27/docs/api/java.base/java/time/package-summary.html)).

### Modules, programs, and platform integrity

- Use `import module M;` in scripts, prototypes, and compact source files; resolve name clashes with a single-type import, which shadows module imports (25+) ([JEP 511](https://openjdk.org/jeps/511)).
- Write small tools and scripts as compact source files with an instance `void main()` and run them with `java Tool.java` (25+) ([JEP 512](https://openjdk.org/jeps/512), [Compact source files guide](https://docs.oracle.com/en/java/javase/27/language/compact-source-files-instance-main-methods.html)).

```java
void main() {
    IO.println("Hello, World!");
}
```

- Hide internal packages by exporting only API packages from `module-info.java` ([Secure Coding 4-2](https://www.oracle.com/java/technologies/javase/seccodeguide.html)).
- Do not mutate `final` fields with deep reflection; JDK 26+ warns and a future release will deny it unless `--enable-final-field-mutation` is set (26+) ([JEP 500](https://openjdk.org/jeps/500)).
- Replace `sun.misc.Unsafe` memory access with `VarHandle` or the Foreign Function & Memory API; 24+ warns on first use (24+) ([JEP 498](https://openjdk.org/jeps/498)).
- Grant native access explicitly with `--enable-native-access=ALL-UNNAMED` (or module names) for JNI/FFM code instead of ignoring the warnings (24+) ([JEP 472](https://openjdk.org/jeps/472)).

### Security

- Use `PreparedStatement` with bound parameters for all SQL; never concatenate untrusted input into queries ([Secure Coding 3-2](https://www.oracle.com/java/technologies/javase/seccodeguide.html), [PreparedStatement API](https://docs.oracle.com/en/java/javase/27/docs/api/java.sql/java/sql/PreparedStatement.html)).
- Avoid Java serialization for untrusted data; if unavoidable, install an allow-list `ObjectInputFilter` or `jdk.serialFilter` pattern (9+), using context-specific filter factories where needed (17+) ([Serialization filtering guide](https://docs.oracle.com/en/java/javase/27/core/java-serialization-filters.html), [JEP 415](https://openjdk.org/jeps/415), [Secure Coding 8-6](https://www.oracle.com/java/technologies/javase/seccodeguide.html)).
- Generate tokens, keys, and nonces with `new SecureRandom()` and let it self-seed; never use `java.util.Random` or `Math.random()` for security, and never pass a fixed seed ([SecureRandom API](https://docs.oracle.com/en/java/javase/27/docs/api/java.base/java/security/SecureRandom.html)).
- Validate all untrusted input (size, range, format) before use and check resource limits without integer overflow ([Secure Coding 5-1, 1-3](https://www.oracle.com/java/technologies/javase/seccodeguide.html)).
- Never place untrusted data on a `ProcessBuilder`/`Runtime.exec` command line; pass it encoded, through a temporary file, or through an inherited channel ([Secure Coding 3-4](https://www.oracle.com/java/technologies/javase/seccodeguide.html)).
- Build XML and HTML with a library or proper encoder rather than string concatenation of untrusted data ([Secure Coding 3-3](https://www.oracle.com/java/technologies/javase/seccodeguide.html)).
- Never log passwords, keys, session tokens, or personal data ([Secure Coding 2-2](https://www.oracle.com/java/technologies/javase/seccodeguide.html)).
- Do not design for or depend on the Security Manager; it cannot be enabled on 24+ and `System.setSecurityManager` throws (24+) ([JEP 486](https://openjdk.org/jeps/486)).
- For highly sensitive values (passwords, private keys), consider holding them in `char[]`/`byte[]` and zeroing them right after use, accepting the extra complexity ([Secure Coding 2-3](https://www.oracle.com/java/technologies/javase/seccodeguide.html)).

### Logging, diagnostics, and documentation

- In libraries without a logging dependency, use `System.getLogger(name)` and the `Supplier` overloads so expensive messages are built only when the level is enabled (9+) ([System.Logger API](https://docs.oracle.com/en/java/javase/27/docs/api/java.base/java/lang/System.Logger.html)); in applications, keep the project's logging framework.
- Profile and diagnose with JDK Flight Recorder (`java -XX:StartFlightRecording:...` or `jcmd <pid> JFR.start`), which is designed for always-on production use, and analyze with `jfr` or JDK Mission Control ([java command](https://docs.oracle.com/en/java/javase/27/docs/specs/man/java.html), [dev.java: JFR](https://dev.java/learn/jvm/monitoring-troubleshooting/jfr/intro/), [JMC](https://jdk.java.net/jmc/9/)).
- Document every public type and member with a summary first sentence plus `@param`, `@return`, and `@throws` for each declared or documented exception ([Doc comment spec](https://docs.oracle.com/en/java/javase/27/docs/specs/javadoc/doc-comment-spec.html)).
- Use `{@snippet}` for code examples in Javadoc instead of `<pre>` blocks (18+) ([JEP 413](https://openjdk.org/jeps/413)).
- Write new doc comments in Markdown with `///` when the project targets 23+ and has no HTML doc convention (23+) ([JEP 467](https://openjdk.org/jeps/467)).

### Build, compiler, and testing

- Compile with `--release N` (Maven `maven.compiler.release`, Gradle toolchain) rather than `-source`/`-target`, so the code cannot call APIs missing from the target release ([javac --release](https://docs.oracle.com/en/java/javase/27/docs/specs/man/javac.html#option-release), [Maven compiler release](https://maven.apache.org/plugins/maven-compiler-plugin/examples/set-compiler-release.html), [Gradle toolchains](https://docs.gradle.org/current/userguide/toolchains.html)).
- Enable `-Xlint:all` and fail on warnings with `-Werror` in CI; suppress individual categories explicitly, not globally ([javac -Xlint](https://docs.oracle.com/en/java/javase/27/docs/specs/man/javac.html#option-Xlint), [javac -Werror](https://docs.oracle.com/en/java/javase/27/docs/specs/man/javac.html#option-Werror)).
- Write tests with JUnit Jupiter; use parameterized tests for input tables, and note that current JUnit requires Java 17+ at runtime ([JUnit User Guide](https://docs.junit.org/current/user-guide/)).

## Examples

Input: "Refactor this `instanceof` chain over `Shape` subclasses into something safer" in a project with `maven.compiler.release` 21.
Output: A `sealed interface Shape permits ...` with record implementations and an exhaustive `switch` expression using record patterns and no `default`; `_` is not used because the target is 21 (unnamed variables need 22+). Rules applied: sealed types, pattern matching for switch, records.

Input: "Our service creates a fixed thread pool of 200 threads for outbound HTTP calls; modernize it" on Gradle toolchain `JavaLanguageVersion.of(25)`.
Output: Replace the pool with `Executors.newVirtualThreadPerTaskExecutor()` in try-with-resources, a `Semaphore` to cap concurrent calls to the downstream service, a single shared `HttpClient`, `ScopedValue` for request context instead of `ThreadLocal`, and `synchronized` blocks kept as-is (no pinning on 24+). Rules applied: virtual threads, no pooling, semaphores, scoped values, HttpClient reuse.

Input: "Review this DAO" containing string-built SQL, `catch (Exception e) {}`, and `ObjectInputStream.readObject()` on network data.
Output: Review comments requiring `PreparedStatement` with bound parameters, specific exception handling with chained causes, try-with-resources for `Connection`/`ResultSet`, and removal of Java deserialization or an allow-list `ObjectInputFilter`. Rules applied: Secure Coding 3-2, 8-6, exception chaining, resource management.

## Edge cases

- Target is 17 or older: avoid pattern matching for `switch`, record patterns, sequenced collections, and virtual threads (21+); on 11 or older also avoid records, sealed types, text blocks, and switch expressions. Suggest JDK 25 LTS as the upgrade path.
- Target is 21-23: virtual threads are available but `synchronized` around long blocking I/O still pins; use `ReentrantLock` there. Gatherers (24+), scoped values, module imports, compact source files, and flexible constructor bodies (25+) are unavailable.
- Preview features in JDK 27: primitive types in patterns, `instanceof`, and `switch` (fifth preview, [JEP 532](https://openjdk.org/jeps/532)); structured concurrency (seventh preview, [JEP 533](https://openjdk.org/jeps/533)); lazy constants (third preview, [JEP 531](https://openjdk.org/jeps/531)); PEM encodings (third preview, [JEP 538](https://openjdk.org/jeps/538)). Use them only if the project already compiles and runs with `--enable-preview --release 27`, since preview code binds to that exact release ([JEP 12](https://openjdk.org/jeps/12)).
- Incubator APIs: the Vector API is still incubating in JDK 27 ([JEP 537](https://openjdk.org/jeps/537)); do not introduce it in production code without the user opting in.
- Project uses Lombok, Immutables, or similar: follow the existing approach; propose records only for new plain data carriers and do not mix styles within a type hierarchy.
- Generated code (annotation processors, protobuf, OpenAPI, JOOQ): never hand-edit it; change the generator input or configuration, and exclude generated sources from lint and formatting rules.
- Project style conflicts (for example a "never use `var`" Checkstyle rule or a mandated logging facade): follow the project; security and correctness rules still apply.
- Framework-managed beans (Spring, Jakarta EE, JPA entities): JPA entities need a no-arg constructor and mutable state, so do not convert them to records; records are fine for DTOs and projections.
- Android or other non-OpenJDK runtimes: do not assume JDK 21+ APIs; check the platform's supported language level and library desugaring.
- Libraries published to Maven Central: compile for the lowest supported release with `--release`, and keep new APIs behind multi-release JARs only when necessary.

## Resources

- [JDK 27 project page](https://openjdk.org/projects/jdk/27/): read when checking which JEPs are final, preview, or incubator in the current release.
- [Oracle Java SE Support Roadmap](https://www.oracle.com/java/technologies/java-se-support-roadmap.html): read when choosing an LTS target or upgrade path.
- [Java Language Updates, Release 27](https://docs.oracle.com/en/java/javase/27/language/index.html): read when applying records, sealed classes, patterns, switch, text blocks, or other language features.
- [Core Libraries, Release 27](https://docs.oracle.com/en/java/javase/27/core/index.html): read when working with collections, virtual threads, serialization filters, or logging.
- [Java SE 27 API documentation](https://docs.oracle.com/en/java/javase/27/docs/api/index.html): read when checking method contracts and `@since` versions.
- [Java Language Specification SE 27](https://docs.oracle.com/javase/specs/jls/se27/html/index.html): read when exact language semantics matter.
- [JEP index](https://openjdk.org/jeps/0): read when looking up a feature's status and history.
- [Local Variable Type Inference style guide](https://openjdk.org/projects/amber/guides/lvti-style-guide): read when deciding whether to use `var`.
- [Secure Coding Guidelines for Java SE](https://www.oracle.com/java/technologies/javase/seccodeguide.html): read when reviewing input handling, serialization, mutability, or exposure of internals.
- [javac command reference](https://docs.oracle.com/en/java/javase/27/docs/specs/man/javac.html): read when configuring `--release`, `-Xlint`, or `-Werror`.
- [Documentation Comment Specification](https://docs.oracle.com/en/java/javase/27/docs/specs/javadoc/doc-comment-spec.html): read when writing Javadoc.
- [dev.java Learn](https://dev.java/learn/): read when an official tutorial-style explanation is needed.
