using System.Text.RegularExpressions;

namespace Example.Pricing;

public static class PriceLineParser
{
    private static readonly Dictionary<string, string> Regions = new Dictionary<string, string>
    {
        { "eu", "Europe" },
        { "us", "United States" },
        { "uk", "United Kingdom" },
        { "in", "India" },
        { "id", "Indonesia" },
        { "tr", "Türkiye" },
    };

    /// <summary>
    /// Parses a supplier price line such as <c>ABC-1234 eu 12 9.99</c>:
    /// SKU, region code (any case), pack quantity and unit price.
    /// </summary>
    /// <exception cref="FormatException">The line is not a valid price line.</exception>
    public static PriceLine Parse(string line)
    {
        Match match = new Regex(@"^\s*(?<sku>[A-Z]{2,4}-\d{3,6})\s+(?<region>[A-Za-z]{2})\s+(?<qty>\d+)\s+(?<price>\d+(\.\d{1,4})?)\s*$").Match(line);
        if (!match.Success)
        {
            throw new FormatException($"not a price line: '{line}'");
        }
        string code = match.Groups["region"].Value.ToLower();
        if (!Regions.ContainsKey(code))
        {
            throw new FormatException($"unknown region '{match.Groups["region"].Value}' in '{line}'");
        }
        int quantity;
        try
        {
            quantity = int.Parse(match.Groups["qty"].Value);
        }
        catch (OverflowException)
        {
            throw new FormatException($"quantity too large in '{line}'");
        }
        if (quantity == 0)
        {
            throw new FormatException($"zero quantity in '{line}'");
        }
        decimal price = decimal.Parse(match.Groups["price"].Value);
        return new PriceLine(match.Groups["sku"].Value, Regions[code], quantity, price);
    }

    /// <summary>Parses a line, returning false for anything Parse rejects.</summary>
    public static bool TryParse(string line, out PriceLine? result)
    {
        try
        {
            result = Parse(line);
            return true;
        }
        catch (FormatException)
        {
            result = null;
            return false;
        }
    }

    public static (List<PriceLine> Lines, int Rejected) ParseAll(IEnumerable<string> lines)
    {
        var parsed = new List<PriceLine>();
        int rejected = 0;
        foreach (string line in lines)
        {
            if (TryParse(line, out PriceLine? result))
            {
                parsed.Add(result!);
            }
            else
            {
                rejected++;
            }
        }
        return (parsed, rejected);
    }
}
