---
name: php-best-practices
description: "Applies current, officially sourced PHP 8.6 best practices to write new PHP code or modernize existing code across style, types, modern syntax, errors, OOP design, security, Composer, testing, and static analysis. Use when the user asks to write, refactor, review, or upgrade PHP code, mentions composer.json, PSR standards, PHPUnit, PHPStan, Psalm, or Rector, or works with .php files."
license: MIT
---

# PHP 8.6 best practices

Produces strictly typed, secure, maintainable PHP that targets the project's declared PHP version, using PHP 8.6 (latest stable, released 2026-11-19) idioms when allowed. Each branch gets two years of active support and two more of security fixes, so PHP 8.2 (security fixes until 2026-12-31) is the oldest supported branch and PHP 8.3 is the sensible baseline for new libraries ([Supported Versions](https://www.php.net/supported-versions.php)).

## Steps

1. Detect the target by reading `require.php` and `config.platform.php` in `composer.json`, the PHP version in CI, `Dockerfile`, or `.tool-versions`, and `phpVersion` in `phpstan.neon` or `psalm.xml`.
2. Detect project tooling: `phpcs.xml(.dist)`, `.php-cs-fixer(.dist).php`, `phpstan.neon(.dist)`, `psalm.xml(.dist)`, `rector.php`, `phpunit.xml(.dist)`, `tests/Pest.php`, and `scripts` entries in `composer.json`.
3. Apply the practices below. Use version-tagged features only when the lowest allowed PHP version supports them, otherwise write compatible code and optionally suggest raising `require.php`.
4. Follow existing project conventions and tool configs when they conflict with a non-safety rule, but never relax security or error-handling rules for consistency.
5. Run the formatter (`vendor/bin/php-cs-fixer fix` or `vendor/bin/phpcbf`), static analysis (`vendor/bin/phpstan analyse` or `vendor/bin/psalm`), tests (`vendor/bin/phpunit` or `vendor/bin/pest`), and `composer audit`. Prefer the project's Composer scripts when they exist.
6. After a PHP upgrade, run `vendor/bin/rector process --dry-run`, review, then apply, and read the migration guide for the new branch.

## Best practices

### Formatting, naming, autoloading

