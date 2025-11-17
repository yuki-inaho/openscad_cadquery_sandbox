// 2D投影（トップビュー）
// Original 3D model
module model_3d() {
difference() {
	union() {
		cylinder($fn = 50, center = true, h = 5, r = 15);
		rotate(a = [0, 0, 0.0]) {
			translate(v = [18, 0, 0]) {
				cube(center = true, size = [6, 4, 5]);
			}
		}
		rotate(a = [0, 0, 30.0]) {
			translate(v = [18, 0, 0]) {
				cube(center = true, size = [6, 4, 5]);
			}
		}
		rotate(a = [0, 0, 60.0]) {
			translate(v = [18, 0, 0]) {
				cube(center = true, size = [6, 4, 5]);
			}
		}
		rotate(a = [0, 0, 90.0]) {
			translate(v = [18, 0, 0]) {
				cube(center = true, size = [6, 4, 5]);
			}
		}
		rotate(a = [0, 0, 120.0]) {
			translate(v = [18, 0, 0]) {
				cube(center = true, size = [6, 4, 5]);
			}
		}
		rotate(a = [0, 0, 150.0]) {
			translate(v = [18, 0, 0]) {
				cube(center = true, size = [6, 4, 5]);
			}
		}
		rotate(a = [0, 0, 180.0]) {
			translate(v = [18, 0, 0]) {
				cube(center = true, size = [6, 4, 5]);
			}
		}
		rotate(a = [0, 0, 210.0]) {
			translate(v = [18, 0, 0]) {
				cube(center = true, size = [6, 4, 5]);
			}
		}
		rotate(a = [0, 0, 240.0]) {
			translate(v = [18, 0, 0]) {
				cube(center = true, size = [6, 4, 5]);
			}
		}
		rotate(a = [0, 0, 270.0]) {
			translate(v = [18, 0, 0]) {
				cube(center = true, size = [6, 4, 5]);
			}
		}
		rotate(a = [0, 0, 300.0]) {
			translate(v = [18, 0, 0]) {
				cube(center = true, size = [6, 4, 5]);
			}
		}
		rotate(a = [0, 0, 330.0]) {
			translate(v = [18, 0, 0]) {
				cube(center = true, size = [6, 4, 5]);
			}
		}
	}
	cylinder($fn = 40, center = true, h = 6, r = 5);
}

}

// Top view projection
projection(cut=false) model_3d();
