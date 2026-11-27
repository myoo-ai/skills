using System.Globalization;
using Example.Pricing;

string path = Path.Combine(AppContext.BaseDirectory, "prices.txt");
(List<PriceLine> lines, int rejected) = PriceLineParser.ParseAll(File.ReadLines(path));

foreach (PriceLine line in lines)
{
    Console.WriteLine(string.Create(CultureInfo.InvariantCulture, $"{line.Sku} {line.Region} {line.Quantity} x {line.UnitPrice}"));
}
Console.WriteLine($"parsed {lines.Count}, rejected {rejected}");
