namespace Example.Exports;

public static class StockExporter
{
    public static int Export(string path, IEnumerable<StockRow> rows)
    {
        CsvExportWriter writer = new CsvExportWriter(path);
        try
        {
            foreach (StockRow row in rows)
            {
                writer.WriteRow(row);
            }
            return writer.RowsWritten;
        }
        finally
        {
            writer.Close();
        }
    }

    public static async Task<int> ExportAsync(string path, IAsyncEnumerable<StockRow> rows, CancellationToken cancellationToken = default)
    {
        CsvExportWriter writer = new CsvExportWriter(path);
        try
        {
            await foreach (StockRow row in rows.WithCancellation(cancellationToken).ConfigureAwait(false))
            {
                await writer.WriteRowAsync(row, cancellationToken).ConfigureAwait(false);
            }
            return writer.RowsWritten;
        }
        finally
        {
            writer.Close();
        }
    }

    public static string Preview(string path, int maxLines)
    {
        StreamReader reader = new StreamReader(path);
        try
        {
            var lines = new List<string>();
            string? line;
            while (lines.Count < maxLines && (line = reader.ReadLine()) is not null)
            {
                lines.Add(line);
            }
            return string.Join(Environment.NewLine, lines);
        }
        finally
        {
            reader.Dispose();
        }
    }
}
