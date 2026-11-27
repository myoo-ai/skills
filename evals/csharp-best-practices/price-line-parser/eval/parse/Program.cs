using System.Globalization;
using Example.Pricing;

CultureInfo turkish = CultureInfo.GetCultureInfo("tr-TR");
Check("IN".ToLower(turkish) != "in", "the runtime has Turkish casing rules (ICU)");
CultureInfo.CurrentCulture = turkish;
CultureInfo.CurrentUICulture = turkish;

string[] good =
[
    "ABC-1004 IN 3 2.25",
    "ABC-1005 id 1 10",
    "XY-200 uK 6 0.4999",
    "  ABC-1001 eu 12 9.99  ",
    "XY-202 Tr 2 3.50",
];
PriceLine[] expected =
[
    new("ABC-1004", "India", 3, 2.25m),
    new("ABC-1005", "Indonesia", 1, 10m),
    new("XY-200", "United Kingdom", 6, 0.4999m),
    new("ABC-1001", "Europe", 12, 9.99m),
    new("XY-202", "Türkiye", 2, 3.50m),
];
string[] bad =
[
    "",
    "# supplier comment",
    "ABC-1003 xx 5 1.00",
    "XY-201 tr 0 3.50",
    "QQ-777 eu 99999999999 1",
    "ZZZ 5 eu 1",
    "ABC-1001 eu 12 9.99.1",
    "ABC-1001 ıd 1 10",
];

for (int i = 0; i < good.Length; i++)
{
    PriceLine parsed = Parse(good[i]);
    Check(parsed == expected[i], $"Parse(\"{good[i]}\") under tr-TR gave {parsed}, want {expected[i]}");
    Check(PriceLineParser.TryParse(good[i], out var tried) && tried == expected[i], $"TryParse(\"{good[i]}\") under tr-TR");
}

foreach (string line in bad)
{
    try
    {
        PriceLineParser.Parse(line);
        Check(false, $"Parse(\"{line}\") must throw FormatException, nothing thrown");
    }
    catch (FormatException)
    {
    }
    catch (Exception e)
    {
        Check(false, $"Parse(\"{line}\") must throw FormatException, got {e.GetType().Name}");
    }
}

int thrown = 0;
AppDomain.CurrentDomain.FirstChanceException += (_, _) => Interlocked.Increment(ref thrown);
foreach (string line in bad)
{
    Check(!PriceLineParser.TryParse(line, out _), $"TryParse(\"{line}\") returns false");
}
var (lines, rejected) = PriceLineParser.ParseAll([.. good, .. bad]);
Check(thrown == 0, $"TryParse and ParseAll threw {thrown} exception(s) internally for rejected lines");
Check(lines.Count == good.Length && rejected == bad.Length && lines.SequenceEqual(expected), "ParseAll");

Console.WriteLine("ok");
return 0;

static PriceLine Parse(string line)
{
    try
    {
        return PriceLineParser.Parse(line);
    }
    catch (Exception e)
    {
        Check(false, $"Parse(\"{line}\") under tr-TR threw {e.GetType().Name}: {e.Message}");
        throw;
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
