// l_bracket_camera_mount - フロントビュー (2D投影)

module model_3d() {
    import("l_bracket_camera_mount.stl");
}

// フロントビュー (正面から見た図)
projection(cut=false) {
    rotate([90, 0, 0]) model_3d();
}
