package com.example.shapes;

import java.util.ArrayList;
import java.util.Collections;
import java.util.Comparator;
import java.util.List;
import java.util.Locale;
import java.util.stream.Collectors;

public final class Drawing {

    private final String title;
    private final List<Shape> shapes;

    public Drawing(String title, List<Shape> shapes) {
        this.title = title;
        this.shapes = shapes;
    }

    public String getTitle() {
        return title;
    }

    public List<Shape> getShapes() {
        return shapes;
    }

    public double totalArea() {
        double total = 0;
        for (Shape shape : shapes) {
            total += Geometry.area(shape);
        }
        return total;
    }

    public List<Shape> largest(int n) {
        List<Shape> sorted = new ArrayList<Shape>(shapes);
        Collections.sort(sorted, new Comparator<Shape>() {
            @Override
            public int compare(Shape a, Shape b) {
                return Double.compare(Geometry.area(b), Geometry.area(a));
            }
        });
        return sorted.stream().limit(n).collect(Collectors.toList());
    }

    public String report() {
        StringBuilder sb = new StringBuilder();
        sb.append("Drawing: " + title + "\n");
        sb.append("Shapes: " + shapes.size() + "\n");
        sb.append("Total area: " + String.format(Locale.ROOT, "%.2f", totalArea()) + "\n");
        sb.append("Largest: " + Geometry.describe(largest(1).get(0)) + "\n");
        return sb.toString();
    }
}
