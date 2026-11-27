using System;
using System.Collections.Generic;

namespace Example.Inventory
{
    public class InMemoryProductRepository : IProductRepository
    {
        private readonly List<Product> products;

        public InMemoryProductRepository(IEnumerable<Product> products)
        {
            if (products == null)
            {
                throw new ArgumentNullException("products");
            }
            this.products = new List<Product>(products);
        }

        public IEnumerable<Product> All()
        {
            return products;
        }
    }
}
