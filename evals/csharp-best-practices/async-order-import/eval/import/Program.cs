using System.Collections.Concurrent;
using Example.Orders;

string dir = Directory.CreateTempSubdirectory("orders").FullName;
string path = Path.Combine(dir, "orders.csv");
File.WriteAllText(path, "id,customer,total\nA1,alice@example.com,12.50\nA2,bob@example.com,7\n\nA3,carol@example.com,99.99\n");
string badPath = Path.Combine(dir, "bad.csv");
File.WriteAllText(badPath, "id,customer,total\nB1,x@example.com,1\nB2,broken\n");

using var cts = new CancellationTokenSource();
var recorder = new RecordingValidator();
var orders = await new OrderImporter(recorder).ImportAsync(path, cts.Token);
Check(orders.Count == 3 && orders[0] == new Order("A1", "alice@example.com", 12.50m) && orders[2].Id == "A3", "imports the valid rows in file order");
Check(recorder.Tokens.Count == 3 && recorder.Tokens.All(t => t == cts.Token), "passes the caller's token to the validator");

orders = await new OrderImporter(new RecordingValidator { Reject = "A2" }).ImportAsync(path);
Check(orders.Select(o => o.Id).SequenceEqual(new[] { "A1", "A3" }), "drops rejected orders");

using var midway = new CancellationTokenSource();
await ThrowsAsync<OperationCanceledException>(() => new OrderImporter(new RecordingValidator { AfterValidate = midway.Cancel }).ImportAsync(path, midway.Token), "token cancelled during the import");
await ThrowsAsync<OperationCanceledException>(() => new OrderImporter(new RecordingValidator()).ImportAsync(path, new CancellationToken(true)), "token cancelled before the import");
var crm = new EmailDomainValidator(new[] { "example.com" });
await ThrowsAsync<OperationCanceledException>(() => crm.ValidateAsync(new Order("X", "x@example.com", 1m), new CancellationToken(true)), "EmailDomainValidator honours its token");
Check(await crm.ValidateAsync(new Order("X", "x@EXAMPLE.com", 1m), CancellationToken.None), "EmailDomainValidator accepts allowed domains");
Check(!await crm.ValidateAsync(new Order("Y", "y@example.net", 1m), CancellationToken.None), "EmailDomainValidator rejects other domains");

await ThrowsAsync<FormatException>(() => new OrderImporter(new RecordingValidator()).ImportAsync(badPath), "bad row", e => e.Message.Contains("line 3"));
await ThrowsAsync<FileNotFoundException>(() => new OrderImporter(new RecordingValidator()).ImportAsync(Path.Combine(dir, "missing.csv")), "missing file");
await ThrowsAsync<ArgumentNullException>(() => new OrderImporter(new RecordingValidator()).ImportAsync(null!), "null path");
await ThrowsAsync<ArgumentException>(() => new OrderImporter(new RecordingValidator()).ImportAsync(""), "empty path");
await ThrowsAsync<ArgumentException>(() => new OrderImporter(new RecordingValidator()).ImportAsync("   "), "whitespace path");
await ThrowsAsync<ArgumentNullException>(() => { _ = new OrderImporter(null!); return Task.CompletedTask; }, "null validator");

var gate = new TaskCompletionSource(TaskCreationOptions.RunContinuationsAsynchronously);
var gated = new RecordingValidator { Gate = gate.Task };
Task? pending = null;
var caller = new Thread(() => pending = new OrderImporter(gated).ImportAsync(path));
caller.Start();
bool returned = caller.Join(TimeSpan.FromSeconds(3));
gate.SetResult();
caller.Join();
Check(returned, "ImportAsync blocked its caller while validation was pending");
await pending!;
Check(gated.Tokens.Count == 3, "import finished after the validator answered");
Console.WriteLine("ok");

static void Check(bool ok, string message)
{
    if (!ok)
    {
        Console.Error.WriteLine("FAIL: " + message);
        Environment.Exit(1);
    }
}

static async Task ThrowsAsync<T>(Func<Task> action, string what, Func<T, bool>? matches = null) where T : Exception
{
    try
    {
        await action();
    }
    catch (T e) when (matches is null || matches(e))
    {
        return;
    }
    catch (Exception e)
    {
        Check(false, $"{what}: expected {typeof(T).Name}, got {e.GetType().Name}: {e.Message}");
    }
    Check(false, $"{what}: expected {typeof(T).Name}, nothing thrown");
}

sealed class RecordingValidator : IOrderValidator
{
    public ConcurrentQueue<CancellationToken> Tokens { get; } = new();
    public string? Reject { get; init; }
    public Action? AfterValidate { get; init; }
    public Task? Gate { get; init; }

    public async Task<bool> ValidateAsync(Order order, CancellationToken cancellationToken)
    {
        cancellationToken.ThrowIfCancellationRequested();
        Tokens.Enqueue(cancellationToken);
        await (Gate ?? Task.Delay(1, CancellationToken.None)).ConfigureAwait(false);
        AfterValidate?.Invoke();
        return order.Id != Reject;
    }
}
