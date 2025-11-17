include </usr/local/lib/python3.11/dist-packages/solid2/extensions/bosl2/BOSL2/version.scad>;
include </usr/local/lib/python3.11/dist-packages/solid2/extensions/bosl2/BOSL2/constants.scad>;
include </usr/local/lib/python3.11/dist-packages/solid2/extensions/bosl2/BOSL2/transforms.scad>;
include </usr/local/lib/python3.11/dist-packages/solid2/extensions/bosl2/BOSL2/distributors.scad>;
include </usr/local/lib/python3.11/dist-packages/solid2/extensions/bosl2/BOSL2/miscellaneous.scad>;
include </usr/local/lib/python3.11/dist-packages/solid2/extensions/bosl2/BOSL2/color.scad>;
include </usr/local/lib/python3.11/dist-packages/solid2/extensions/bosl2/BOSL2/attachments.scad>;
include </usr/local/lib/python3.11/dist-packages/solid2/extensions/bosl2/BOSL2/beziers.scad>;
include </usr/local/lib/python3.11/dist-packages/solid2/extensions/bosl2/BOSL2/shapes3d.scad>;
include </usr/local/lib/python3.11/dist-packages/solid2/extensions/bosl2/BOSL2/shapes2d.scad>;
include </usr/local/lib/python3.11/dist-packages/solid2/extensions/bosl2/BOSL2/drawing.scad>;
include </usr/local/lib/python3.11/dist-packages/solid2/extensions/bosl2/BOSL2/masks3d.scad>;
include </usr/local/lib/python3.11/dist-packages/solid2/extensions/bosl2/BOSL2/masks2d.scad>;
include </usr/local/lib/python3.11/dist-packages/solid2/extensions/bosl2/BOSL2/math.scad>;
include </usr/local/lib/python3.11/dist-packages/solid2/extensions/bosl2/BOSL2/paths.scad>;
include </usr/local/lib/python3.11/dist-packages/solid2/extensions/bosl2/BOSL2/lists.scad>;
include </usr/local/lib/python3.11/dist-packages/solid2/extensions/bosl2/BOSL2/comparisons.scad>;
include </usr/local/lib/python3.11/dist-packages/solid2/extensions/bosl2/BOSL2/linalg.scad>;
include </usr/local/lib/python3.11/dist-packages/solid2/extensions/bosl2/BOSL2/trigonometry.scad>;
include </usr/local/lib/python3.11/dist-packages/solid2/extensions/bosl2/BOSL2/vectors.scad>;
include </usr/local/lib/python3.11/dist-packages/solid2/extensions/bosl2/BOSL2/affine.scad>;
include </usr/local/lib/python3.11/dist-packages/solid2/extensions/bosl2/BOSL2/coords.scad>;
include </usr/local/lib/python3.11/dist-packages/solid2/extensions/bosl2/BOSL2/geometry.scad>;
include </usr/local/lib/python3.11/dist-packages/solid2/extensions/bosl2/BOSL2/regions.scad>;
include </usr/local/lib/python3.11/dist-packages/solid2/extensions/bosl2/BOSL2/strings.scad>;
include </usr/local/lib/python3.11/dist-packages/solid2/extensions/bosl2/BOSL2/vnf.scad>;
include </usr/local/lib/python3.11/dist-packages/solid2/extensions/bosl2/BOSL2/structs.scad>;
include </usr/local/lib/python3.11/dist-packages/solid2/extensions/bosl2/BOSL2/rounding.scad>;
include </usr/local/lib/python3.11/dist-packages/solid2/extensions/bosl2/BOSL2/skin.scad>;
include </usr/local/lib/python3.11/dist-packages/solid2/extensions/bosl2/BOSL2/utility.scad>;
include </usr/local/lib/python3.11/dist-packages/solid2/extensions/bosl2/BOSL2/partitions.scad>;

difference() {
	union() {
		cylinder(center = true, h = 5, r = 15, segments = 50);
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
	cylinder(center = true, h = 6, r = 5, segments = 40);
}
