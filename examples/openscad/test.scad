// Simple test OpenSCAD file
// Creates a cube and a sphere

difference() {
    // Main cube
    cube([30, 30, 30], center=true);

    // Sphere to subtract from the cube
    sphere(r=20, $fn=50);
}

// Add a cylinder
translate([0, 0, -20])
    cylinder(h=10, r=5, $fn=30);
