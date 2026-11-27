package com.example.shapes;

public final class Geometry {

    private Geometry() {
    }

    public static double area(Shape shape) {
        return shape.accept(new AreaVisitor()).doubleValue();
    }

    public static String describe(Shape shape) {
        if (shape instanceof Circle) {
            Circle circle = (Circle) shape;
            return "circle r=" + circle.getRadius();
        } else if (shape instanceof Rectangle) {
            Rectangle rectangle = (Rectangle) shape;
            if (rectangle.getWidth() == rectangle.getHeight()) {
                return "square " + rectangle.getWidth();
            }
            return "rectangle " + rectangle.getWidth() + "x" + rectangle.getHeight();
        } else if (shape instanceof Triangle) {
            Triangle triangle = (Triangle) shape;
            return "triangle b=" + triangle.getBase() + " h=" + triangle.getHeight();
        } else {
            throw new IllegalArgumentException("unknown shape: " + shape);
        }
    }
}
