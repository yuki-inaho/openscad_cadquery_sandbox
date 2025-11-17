// L字カメラマウントブラケット - サイドビュー (2D投影)
// CadQueryから生成

// 3Dモデルをインポート
module bracket_3d() {
    import("l_bracket_camera_mount.stl");
}

// サイドビュー (側面から見た図 - L字形状が見える)
projection(cut=false) {
    rotate([90, 0, 90]) bracket_3d();
}
