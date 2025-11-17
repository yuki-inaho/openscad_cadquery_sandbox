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
		cube(center = true, size = [80, 60, 5]);
		translate(v = [0, 0, 7]) {
			cylinder(center = true, h = 10, r = 12, segments = 50);
		}
		translate(v = [0, 0, 2.5]) {
			cube(center = true, size = [4, 60, 10]);
		}
		translate(v = [0, 0, 2.5]) {
			cube(center = true, size = [80, 4, 10]);
		}
	}
	translate(v = [-30, -20, 0]) {
		cylinder(center = true, h = 6, r = 3, segments = 30);
	}
	translate(v = [30, -20, 0]) {
		cylinder(center = true, h = 6, r = 3, segments = 30);
	}
	translate(v = [-30, 20, 0]) {
		cylinder(center = true, h = 6, r = 3, segments = 30);
	}
	translate(v = [30, 20, 0]) {
		cylinder(center = true, h = 6, r = 3, segments = 30);
	}
	translate(v = [0, 0, 7]) {
		cylinder(center = true, h = 12, r = 6, segments = 40);
	}
}
