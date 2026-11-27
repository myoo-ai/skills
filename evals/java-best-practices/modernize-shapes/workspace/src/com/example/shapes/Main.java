package com.example.shapes;

import java.util.ArrayList;
import java.util.List;
import java.util.Locale;

public final class Main {

    private Main() {
    }

    public static void main(String[] args) {
        List<Shape> shapes = new ArrayList<Shape>();
        shapes.add(new Circle(1.5));
        shapes.add(new Rectangle(2, 3));
        shapes.add(new Rectangle(2, 2));
        shapes.add(new Triangle(4, 5));

        Drawing drawing = new Drawing("demo", shapes);
        System.out.print(drawing.report());
        for (Shape shape : drawing.largest(3)) {
            System.out.println("- " + Geometry.describe(shape) + " area="
                    + String.format(Locale.ROOT, "%.2f", Geometry.area(shape)));
        }
    }
}
