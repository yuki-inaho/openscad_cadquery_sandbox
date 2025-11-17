// 2D投影（トップビュー）
// Original 3D model
module model_3d() {
difference() {
	cube(center = true, size = [50, 40, 30]);
	translate(v = [0, 0, 2]) {
		cube(center = true, size = [44, 34, 30]);
	}
}

}

// Top view projection
projection(cut=false) model_3d();
