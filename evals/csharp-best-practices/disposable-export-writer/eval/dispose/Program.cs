using Example.Exports;

string dir = Directory.CreateTempSubdirectory("exports-check").FullName;
string path = Path.Combine(dir, "stock.csv");
string expected = "sku,quantity,price" + Environment.NewLine + "A-1,3,4.50" + Environment.NewLine;
StockRow row = new("A-1", 3, 4.5m);

Check(typeof(IDisposable).IsAssignableFrom(typeof(CsvExportWriter)), "CsvExportWriter is IDisposable");
Check(typeof(IAsyncDisposable).IsAssignableFrom(typeof(CsvExportWriter)), "CsvExportWriter is IAsyncDisposable");

using (var writer = (IDisposable)new CsvExportWriter(path))
{
    ((CsvExportWriter)writer).WriteRow(row);
}
Check(File.ReadAllText(path) == expected, "using block flushes the rows");
Check(Released(path), "using block releases the file");

await using (var writer = (IAsyncDisposable)new CsvExportWriter(path))
{
    await ((CsvExportWriter)writer).WriteRowAsync(row);
}
Check(File.ReadAllText(path) == expected, "await using flushes the rows");
Check(Released(path), "await using releases the file");

var twice = new CsvExportWriter(path);
((IDisposable)twice).Dispose();
NoThrow(() => ((IDisposable)twice).Dispose(), "second Dispose is harmless");
await NoThrowAsync(async () => await ((IAsyncDisposable)twice).DisposeAsync(), "DisposeAsync after Dispose is harmless");
Throws<ObjectDisposedException>(() => twice.WriteRow(row), "WriteRow after Dispose");

var twiceAsync = new CsvExportWriter(path);
await ((IAsyncDisposable)twiceAsync).DisposeAsync();
await NoThrowAsync(async () => await ((IAsyncDisposable)twiceAsync).DisposeAsync(), "second DisposeAsync is harmless");
NoThrow(() => ((IDisposable)twiceAsync).Dispose(), "Dispose after DisposeAsync is harmless");
Throws<ObjectDisposedException>(() => twiceAsync.WriteRowAsync(row).GetAwaiter().GetResult(), "WriteRowAsync after DisposeAsync");

Throws<InvalidDataException>(() => StockExporter.Export(path, Failing()), "Export passes the row source's exception on");
Check(Released(path), "Export releases the file when the rows fail");
Check(StockExporter.Export(path, [row, row]) == 2 && Released(path), "Export writes and releases");

Throws<InvalidDataException>(() => StockExporter.ExportAsync(path, FailingAsync()).GetAwaiter().GetResult(), "ExportAsync passes the row source's exception on");
Check(Released(path), "ExportAsync releases the file when the rows fail");
Check(await StockExporter.ExportAsync(path, FailingAsync(failAt: 99)) == 2 && Released(path), "ExportAsync writes and releases");
Check(StockExporter.Preview(path, 2) == "sku,quantity,price" + Environment.NewLine + "A-1,3,4.50" && Released(path), "Preview reads and releases");

Directory.Delete(dir, recursive: true);
Console.WriteLine("ok");
return 0;

IEnumerable<StockRow> Failing()
{
    yield return row;
    throw new InvalidDataException("bad row");
}

async IAsyncEnumerable<StockRow> FailingAsync(int failAt = 1)
{
    for (int i = 0; i < 2; i++)
    {
        await Task.Yield();
        if (i == failAt)
        {
            throw new InvalidDataException("bad row");
        }
        yield return row;
    }
}

static bool Released(string path)
{
    try
    {
        using var stream = new FileStream(path, FileMode.Open, FileAccess.ReadWrite, FileShare.None);
        return true;
    }
    catch (IOException)
    {
        return false;
    }
}

static void Check(bool ok, string message)
{
    if (!ok)
    {
        Console.Error.WriteLine("FAIL: " + message);
        Environment.Exit(1);
    }
}

static void NoThrow(Action action, string message)
{
    try
    {
        action();
    }
    catch (Exception e)
    {
        Check(false, $"{message}: threw {e.GetType().Name}");
    }
}

static async Task NoThrowAsync(Func<Task> action, string message)
{
    try
    {
        await action();
    }
    catch (Exception e)
    {
        Check(false, $"{message}: threw {e.GetType().Name}");
    }
}

static void Throws<T>(Action action, string message) where T : Exception
{
    try
    {
        action();
    }
    catch (T)
    {
        return;
    }
    catch (Exception e)
    {
        Check(false, $"{message}: expected {typeof(T).Name}, got {e.GetType().Name}");
    }
    Check(false, $"{message}: expected {typeof(T).Name}, nothing thrown");
}
