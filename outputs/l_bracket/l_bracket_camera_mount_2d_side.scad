// l_bracket_camera_mount - サイドビュー (2D投影)

module model_3d() {
    import("l_bracket_camera_mount.stl");
}

// サイドビュー (側面から見た図)
projection(cut=false) {
    rotate([90, 0, 90]) model_3d();
}
