using System;
using System.Collections.Generic;
using Example.Inventory;

namespace Example.Inventory.App
{
    internal static class Program
    {
        private static void Main()
        {
            List<Product> products = new List<Product>();
            products.Add(new Product("A-100", "Widget", 4.50m, "parts"));
            products.Add(new Product("A-200", "Gadget", 25m, "parts"));
            products.Add(new Product("B-300", "Toolbox", 149.99m, "tools"));
            products.Add(new Product("C-400", "Sticker", 0m, null));

            InventoryService service = new InventoryService(new InMemoryProductRepository(products));
            service.Receive("A-100", 10);
            service.Receive("A-100", 5);
            service.Receive("B-300", 2);

            foreach (Product product in products)
            {
                Console.WriteLine(product.Sku + " " + product.Name + ": " + service.OnHand(product.Sku) + " on hand, " + service.PriceBand(product));
            }
            Console.WriteLine("Categories: " + string.Join(", ", service.Categories()));

            Product missing = service.Find("Z-999");
            Console.WriteLine("Z-999: " + (missing == null ? "not found" : missing.Name));
            Console.WriteLine("Same product: " + products[0].Equals(new Product("A-100", "Widget", 4.50m, "parts")));
        }
    }
}
