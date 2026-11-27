package com.example.shapes;

public interface ShapeVisitor<R> {

    R visitCircle(Circle circle);

    R visitRectangle(Rectangle rectangle);

    R visitTriangle(Triangle triangle);
}
