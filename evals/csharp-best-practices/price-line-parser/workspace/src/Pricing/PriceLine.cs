namespace Example.Pricing;

public sealed record PriceLine(string Sku, string Region, int Quantity, decimal UnitPrice);
