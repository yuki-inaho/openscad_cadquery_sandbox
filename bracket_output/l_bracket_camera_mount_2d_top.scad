// L字カメラマウントブラケット - トップビュー (2D投影)
// CadQueryから生成

// 3Dモデルをインポート
module bracket_3d() {
    import("l_bracket_camera_mount.stl");
}

// トップビュー (上から見た図)
projection(cut=false) {
    bracket_3d();
}
