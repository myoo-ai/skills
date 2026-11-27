using System.Globalization;

namespace Example.Orders;

public sealed class OrderImporter
{
    private readonly IOrderValidator _validator;

    public OrderImporter(IOrderValidator validator)
    {
        _validator = validator;
    }

    public List<Order> Import(string path)
    {
        var orders = new List<Order>();
        try
        {
            string[] lines = File.ReadAllLines(path);
            for (int i = 1; i < lines.Length; i++)
            {
                if (string.IsNullOrWhiteSpace(lines[i]))
                {
                    continue;
                }
                Order order = Parse(lines[i], i + 1);
                if (_validator.ValidateAsync(order).Result)
                {
                    orders.Add(order);
                }
            }
        }
        catch (Exception ex)
        {
            Console.WriteLine("import failed: " + ex.Message);
            throw new InvalidOperationException("import failed: " + ex.Message);
        }
        return orders;
    }

    private static Order Parse(string line, int lineNumber)
    {
        string[] fields = line.Split(',');
        if (fields.Length != 3)
        {
            throw new FormatException($"line {lineNumber}: expected 3 fields, got {fields.Length}");
        }
        if (!decimal.TryParse(fields[2].Trim(), NumberStyles.Number, CultureInfo.InvariantCulture, out decimal total))
        {
            throw new FormatException($"line {lineNumber}: invalid total '{fields[2].Trim()}'");
        }
        return new Order(fields[0].Trim(), fields[1].Trim(), total);
    }
}
