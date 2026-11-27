using Example.Orders;

string path = Path.Combine(Directory.CreateTempSubdirectory("orders").FullName, "orders.csv");
File.WriteAllText(path, "id,customer,total\nA1,alice@example.com,12.50\nA2,bob@example.org,7\nA3,carol@example.com,99.99\n");

var ui = new CountingContext();
Task import;
SynchronizationContext.SetSynchronizationContext(ui);
try
{
    import = new OrderImporter(new SlowValidator()).ImportAsync(path);
}
finally
{
    SynchronizationContext.SetSynchronizationContext(null);
}
await import;
var crm = new CountingContext();
SynchronizationContext.SetSynchronizationContext(crm);
Task<bool> check;
try
{
    check = new EmailDomainValidator(new[] { "example.com" }).ValidateAsync(new Order("X", "x@example.com", 1m), CancellationToken.None);
}
finally
{
    SynchronizationContext.SetSynchronizationContext(null);
}
await check;
if (ui.Posts + crm.Posts > 0)
{
    Console.Error.WriteLine($"FAIL: {ui.Posts} continuation(s) of ImportAsync and {crm.Posts} of EmailDomainValidator ran on the caller's context");
    return 1;
}
Console.WriteLine("ok");
return 0;

sealed class SlowValidator : IOrderValidator
{
    public async Task<bool> ValidateAsync(Order order, CancellationToken cancellationToken)
    {
        await Task.Delay(5, cancellationToken).ConfigureAwait(false);
        return true;
    }
}

sealed class CountingContext : SynchronizationContext
{
    private int _posts;
    public int Posts => Volatile.Read(ref _posts);

    public override void Post(SendOrPostCallback d, object? state)
    {
        Interlocked.Increment(ref _posts);
        ThreadPool.QueueUserWorkItem(_ =>
        {
            SetSynchronizationContext(this);
            d(state);
        });
    }
}
