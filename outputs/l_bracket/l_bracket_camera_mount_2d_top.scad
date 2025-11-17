// l_bracket_camera_mount - トップビュー (2D投影)

module model_3d() {
    import("l_bracket_camera_mount.stl");
}

// トップビュー (上から見た図)
projection(cut=false) {
    model_3d();
}
