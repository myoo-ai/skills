package com.example.shapes;

public abstract class Shape {

    public abstract <R> R accept(ShapeVisitor<R> visitor);
}
