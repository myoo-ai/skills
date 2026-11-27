using Microsoft.Extensions.Logging;

namespace Example.Billing;

/// <summary>
/// Nightly job. It finds subscriptions that renew within the reminder window and
/// subscriptions whose renewal date has passed.
/// </summary>
public sealed class RenewalReminderService
{
    public static readonly TimeSpan ReminderWindow = TimeSpan.FromDays(7);

    private readonly ISubscriptionStore _store;
    private readonly ILogger<RenewalReminderService> _logger;

    public RenewalReminderService(ISubscriptionStore store, ILogger<RenewalReminderService> logger)
    {
        _store = store;
        _logger = logger;
    }

    public RenewalRun Run()
    {
        DateTimeOffset now = DateTimeOffset.UtcNow;
        var reminders = new List<Subscription>();
        var expired = new List<Subscription>();
        foreach (Subscription subscription in _store.All())
        {
            if (subscription.RenewsAt <= now)
            {
                expired.Add(subscription);
                _logger.LogWarning($"Subscription {subscription.Id} expired on {subscription.RenewsAt:yyyy-MM-dd}");
            }
            else if (subscription.RenewsAt - now <= ReminderWindow)
            {
                reminders.Add(subscription);
                _logger.LogInformation($"Reminder due for subscription {subscription.Id}, renews on {subscription.RenewsAt:yyyy-MM-dd}");
            }
        }
        _logger.LogInformation($"Renewal run finished: {reminders.Count} reminders, {expired.Count} expired");
        return new RenewalRun(reminders, expired);
    }
}
