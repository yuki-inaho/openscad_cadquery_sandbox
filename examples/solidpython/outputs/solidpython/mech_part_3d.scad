difference() {
	union() {
		cube(center = true, size = [80, 60, 5]);
		translate(v = [0, 0, 7]) {
			cylinder($fn = 50, center = true, h = 10, r = 12);
		}
		translate(v = [0, 0, 2.5]) {
			cube(center = true, size = [4, 60, 10]);
		}
		translate(v = [0, 0, 2.5]) {
			cube(center = true, size = [80, 4, 10]);
		}
	}
	translate(v = [-30, -20, 0]) {
		cylinder($fn = 30, center = true, h = 6, r = 3);
	}
	translate(v = [30, -20, 0]) {
		cylinder($fn = 30, center = true, h = 6, r = 3);
	}
	translate(v = [-30, 20, 0]) {
		cylinder($fn = 30, center = true, h = 6, r = 3);
	}
	translate(v = [30, 20, 0]) {
		cylinder($fn = 30, center = true, h = 6, r = 3);
	}
	translate(v = [0, 0, 7]) {
		cylinder($fn = 40, center = true, h = 12, r = 6);
	}
}
