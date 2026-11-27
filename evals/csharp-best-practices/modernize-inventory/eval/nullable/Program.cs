using System.Reflection;
using Example.Inventory;

var context = new NullabilityInfoContext();
var failures = new List<string>();
void Expect(NullabilityState actual, NullabilityState expected, string what)
{
    if (actual != expected) failures.Add($"{what}: {actual}, expected {expected}");
}

Expect(context.Create(typeof(Product).GetProperty("Category")!).ReadState, NullabilityState.Nullable, "Product.Category");
Expect(context.Create(typeof(Product).GetProperty("Sku")!).ReadState, NullabilityState.NotNull, "Product.Sku");
Expect(context.Create(typeof(Product).GetProperty("Name")!).ReadState, NullabilityState.NotNull, "Product.Name");
MethodInfo find = typeof(InventoryService).GetMethod("Find")!;
Expect(context.Create(find.ReturnParameter).ReadState, NullabilityState.Nullable, "Find return");
Expect(context.Create(find.GetParameters()[0]).ReadState, NullabilityState.NotNull, "Find sku");
MethodInfo categories = typeof(InventoryService).GetMethod("Categories")!;
Expect(context.Create(categories.ReturnParameter).ReadState, NullabilityState.NotNull, "Categories return");
foreach (string failure in failures) Console.Error.WriteLine("FAIL: " + failure);
return failures.Count == 0 ? 0 : 1;
