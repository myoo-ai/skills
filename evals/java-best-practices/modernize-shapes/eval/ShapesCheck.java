import com.example.shapes.*;
import java.util.ArrayList;
import java.util.List;

public class ShapesCheck {
    static void check(boolean ok, String msg) {
        if (!ok) throw new AssertionError(msg);
    }

    static void rejects(Runnable r, String msg) {
        try {
            r.run();
        } catch (IllegalArgumentException expected) {
            return;
        }
        throw new AssertionError("no IllegalArgumentException: " + msg);
    }

    public static void main(String[] args) {
        check(Shape.class.isInterface() && Shape.class.isSealed(), "Shape is a sealed interface");
        check(Shape.class.getPermittedSubclasses().length == 3, "Shape permits exactly 3 types");
        for (Class<?> c : List.of(Circle.class, Rectangle.class, Triangle.class, Drawing.class)) {
            check(c.isRecord(), c.getSimpleName() + " is a record");
        }
        check(new Circle(2.0).equals(new Circle(2.0)) && new Circle(2.0).radius() == 2.0, "Circle");
        check(new Rectangle(2, 3).width() == 2 && new Rectangle(2, 3).height() == 3, "Rectangle");
        check(new Triangle(4, 5).base() == 4 && new Triangle(4, 5).height() == 5, "Triangle");
        rejects(() -> new Circle(0), "Circle(0)");
        rejects(() -> new Circle(-1), "Circle(-1)");
        rejects(() -> new Rectangle(1, Double.NaN), "Rectangle(1, NaN)");
        rejects(() -> new Rectangle(-2, 1), "Rectangle(-2, 1)");
        rejects(() -> new Triangle(3, 0), "Triangle(3, 0)");
        check(Geometry.area(new Triangle(4, 5)) == 10.0, "triangle area");
        check(Math.abs(Geometry.area(new Circle(1)) - Math.PI) < 1e-9, "circle area");
        check(Geometry.describe(new Rectangle(2, 2)).equals("square 2.0"), "square");
        check(Geometry.describe(new Rectangle(2, 3)).equals("rectangle 2.0x3.0"), "rectangle");

        List<Shape> input = new ArrayList<>(List.of(new Circle(1), new Rectangle(2, 3)));
        Drawing drawing = new Drawing("t", input);
        input.add(new Triangle(1, 1));
        input.set(0, new Circle(9));
        check(drawing.title().equals("t"), "title()");
        check(drawing.shapes().equals(List.of(new Circle(1), new Rectangle(2, 3))), "Drawing copies its input list");
        try {
            drawing.shapes().add(new Circle(1));
            throw new AssertionError("shapes() is modifiable");
        } catch (UnsupportedOperationException expected) {
            // unmodifiable, as required
        }
        check(drawing.largest(1).equals(List.of(new Rectangle(2, 3))), "largest(1)");
        System.out.println("ok");
    }
}
