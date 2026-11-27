package com.example.shapes;

final class AreaVisitor implements ShapeVisitor<Double> {

    @Override
    public Double visitCircle(Circle circle) {
        return Math.PI * circle.getRadius() * circle.getRadius();
    }

    @Override
    public Double visitRectangle(Rectangle rectangle) {
        return rectangle.getWidth() * rectangle.getHeight();
    }

    @Override
    public Double visitTriangle(Triangle triangle) {
        return 0.5 * triangle.getBase() * triangle.getHeight();
    }
}
