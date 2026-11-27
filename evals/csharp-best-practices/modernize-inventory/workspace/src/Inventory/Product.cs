using System;

namespace Example.Inventory
{
    public class Product
    {
        private readonly string sku;
        private readonly string name;
        private readonly decimal price;
        private readonly string category;

        public Product(string sku, string name, decimal price, string category)
        {
            this.sku = sku;
            this.name = name;
            this.price = price;
            this.category = category;
        }

        public string Sku
        {
            get { return sku; }
        }

        public string Name
        {
            get { return name; }
        }

        public decimal Price
        {
            get { return price; }
        }

        public string Category
        {
            get { return category; }
        }

        public override bool Equals(object obj)
        {
            Product other = obj as Product;
            if (other == null)
            {
                return false;
            }
            return sku == other.sku && name == other.name && price == other.price && category == other.category;
        }

        public override int GetHashCode()
        {
            return HashCode.Combine(sku, name, price, category);
        }

        public override string ToString()
        {
            return "Product { Sku = " + sku + ", Name = " + name + ", Price = " + price + ", Category = " + category + " }";
        }
    }
}
