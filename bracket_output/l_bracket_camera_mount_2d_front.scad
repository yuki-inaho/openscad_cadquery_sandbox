// L字カメラマウントブラケット - フロントビュー (2D投影)
// CadQueryから生成

// 3Dモデルをインポート
module bracket_3d() {
    import("l_bracket_camera_mount.stl");
}

// フロントビュー (正面から見た図 - 垂直板のカメラ固定穴が見える)
projection(cut=false) {
    rotate([90, 0, 0]) bracket_3d();
}
