using Example.Exports;

string dir = Directory.CreateTempSubdirectory("exports").FullName;
string path = Path.Combine(dir, "stock.csv");

StockRow[] rows =
[
    new("A-100", 15, 4.5m),
    new("B-300", 2, 129m),
    new("C-400", 0, 0.99m),
];

int written = StockExporter.Export(path, rows);
Console.WriteLine($"exported {written} rows");
Console.WriteLine(StockExporter.Preview(path, 3));

int streamed = await StockExporter.ExportAsync(path, Stream(rows));
Console.WriteLine($"exported {streamed} rows async");

var writer = new CsvExportWriter(path);
writer.WriteRow(new StockRow("D-500", 7, 12m));
writer.Close();
Console.WriteLine(StockExporter.Preview(path, 2));

Directory.Delete(dir, recursive: true);

static async IAsyncEnumerable<StockRow> Stream(IEnumerable<StockRow> rows)
{
    foreach (StockRow row in rows)
    {
        await Task.Yield();
        yield return row;
    }
}
