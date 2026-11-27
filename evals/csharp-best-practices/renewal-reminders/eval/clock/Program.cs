using Example.Billing;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Logging;

var start = new DateTimeOffset(2031, 3, 10, 12, 0, 0, TimeSpan.Zero);
var clock = new ManualClock(start);
var capture = new CaptureProvider();

var services = new ServiceCollection();
services.AddLogging(logging => logging.AddProvider(capture).SetMinimumLevel(LogLevel.Trace));
services.AddSingleton<ISubscriptionStore>(new InMemorySubscriptionStore(
[
    new("S-1", "ann@example.com", start.AddDays(-1)),
    new("S-2", "bob@example.com", start.AddDays(2)),
    new("S-3", "cem@example.com", start.AddDays(7)),
    new("S-4", "dua@example.com", start.AddDays(7).AddMinutes(1)),
]));
services.AddBilling();
services.AddSingleton<TimeProvider>(clock);

using ServiceProvider provider = services.BuildServiceProvider(new ServiceProviderOptions { ValidateScopes = true, ValidateOnBuild = true });
RenewalReminderService service = provider.GetRequiredService<RenewalReminderService>();

RenewalRun first = service.Run();
Check(Ids(first.Reminders) == "S-2,S-3" && Ids(first.Expired) == "S-1", $"run at {start:O}: reminders {Ids(first.Reminders)}, expired {Ids(first.Expired)}; want S-2,S-3 and S-1 (the job must use the registered TimeProvider)");

clock.Now = start.AddDays(3);
RenewalRun second = service.Run();
Check(Ids(second.Reminders) == "S-3,S-4" && Ids(second.Expired) == "S-1,S-2", $"run 3 days later: reminders {Ids(second.Reminders)}, expired {Ids(second.Expired)}; want S-3,S-4 and S-1,S-2");

Check(capture.Entries.Count > 0, "the job logs");
string[] wanted =
[
    "Subscription S-1 expired on 2031-03-09",
    "Reminder due for subscription S-2, renews on 2031-03-12",
    "Renewal run finished: 2 reminders, 1 expired",
];
foreach (string message in wanted)
{
    Check(capture.Entries.Any(e => e.Message == message), $"message \"{message}\" logged with unchanged wording; got: {string.Join(" | ", capture.Entries.Select(e => e.Message).Distinct().Take(8))}");
}
foreach (Entry entry in capture.Entries.Where(e => e.Message.Contains("S-", StringComparison.Ordinal)))
{
    Check(entry.Properties.TryGetValue("{OriginalFormat}", out object? template) && template is string text && !text.Contains("S-", StringComparison.Ordinal),
        $"\"{entry.Message}\" is logged from a message template, not a finished string");
    Check(entry.Properties.TryGetValue("SubscriptionId", out object? id) && id is string s && entry.Message.Contains(s, StringComparison.Ordinal),
        $"\"{entry.Message}\" carries the subscription id as a SubscriptionId property; properties: {string.Join(", ", entry.Properties.Keys)}");
}

Console.WriteLine("ok");
return 0;

static string Ids(IEnumerable<Subscription> subscriptions) => string.Join(",", subscriptions.Select(s => s.Id).Order(StringComparer.Ordinal));

static void Check(bool ok, string message)
{
    if (!ok)
    {
        Console.Error.WriteLine("FAIL: " + message);
        Environment.Exit(1);
    }
}

sealed class ManualClock(DateTimeOffset now) : TimeProvider
{
    public DateTimeOffset Now { get; set; } = now;

    public override DateTimeOffset GetUtcNow() => Now;
}

sealed record Entry(LogLevel Level, string Message, IReadOnlyDictionary<string, object?> Properties);

sealed class CaptureProvider : ILoggerProvider
{
    public List<Entry> Entries { get; } = [];

    public ILogger CreateLogger(string categoryName) => new CaptureLogger(this);

    public void Dispose()
    {
    }

    private sealed class CaptureLogger(CaptureProvider owner) : ILogger
    {
        public IDisposable? BeginScope<TState>(TState state) where TState : notnull => null;

        public bool IsEnabled(LogLevel logLevel) => true;

        public void Log<TState>(LogLevel logLevel, EventId eventId, TState state, Exception? exception, Func<TState, Exception?, string> formatter)
        {
            Dictionary<string, object?> properties = [];
            if (state is IEnumerable<KeyValuePair<string, object?>> pairs)
            {
                foreach ((string key, object? value) in pairs)
                {
                    properties[key] = value;
                }
            }
            lock (owner.Entries)
            {
                owner.Entries.Add(new Entry(logLevel, formatter(state, exception), properties));
            }
        }
    }
}
