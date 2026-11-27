using Example.Inventory;

Product widget = new("A-1", "Widget", 4.50m, "parts");
Product sticker = new("C-4", "Sticker", 0m, null);
Product dearer = widget with { Price = 12m };
Check(widget == new Product("A-1", "Widget", 4.50m, "parts"), "Product has value equality with ==");
Check(dearer.Price == 12m && dearer.Sku == "A-1" && dearer != widget, "with-expression copies Product");

var service = new InventoryService(new InMemoryProductRepository(
    [widget, sticker, new Product("B-3", "Toolbox", 100m, "tools"), new Product("B-4", "Crate", 99.99m, "tools"), new Product("D-5", "Tape", 10m, "parts")]));
Check(service.PriceBand(sticker) == "free", "band free");
Check(service.PriceBand(widget) == "budget", "band budget");
Check(service.PriceBand(service.Find("D-5")!) == "standard", "band standard at 10");
Check(service.PriceBand(service.Find("B-4")!) == "standard", "band standard at 99.99");
Check(service.PriceBand(service.Find("B-3")!) == "premium", "band premium at 100");
Check(service.Categories().SequenceEqual(new[] { "parts", "tools" }), "categories");
Check(service.Find("A-1") == widget && service.Find("nope") is null, "Find");

Parallel.For(0, 1000, _ => service.Receive("A-1", 1));
service.Receive("B-3", 2);
Check(service.OnHand("A-1") == 1000 && service.OnHand("B-3") == 2 && service.OnHand("nope") == 0, "stock counts");

Throws<ArgumentNullException>(() => new InventoryService(null!), "repository");
Throws<ArgumentNullException>(() => new InMemoryProductRepository(null!), "products");
Throws<ArgumentNullException>(() => service.Find(null!), "sku");
Throws<ArgumentOutOfRangeException>(() => service.Receive("A-1", 0), "quantity");
Throws<ArgumentOutOfRangeException>(() => service.Receive("A-1", -5), "quantity");
Throws<ArgumentException>(() => service.Receive("nope", 1), "sku");
Throws<ArgumentNullException>(() => service.PriceBand(null!), "product");
Console.WriteLine("ok");

static void Check(bool ok, string message)
{
    if (!ok)
    {
        Console.Error.WriteLine("FAIL: " + message);
        Environment.Exit(1);
    }
}

static void Throws<T>(Action action, string paramName) where T : ArgumentException
{
    try
    {
        action();
    }
    catch (T e) when (e.ParamName == paramName)
    {
        return;
    }
    catch (Exception e)
    {
        Check(false, $"expected {typeof(T).Name} for {paramName}, got {e.GetType().Name} ({(e as ArgumentException)?.ParamName})");
    }
    Check(false, $"expected {typeof(T).Name} for {paramName}, nothing thrown");
}
