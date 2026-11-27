using System.Globalization;

namespace Example.Orders.Demo;

internal static class Program
{
    private static void Main(string[] args)
    {
        string path = args.Length > 0 ? args[0] : Path.Combine(AppContext.BaseDirectory, "orders.csv");
        var importer = new OrderImporter(new EmailDomainValidator(["example.com", "example.org"]));

        List<Order> orders = importer.Import(path);

        foreach (Order order in orders)
        {
            Console.WriteLine($"{order.Id} {order.Customer} {order.Total.ToString("0.00", CultureInfo.InvariantCulture)}");
        }
        decimal sum = orders.Sum(o => o.Total);
        Console.WriteLine($"imported {orders.Count} orders, total {sum.ToString("0.00", CultureInfo.InvariantCulture)}");
    }
}
