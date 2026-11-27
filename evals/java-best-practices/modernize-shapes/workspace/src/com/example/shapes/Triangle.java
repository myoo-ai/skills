package com.example.shapes;

public final class Triangle extends Shape {

    private final double base;
    private final double height;

    public Triangle(double base, double height) {
        this.base = base;
        this.height = height;
    }

    public double getBase() {
        return base;
    }

    public double getHeight() {
        return height;
    }

    @Override
    public <R> R accept(ShapeVisitor<R> visitor) {
        return visitor.visitTriangle(this);
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) {
            return true;
        }
        if (!(o instanceof Triangle)) {
            return false;
        }
        Triangle other = (Triangle) o;
        return Double.compare(base, other.base) == 0
                && Double.compare(height, other.height) == 0;
    }

    @Override
    public int hashCode() {
        return 31 * Double.hashCode(base) + Double.hashCode(height);
    }

    @Override
    public String toString() {
        return "Triangle[base=" + base + ", height=" + height + "]";
    }
}
