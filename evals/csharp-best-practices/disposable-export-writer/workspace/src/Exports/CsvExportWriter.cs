using System.Globalization;

namespace Example.Exports;

/// <summary>Writes stock rows to a CSV file. Call Close when done.</summary>
public class CsvExportWriter
{
    private readonly FileStream _stream;
    private readonly StreamWriter _writer;
    private int _rows;

    public CsvExportWriter(string path)
    {
        _stream = new FileStream(path, FileMode.Create, FileAccess.Write, FileShare.None);
        _writer = new StreamWriter(_stream);
        _writer.WriteLine("sku,quantity,price");
    }

    public int RowsWritten => _rows;

    public void WriteRow(StockRow row)
    {
        _writer.WriteLine(Format(row));
        _rows++;
    }

    public async Task WriteRowAsync(StockRow row, CancellationToken cancellationToken = default)
    {
        await _writer.WriteLineAsync(Format(row).AsMemory(), cancellationToken).ConfigureAwait(false);
        _rows++;
    }

    public void Close()
    {
        _writer.Flush();
        _writer.Close();
        _stream.Close();
    }

    private static string Format(StockRow row) =>
        string.Create(CultureInfo.InvariantCulture, $"{row.Sku},{row.Quantity},{row.Price:0.00}");
}
