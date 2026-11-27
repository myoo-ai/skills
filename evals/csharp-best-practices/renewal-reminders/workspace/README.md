# Billing

Subscription billing jobs. `src/Billing` is the library. Our ASP.NET Core billing API registers it with `AddBilling()` and runs `RenewalReminderService` every night. `src/Billing.Demo` runs the job once over 3 sample subscriptions. Both target `net9.0` and build with the .NET 9 SDK.

```sh
dotnet build src/Billing.Demo
dotnet run --project src/Billing.Demo
```
