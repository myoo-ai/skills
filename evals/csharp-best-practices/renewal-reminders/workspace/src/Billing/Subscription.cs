namespace Example.Billing;

public sealed record Subscription(string Id, string CustomerEmail, DateTimeOffset RenewsAt);

public sealed record RenewalRun(IReadOnlyList<Subscription> Reminders, IReadOnlyList<Subscription> Expired);

public interface ISubscriptionStore
{
    IEnumerable<Subscription> All();
}

public sealed class InMemorySubscriptionStore(IEnumerable<Subscription> subscriptions) : ISubscriptionStore
{
    private readonly Subscription[] _subscriptions = [.. subscriptions];

    public IEnumerable<Subscription> All() => _subscriptions;
}
