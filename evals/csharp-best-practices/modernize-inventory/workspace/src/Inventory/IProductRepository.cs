using System.Collections.Generic;

namespace Example.Inventory
{
    public interface IProductRepository
    {
        IEnumerable<Product> All();
    }
}
