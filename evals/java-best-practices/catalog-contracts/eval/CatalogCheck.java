import com.example.catalog.*;
import java.lang.reflect.Method;
import java.lang.reflect.Modifier;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Optional;
import java.util.SortedSet;
import java.util.TreeSet;

public class CatalogCheck {
    static void check(boolean ok, String msg) {
        if (!ok) throw new AssertionError(msg);
    }

    static void throwsNpe(Runnable r, String msg) {
        try {
            r.run();
        } catch (NullPointerException expected) {
            return;
        }
        throw new AssertionError("no NullPointerException: " + msg);
    }

    static void tryClear(Runnable r) {
        try {
            r.run();
        } catch (UnsupportedOperationException expected) {
            // an unmodifiable view is fine, so is a copy
        }
    }

    public static void main(String[] args) throws Exception {
        Product mug = new Product("MUG-01", "Enamel mug", 1250);
        Product tote = new Product("TOTE-4", "Canvas tote", 1250);
        Product gift = new Product("GIFT-X", "Gift card", 5_000_000_000L);
        Product pen = new Product("PEN-05", "Pen", 299);
        Product cheapGift = new Product("GIFT-X", "Gift card", 2_500_000_000L);

        // value semantics
        Product mug2 = new Product("MUG-01", "Enamel mug", 1250);
        check(mug.equals(mug2) && mug.hashCode() == mug2.hashCode(), "equal products have equal hash codes");
        check(new HashSet<>(List.of(mug, mug2, tote, new Product("TOTE-4", "Canvas tote", 1250))).size() == 2, "HashSet removes duplicate products");
        check(!mug.equals(null) && !mug.equals("MUG-01"), "equals handles null and other types");
        for (Method m : Product.class.getMethods()) {
            check(!(m.getName().startsWith("set") && m.getParameterCount() == 1), "Product has no setter " + m.getName());
        }
        for (var f : Product.class.getDeclaredFields()) {
            check(Modifier.isStatic(f.getModifiers()) || Modifier.isFinal(f.getModifiers()), "field " + f.getName() + " is final");
        }
        throwsNpe(() -> new Product(null, "x", 1), "Product with null sku");
        throwsNpe(() -> new Product("X", null, 1), "Product with null name");

        // ordering by price, then a total order consistent with equals
        List<Product> all = List.of(gift, mug, pen, tote, cheapGift);
        for (Product a : all) {
            for (Product b : all) {
                check(Integer.signum(a.compareTo(b)) == -Integer.signum(b.compareTo(a)), "compareTo is antisymmetric for " + a + " / " + b);
                check((a.compareTo(b) == 0) == a.equals(b), "compareTo is consistent with equals for " + a + " / " + b);
            }
        }
        check(pen.compareTo(gift) < 0 && gift.compareTo(pen) > 0, "5 000 000 000 cents sorts after 299 cents");
        check(cheapGift.compareTo(gift) < 0, "2.5e9 cents sorts before 5e9 cents");
        throwsNpe(() -> mug.compareTo(null), "compareTo(null)");

        Catalog catalog = new Catalog();
        for (Product p : List.of(gift, mug, pen, tote)) {
            catalog.add(p);
        }
        throwsNpe(() -> catalog.add(null), "add(null) fails fast");
        check(catalog.getProducts().size() == 4, "null was not added");
        check(catalog.sortedByPrice().equals(List.of(pen, mug, tote, gift)), "sortedByPrice, ties by SKU, got " + catalog.sortedByPrice());
        check(new ArrayList<>(catalog.priceList()).equals(List.of(pen, mug, tote, gift)), "priceList keeps products with the same price, got " + catalog.priceList());
        check(new TreeSet<>(List.of(mug, tote)).size() == 2, "TreeSet keeps products with the same price");

        // lookups
        Optional<Product> found = catalog.find("TOTE-4");
        check(found.equals(Optional.of(tote)), "find existing SKU");
        check(catalog.find("NOPE").isEmpty(), "find missing SKU is empty, not null");

        // callers cannot change the catalog through what it returns
        tryClear(() -> catalog.getProducts().clear());
        tryClear(() -> catalog.getProducts().add(cheapGift));
        tryClear(() -> catalog.sortedByPrice().clear());
        tryClear(() -> catalog.priceList().clear());
        check(catalog.getProducts().size() == 4, "changing getProducts() changed the catalog");
        check(catalog.sortedByPrice().equals(List.of(pen, mug, tote, gift)), "changing returned collections changed the catalog");
        System.out.println("ok");
    }
}
