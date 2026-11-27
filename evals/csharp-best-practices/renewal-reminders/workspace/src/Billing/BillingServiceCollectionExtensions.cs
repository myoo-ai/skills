using Microsoft.Extensions.DependencyInjection;

namespace Example.Billing;

public static class BillingServiceCollectionExtensions
{
    /// <summary>Registers the billing services. The host registers the ISubscriptionStore and logging.</summary>
    public static IServiceCollection AddBilling(this IServiceCollection services)
    {
        services.AddSingleton<RenewalReminderService>();
        return services;
    }
}