- Follow PER Coding Style 3.1, the successor of PSR-12, and let php-cs-fixer or PHP_CodeSniffer enforce it ([PER-CS](https://www.php-fig.org/per/coding-style/), [PSR-12](https://www.php-fig.org/psr/psr-12/)).
- Use only `<?php` tags, UTF-8 without BOM, and omit the closing `?>` in files that contain only PHP ([PSR-1](https://www.php-fig.org/psr/psr-1/), [PER-CS](https://www.php-fig.org/per/coding-style/)).
- Name classes `StudlyCaps`, methods `camelCase`, and class constants `UPPER_SNAKE_CASE` ([PSR-1](https://www.php-fig.org/psr/psr-1/)).
- Declare one class, interface, trait, or enum per file under a vendor namespace, and map namespaces to directories with PSR-4 ([PSR-4](https://www.php-fig.org/psr/psr-4/), [Composer autoload](https://getcomposer.org/doc/04-schema.md#psr-4)).
- Keep files either declaring symbols or causing side effects, never both ([PSR-1](https://www.php-fig.org/psr/psr-1/)).
- Load code through `vendor/autoload.php`, not manual `require` chains, and run `composer dump-autoload --optimize` in production builds ([Composer autoloader optimization](https://getcomposer.org/doc/articles/autoloader-optimization.md)).
- Use trailing commas in multi-line argument, parameter, array, and `use` lists so diffs stay one line ([PER-CS](https://www.php-fig.org/per/coding-style/), [Trailing comma RFC](https://wiki.php.net/rfc/trailing_comma_in_parameter_list)).
- Document each parameter with its own doc comment next to the declaration instead of a repeated `@param` tag (8.6+) ([Parameter doc comments RFC](https://wiki.php.net/rfc/parameter-doccomments)).

### Types

- Start every file with `declare(strict_types=1);` so scalar arguments are not silently coerced ([Strict typing](https://www.php.net/manual/en/language.types.declarations.php#language.types.declarations.strict)).
- Type every parameter, return value, property, and class constant. Keep docblock types only for what native types cannot express, such as `list<User>` ([Type declarations](https://www.php.net/manual/en/language.types.declarations.php), [PHPStan PHPDoc types](https://phpstan.org/writing-php-code/phpdoc-types)).
- Use union and intersection types, including DNF forms such as `(A&B)|null`, instead of `mixed` (DNF 8.2+) ([Composite types](https://www.php.net/manual/en/language.types.type-system.php#language.types.type-system.composite), [DNF RFC](https://wiki.php.net/rfc/dnf_types)).
- Return `void` when nothing is returned and `never` from functions that always throw or exit (8.1+) ([never RFC](https://wiki.php.net/rfc/noreturn_type)).
- Type class constants (8.3+) ([Typed class constants RFC](https://wiki.php.net/rfc/typed_class_constants)).
- Use backed enums instead of class constants or magic strings for closed sets of values (8.1+) ([Enumerations](https://www.php.net/manual/en/language.enumerations.php)).

```php
enum Status: string
{
    case Draft = 'draft';
    case Published = 'published';

    public function label(): string
    {
        return match ($this) {
            self::Draft => 'Draft',
            self::Published => 'Published',
        };
    }
}

$status = Status::from($row['status']); // throws ValueError on unknown input
```

- Use the built-in `SortDirection` enum in APIs that take a sort order instead of `SORT_ASC` ints or strings (8.6+) ([SortDirection RFC](https://wiki.php.net/rfc/sort_direction_enum)).
- Use `\Time\Duration` for timeouts and elapsed times instead of bare integers of unclear unit (8.6+) ([Duration](https://www.php.net/manual/en/class.time-duration.php)).

### Immutability and properties

- Mark value-object properties `readonly` (8.1+) and whole value classes `readonly class` (8.2+) ([Readonly properties](https://www.php.net/manual/en/language.oop5.properties.php#language.oop5.properties.readonly-properties), [Readonly classes RFC](https://wiki.php.net/rfc/readonly_classes)).
- Give readonly properties a default value when it is fixed, instead of assigning it in the constructor (8.6+) ([Readonly defaults RFC](https://wiki.php.net/rfc/readonly_property_defaults)).
- Use constructor property promotion for plain data holders (8.0+) ([Constructor promotion](https://www.php.net/manual/en/language.oop5.decon.php#language.oop5.decon.constructor.promotion)).
- Build "withers" with `clone($this, ['name' => $name])` instead of cloning and mutating (8.5+) ([Clone with RFC](https://wiki.php.net/rfc/clone_with_v2)).
- Use `public private(set)` for properties readable everywhere but written only inside the class, instead of a getter (8.4+) ([Asymmetric visibility RFC](https://wiki.php.net/rfc/asymmetric-visibility-v2)).
- Use property hooks for validation or derived values instead of getter and setter pairs (8.4+) ([Property hooks](https://www.php.net/manual/en/language.oop5.property-hooks.php)).

```php
final class User
{
    public string $email {
        set => strtolower(trim($value));
    }

    public function __construct(
        public private(set) int $id,
        string $email,
    ) {
        $this->email = $email;
    }
}
```

### Modern syntax

- Use `match` instead of `switch` for value mapping, since it compares strictly and throws `UnhandledMatchError` on missing arms (8.0+) ([match](https://www.php.net/manual/en/control-structures.match.php)).
- Use the nullsafe operator `?->` instead of nested null checks (8.0+) ([Nullsafe RFC](https://wiki.php.net/rfc/nullsafe_operator)).
- Use named arguments for boolean flags and optional parameters to make calls self-describing (8.0+) ([Named arguments](https://www.php.net/manual/en/functions.arguments.php#functions.named-arguments)).
- Use first-class callable syntax `strlen(...)` instead of string or array callables (8.1+) ([First-class callables](https://www.php.net/manual/en/functions.first_class_callable_syntax.php)).
- Use partial function application with `?` and `...` placeholders instead of wrapper closures (8.6+) ([Partial application](https://www.php.net/manual/en/functions.partial-application.php)).

```php
$supported = array_filter($versions, version_compare(?, '8.6', '>='));
```

- Use the pipe operator `|>` for linear chains of single-argument calls instead of nested calls or temporary variables (8.5+) ([Pipe operator RFC](https://wiki.php.net/rfc/pipe-operator-v3)).
- Use `str_contains`, `str_starts_with`, and `str_ends_with` instead of `strpos` comparisons (8.0+) ([str_contains](https://www.php.net/manual/en/function.str-contains.php)).
- Use `array_find`, `array_find_key`, `array_any`, and `array_all` instead of manual search loops (8.4+) ([array_find](https://www.php.net/manual/en/function.array-find.php)).
- Use `array_first` and `array_last` instead of `reset`/`end` or `array_key_first` lookups (8.5+) ([array_first RFC](https://wiki.php.net/rfc/array_first_last)).
- Use `clamp($value, $min, $max)` instead of `max($min, min($value, $max))` (8.6+) ([clamp](https://www.php.net/manual/en/function.clamp.php)).
- Write `new Foo()->bar()` without wrapping parentheses (8.4+) ([new without parentheses RFC](https://wiki.php.net/rfc/new_without_parentheses)).
- Use short array syntax `[]`, `??` and `??=` for defaults, and spread `...` for unpacking, including string keys (8.1+) ([Arrays](https://www.php.net/manual/en/language.types.array.php), [Null coalescing assignment](https://www.php.net/manual/en/language.operators.assignment.php)).
- Mark methods that override a parent with `#[\Override]` so renames fail loudly (8.3+) ([Override RFC](https://wiki.php.net/rfc/marking_overriden_methods)).
- Mark functions whose result must be used with `#[\NoDiscard]` (8.5+) ([NoDiscard RFC](https://wiki.php.net/rfc/marking_return_value_as_important)).

### Errors and exceptions

- Never use the `@` error suppression operator. Check return values or enable exceptions instead ([Error control operator](https://www.php.net/manual/en/language.operators.errorcontrol.php)).
- Configure streams to throw `StreamException` with `error_mode` set to `StreamErrorMode::Exception` instead of reading `error_get_last()` (8.6+) ([Stream errors](https://www.php.net/manual/en/stream.errors.handling.php)).
- Throw specific exception classes (`InvalidArgumentException`, `DomainException`, or your own) and catch the narrowest type you can handle ([SPL exceptions](https://www.php.net/manual/en/spl.exceptions.php)).
- Never swallow exceptions with an empty `catch`. Log with context, or rethrow a wrapping exception that passes the original as `previous` ([Exception](https://www.php.net/manual/en/class.exception.php), [Exception::__construct](https://www.php.net/manual/en/exception.construct.php)).
- Use the catch-without-variable form `catch (Foo)` when the exception object is unused (8.0+) ([Non-capturing catches RFC](https://wiki.php.net/rfc/non-capturing_catches)).
- Never `return` from a `finally` block, because it discards the pending exception (deprecated in 8.6) ([8.6 deprecations](https://www.php.net/manual/en/migration86.deprecated.php)).
- Log through a PSR-3 `LoggerInterface` and pass variables in the context array, not interpolated into the message ([PSR-3](https://www.php-fig.org/psr/psr-3/)).
- Set `display_errors=Off` and `log_errors=On` in production, and report all errors with `error_reporting=E_ALL` ([Error reporting security](https://www.php.net/manual/en/security.errors.php)).
- Enable `mysqli` exceptions or use PDO with `PDO::ERRMODE_EXCEPTION`, the default since 8.0 ([PDO errors](https://www.php.net/manual/en/pdo.error-handling.php)).

### OOP design

- Declare classes `final` unless designed for extension, and prefer composition over inheritance ([final keyword](https://www.php.net/manual/en/language.oop5.final.php)).
- Depend on interfaces and inject dependencies through the constructor. Wire them in a PSR-11 container rather than fetching services from it inside classes ([PSR-11](https://www.php-fig.org/psr/psr-11/)).
- Avoid mutable static properties and singletons, which leak state across tests and long-running workers ([Static keyword](https://www.php.net/manual/en/language.oop5.static.php)).
- Code against the PSR-7, PSR-17, and PSR-18 interfaces for HTTP so implementations stay swappable ([PSR-7](https://www.php-fig.org/psr/psr-7/), [PSR-17](https://www.php-fig.org/psr/psr-17/), [PSR-18](https://www.php-fig.org/psr/psr-18/)).
- Implement `__serialize`/`__unserialize` instead of `__sleep`/`__wakeup`, which are soft-deprecated (8.5+) ([8.5 deprecations](https://www.php.net/manual/en/migration85.deprecated.php)).
- Avoid dynamic properties. Declare every property, and use `#[\AllowDynamicProperties]` only on legacy classes (deprecated since 8.2) ([Dynamic properties RFC](https://wiki.php.net/rfc/deprecate_dynamic_properties)).

### Arrays, strings, performance

- Use generators (`yield`) to stream large datasets instead of building full arrays in memory ([Generators](https://www.php.net/manual/en/language.generators.overview.php)).
- Compare with `===` and pass `strict: true` to `in_array` and `array_search` ([Comparison operators](https://www.php.net/manual/en/language.operators.comparison.php), [in_array](https://www.php.net/manual/en/function.in-array.php)).
- Use `array_map`, `array_filter`, and `array_column` for transformations, and `array_is_list` to check for list arrays (8.1+) ([Array functions](https://www.php.net/manual/en/ref.array.php), [array_is_list](https://www.php.net/manual/en/function.array-is-list.php)).
- Use `mb_*` functions for user-visible text, including `mb_trim` and `mb_ucfirst` (8.4+) ([mbstring](https://www.php.net/manual/en/book.mbstring.php)).
- Enable OPcache in production, and consider preloading for frameworks with a stable class set ([OPcache](https://www.php.net/manual/en/book.opcache.php), [Preloading](https://www.php.net/manual/en/opcache.preloading.php)).
- Use the `Io\Poll` API instead of `stream_select()` for many concurrent streams (8.6+) ([Poll API RFC](https://wiki.php.net/rfc/poll_api)).
- Profile before optimizing, and measure with `hrtime(true)` rather than `microtime` ([hrtime](https://www.php.net/manual/en/function.hrtime.php)).

### Security

- Hash passwords with `password_hash($pw, PASSWORD_DEFAULT)`, verify with `password_verify`, and rehash when `password_needs_rehash` says so ([Password hashing](https://www.php.net/manual/en/faq.passwords.php), [OWASP Password Storage](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html)).
- Use prepared statements with bound parameters for every query, and set `PDO::ATTR_EMULATE_PREPARES` to `false` ([PDO prepared statements](https://www.php.net/manual/en/pdo.prepared-statements.php), [OWASP SQL Injection](https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html)).

```php
$stmt = $pdo->prepare('SELECT id, name FROM users WHERE email = :email');
$stmt->execute(['email' => $email]);
$user = $stmt->fetch(PDO::FETCH_ASSOC);
```

- Escape output for its context, with `htmlspecialchars($s, ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8')` for HTML, or use an auto-escaping template engine ([htmlspecialchars](https://www.php.net/manual/en/function.htmlspecialchars.php), [OWASP XSS](https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html)).
- Protect state-changing requests with synchronizer CSRF tokens from `random_bytes` compared via `hash_equals` ([OWASP CSRF](https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html), [hash_equals](https://www.php.net/manual/en/function.hash-equals.php)).
- Use `random_int` and `random_bytes` (or `Random\Randomizer`) for secrets, never `rand` or `mt_rand` ([Random\Randomizer](https://www.php.net/manual/en/class.random-randomizer.php), [random_bytes](https://www.php.net/manual/en/function.random-bytes.php)).
- Set `session.use_strict_mode=1`, `session.cookie_httponly=1`, `session.cookie_secure=1`, and `session.cookie_samesite=Lax`, and call `session_regenerate_id(true)` after login ([Session security](https://www.php.net/manual/en/session.security.ini.php), [OWASP Session Management](https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html)).
- Never pass user input to `unserialize`. Use `json_decode($s, flags: JSON_THROW_ON_ERROR)` instead ([unserialize](https://www.php.net/manual/en/function.unserialize.php), [OWASP Deserialization](https://cheatsheetseries.owasp.org/cheatsheets/Deserialization_Cheat_Sheet.html)).
- Validate input with `filter_var` and allowlists, and pass shell arguments through `escapeshellarg` or avoid the shell entirely ([filter_var](https://www.php.net/manual/en/function.filter-var.php), [escapeshellarg](https://www.php.net/manual/en/function.escapeshellarg.php)).
- Store uploads outside the web root with generated names and check them with `finfo`, never the client MIME type ([File uploads](https://www.php.net/manual/en/features.file-upload.php), [OWASP File Upload](https://cheatsheetseries.owasp.org/cheatsheets/File_Upload_Cheat_Sheet.html)).
- Parse and validate URLs with the `Uri\Rfc3986\Uri` or `Uri\WhatWg\Url` classes instead of `parse_url` (8.5+) ([URI extension RFC](https://wiki.php.net/rfc/url_parsing_api)).
- Keep secrets out of the repository and read them from the environment or a secret store ([OWASP Secrets Management](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html)).

### Dependencies and Composer

- Declare the supported PHP range in `require.php` (for example `"^8.3"`) and required extensions as `ext-*` entries ([Composer platform packages](https://getcomposer.org/doc/01-basic-usage.md#platform-packages)).
- Set `config.platform.php` to the lowest production version so resolution matches the deployed runtime ([Composer config platform](https://getcomposer.org/doc/06-config.md#platform)).
- Commit `composer.lock` for applications and install with `composer install --no-dev --classmap-authoritative` in production ([Composer basic usage](https://getcomposer.org/doc/01-basic-usage.md#commit-your-composer-lock-file-to-version-control)).
- Use caret constraints (`^2.3`) and never `*` or `dev-main` in released code ([Composer versions](https://getcomposer.org/doc/articles/versions.md)).
- Run `composer audit` in CI and keep `config.audit.block-insecure` enabled so known-vulnerable versions are refused ([composer audit](https://getcomposer.org/doc/03-cli.md#audit), [Composer config audit](https://getcomposer.org/doc/06-config.md#audit)).
- Run `composer validate --strict` in CI and `composer bump` for applications to raise lower bounds ([composer validate](https://getcomposer.org/doc/03-cli.md#validate), [composer bump](https://getcomposer.org/doc/03-cli.md#bump)).
- Put test and analysis tools in `require-dev` and expose them as Composer `scripts` ([Composer scripts](https://getcomposer.org/doc/articles/scripts.md)).

### Testing

- Use PHPUnit attributes (`#[Test]`, `#[DataProvider]`, `#[CoversClass]`) instead of docblock annotations, which PHPUnit 12 removed ([PHPUnit attributes](https://docs.phpunit.de/en/12.5/attributes.html)).
- Make data providers `public static` and give data sets string keys so failures name the case ([PHPUnit data providers](https://docs.phpunit.de/en/12.5/writing-tests-for-phpunit.html#data-providers)).

```php
final class SlugTest extends TestCase
{
    #[Test]
    #[DataProvider('cases')]
    public function itSlugifies(string $input, string $expected): void
    {
        self::assertSame($expected, Slug::from($input));
    }

    public static function cases(): iterable
    {
        yield 'spaces' => ['Hello World', 'hello-world'];
        yield 'accents' => ['Crème brûlée', 'creme-brulee'];
    }
}
```

- Prefer `assertSame` over `assertEquals` to avoid loose comparisons ([PHPUnit assertions](https://docs.phpunit.de/en/12.5/assertions.html#assertsame)).
- Use test stubs for queries and mocks only for verifying outgoing calls, created with `createStub` or `createMock` ([PHPUnit test doubles](https://docs.phpunit.de/en/12.5/test-doubles.html)).
- Enable `failOnWarning`, `failOnRisky`, and `failOnDeprecation` in `phpunit.xml` ([PHPUnit configuration](https://docs.phpunit.de/en/12.5/configuration.html)).
- Pick the PHPUnit major that supports the project's lowest PHP version. PHPUnit 13 requires PHP 8.4+ ([PHPUnit supported versions](https://phpunit.de/supported-versions.html)).

### Static analysis

- Run PHPStan or Psalm in CI. Aim for PHPStan level 8 or higher (level 10 is the strictest) or Psalm level 1 to 3 ([PHPStan rule levels](https://phpstan.org/user-guide/rule-levels), [Psalm error levels](https://psalm.dev/docs/running_psalm/error_levels/)).
- Raise the level on legacy code with a baseline instead of ignoring errors inline ([PHPStan baseline](https://phpstan.org/user-guide/baseline), [Psalm baseline](https://psalm.dev/docs/running_psalm/dealing_with_code_issues/#using-a-baseline-file)).
- Add generic and array-shape types (`@param list<int>`, `@return array{id: int, name: string}`) where native types fall short ([PHPStan PHPDoc types](https://phpstan.org/writing-php-code/phpdoc-types)).
- Automate upgrades and dead-code removal with Rector sets matching the target PHP version ([Rector docs](https://getrector.com/documentation)).

### Deprecations to avoid

- Write `{$var}` instead of `${var}` in string interpolation (deprecated in 8.2) ([String interpolation RFC](https://wiki.php.net/rfc/deprecate_dollar_brace_string_interpolation)).
- Declare nullable parameters as `?T $x = null`, never implicitly via `T $x = null` (deprecated in 8.4) ([Implicit nullable RFC](https://wiki.php.net/rfc/deprecate-implicitly-nullable-types)).
- Use `(bool)`, `(int)`, `(float)`, and `(string)` casts, not `(boolean)`, `(integer)`, `(double)`, or `(binary)`, and use `shell_exec` instead of backticks (deprecated in 8.5) ([8.5 deprecations](https://www.php.net/manual/en/migration85.deprecated.php)).
- Do not use `null` as an array offset or increment non-numeric strings. Use `''` and `str_increment` (deprecated in 8.5) ([8.5 deprecations](https://www.php.net/manual/en/migration85.deprecated.php)).
- Drop `curl_close`, `finfo_close`, and `imagedestroy` calls, since the objects free themselves (deprecated in 8.5) ([8.5 deprecations](https://www.php.net/manual/en/migration85.deprecated.php)).
- Do not return values from `__construct` or `__destruct`, and do not name symbols `let`, `is`, or `readonly` (deprecated in 8.6) ([8.6 deprecations](https://www.php.net/manual/en/migration86.deprecated.php)).
- Replace `utf8_encode`/`utf8_decode` with `mb_convert_encoding` (deprecated in 8.2) ([utf8_encode](https://www.php.net/manual/en/function.utf8-encode.php)).

## Examples

Input: "Add a repository method that finds users by email and a test." (`require.php` is `^8.4`)
Output: A `final readonly class` repository taking `PDO` by constructor promotion, a prepared statement with a named parameter, and a `?User` return built from a readonly value object. A PHPUnit test uses `#[Test]` and a static data provider, and PHPStan runs at the project level.

Input: "Review this controller." (`require.php` is `^8.2`)
Output: Findings citing missing `declare(strict_types=1)`, unescaped output, a `switch` that should be `match`, string status constants that should be an enum, and an empty `catch`. Suggestions for property hooks and `#[\Override]` are marked as requiring a `require.php` bump, not applied.

Input: "We upgraded to PHP 8.6, please modernize the codebase."
Output: Raise `require.php` and `config.platform.php`, run Rector with the PHP 8.6 set in dry-run mode, apply reviewed changes, replace `max(min())` with `clamp`, move `return` out of `finally` blocks, then run php-cs-fixer, PHPStan, PHPUnit with `failOnDeprecation`, and `composer audit`.

## Edge cases

- If `require.php` is older than a tagged feature, keep compatible code (getters instead of hooks, `max(min())` instead of `clamp`) and suggest raising the constraint.
- Libraries: target the oldest supported branch your users need (8.2 support ends 2026-12-31, so prefer `^8.3`) and test every allowed minor in CI.
- In frameworks such as Laravel or Symfony, follow the framework's conventions and escaping helpers, but keep strict types and prepared statements.
- WordPress code follows the WordPress Coding Standards, not PER-CS, so use the project's phpcs ruleset.
- In long-running runtimes such as RoadRunner, FrankenPHP worker mode, or Swoole, reset per-request state and never keep request data in static properties.
- Pest projects: write tests in Pest syntax and keep the PHPUnit configuration rules, since Pest runs on PHPUnit.
- Never hand-edit generated code or `vendor/`. Change the generator or patch upstream.
- If tool versions predate the target PHP version, upgrade PHPStan, Psalm, php-cs-fixer, or Rector instead of disabling checks that fail to parse new syntax.

## Resources

- [PHP 8.6 release page](https://www.php.net/releases/8.6/en.php): read when using or reviewing any 8.6 feature.
- [PHP 8.6 migration guide](https://www.php.net/manual/en/migration86.php): read when upgrading to 8.6 or checking incompatible changes.
- [Supported Versions](https://www.php.net/supported-versions.php): read when choosing the minimum PHP version.
- [PHP Manual](https://www.php.net/manual/en/): read when checking a function or language construct.
- [PHP RFCs](https://wiki.php.net/rfc): read when you need the rationale and exact semantics of a feature.
- [PER Coding Style](https://www.php-fig.org/per/coding-style/): read when formatting questions come up.
- [PHP-FIG PSRs](https://www.php-fig.org/psr/): read when designing interfaces for logging, HTTP, containers, or caching.
- [Composer documentation](https://getcomposer.org/doc/): read when editing `composer.json` or setting up CI installs.
- [PHPUnit manual](https://docs.phpunit.de/): read when writing or configuring tests.
- [PHPStan user guide](https://phpstan.org/user-guide/getting-started): read when configuring static analysis.
- [OWASP Cheat Sheet Series](https://cheatsheetseries.owasp.org/): read when handling input, output, sessions, or authentication.
