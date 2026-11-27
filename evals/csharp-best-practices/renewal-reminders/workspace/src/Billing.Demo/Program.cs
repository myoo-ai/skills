using Example.Billing;
using Microsoft.Extensions.DependencyInjection;

DateTimeOffset today = DateTimeOffset.UtcNow;

var services = new ServiceCollection();
services.AddLogging();
services.AddSingleton<ISubscriptionStore>(new InMemorySubscriptionStore(
[
    new("S-1", "ann@example.com", today.AddDays(-1)),
    new("S-2", "bob@example.com", today.AddDays(3)),
    new("S-3", "cem@example.com", today.AddDays(30)),
]));
services.AddBilling();

using ServiceProvider provider = services.BuildServiceProvider(new ServiceProviderOptions { ValidateScopes = true, ValidateOnBuild = true });
RenewalRun run = provider.GetRequiredService<RenewalReminderService>().Run();
Console.WriteLine($"remind: {string.Join(", ", run.Reminders.Select(s => s.Id))}");
Console.WriteLine($"expired: {string.Join(", ", run.Expired.Select(s => s.Id))}");
