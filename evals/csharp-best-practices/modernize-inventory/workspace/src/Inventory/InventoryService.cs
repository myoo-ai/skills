using System;
using System.Collections.Generic;

namespace Example.Inventory
{
    public class InventoryService
    {
        private readonly IProductRepository repository;
        private readonly object sync = new object();
        private readonly Dictionary<string, int> stock = new Dictionary<string, int>();

        public InventoryService(IProductRepository repository)
        {
            if (repository == null)
            {
                throw new ArgumentNullException("repository");
            }
            this.repository = repository;
        }

        public Product Find(string sku)
        {
            if (sku == null)
            {
                throw new ArgumentNullException("sku");
            }
            foreach (Product product in repository.All())
            {
                if (string.Equals(product.Sku, sku, StringComparison.Ordinal))
                {
                    return product;
                }
            }
            return null;
        }

        public void Receive(string sku, int quantity)
        {
            if (quantity <= 0)
            {
                throw new ArgumentOutOfRangeException("quantity", quantity, "quantity must be positive");
            }
            if (Find(sku) == null)
            {
                throw new ArgumentException("unknown sku: " + sku, "sku");
            }
            lock (sync)
            {
                int current;
                if (stock.TryGetValue(sku, out current))
                {
                    stock[sku] = current + quantity;
                }
                else
                {
                    stock[sku] = quantity;
                }
            }
        }

        public int OnHand(string sku)
        {
            lock (sync)
            {
                int current;
                if (stock.TryGetValue(sku, out current))
                {
                    return current;
                }
                return 0;
            }
        }

        public string PriceBand(Product product)
        {
            if (product == null)
            {
                throw new ArgumentNullException("product");
            }
            if (product.Price == 0)
            {
                return "free";
            }
            else if (product.Price < 10)
            {
                return "budget";
            }
            else if (product.Price < 100)
            {
                return "standard";
            }
            else
            {
                return "premium";
            }
        }

        public List<string> Categories()
        {
            List<string> result = new List<string>();
            foreach (Product product in repository.All())
            {
                if (product.Category != null && !result.Contains(product.Category))
                {
                    result.Add(product.Category);
                }
            }
            result.Sort(StringComparer.Ordinal);
            return result;
        }
    }
}
