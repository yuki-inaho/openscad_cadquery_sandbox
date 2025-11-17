#!/usr/bin/env python3
"""
L字ブラケット仕様要件テスト

このテストは、L字ブラケットが以下の仕様要件を満たしているか確認します：

## 仕様要件

### 0. 用途・機能要件（非幾何）
- 三脚への取り付け機能
- カメラの固定機能
- L字形状による角度調整機能

### 1. 形状・寸法仕様
- 外形: 80mm x 50mm、板厚2.0mm
- L字形状（90度曲げ）
- 水平板: 三脚取り付け用穴 φ6.5mm、1個
- 垂直板: カメラ固定用穴 φ3.2mm (M3用)、4個
- 一体構造（unionで結合）
- フィレット: 外側エッジ R1.5mm以下

### 2. 座標系仕様
- 原点: 水平板中心底面
- X軸: 幅方向（-40〜+40mm）
- Y軸: 奥行き方向（-25〜+25mm）
- Z軸: 高さ方向（0〜42mm）

### 3. 穴位置仕様
- 三脚穴: 中心(0, -5, Z)、水平板中央、曲げ部から20mm
- カメラ穴:
  - X: -31.5mm (左列), +31.5mm (右列)
  - Z: 10mm (下列), 18mm (上列)
  - 2x2配置、合計4個
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import cadquery as cq
from examples.cadquery.l_bracket_camera_mount import create_l_bracket_camera_mount
from scripts.cadquery_utils import export_dxf
from scripts.dxf_parser import parse_dxf


class LBracketRequirements:
    """L字ブラケット仕様要件の定義"""

    # 形状・寸法
    WIDTH = 80.0  # mm
    DEPTH = 50.0  # mm
    THICKNESS = 2.0  # mm
    HORIZONTAL_PLATE_HEIGHT = 2.0  # mm (板厚)
    VERTICAL_PLATE_HEIGHT = 40.0  # mm
    TOTAL_HEIGHT = HORIZONTAL_PLATE_HEIGHT + VERTICAL_PLATE_HEIGHT  # 42mm

    # バウンディングボックス
    BBOX_X_MIN = -40.0
    BBOX_X_MAX = 40.0
    BBOX_Y_MIN = -25.0
    BBOX_Y_MAX = 25.0
    BBOX_Z_MIN = 0.0
    BBOX_Z_MAX = 42.0

    # 三脚穴
    TRIPOD_HOLE_DIAMETER = 6.5  # mm
    TRIPOD_HOLE_COUNT = 1
    TRIPOD_HOLE_X = 0.0
    TRIPOD_HOLE_Y = -5.0

    # カメラ穴
    CAMERA_HOLE_DIAMETER = 3.2  # mm (M3用)
    CAMERA_HOLE_COUNT = 4
    CAMERA_HOLE_X_LEFT = -31.5
    CAMERA_HOLE_X_RIGHT = 31.5
    CAMERA_HOLE_Z_BOTTOM = 10.0
    CAMERA_HOLE_Z_TOP = 18.0

    # 許容誤差
    TOLERANCE_DIMENSION = 0.5  # mm
    TOLERANCE_HOLE_DIAMETER = 0.2  # mm
    TOLERANCE_HOLE_POSITION = 1.0  # mm

    # フィレット
    FILLET_RADIUS_MAX = 1.5  # mm


def test_basic_structure():
    """基本構造のテスト"""

    print("=" * 80)
    print("【テスト1】基本構造")
    print("=" * 80)

    bracket = create_l_bracket_camera_mount()
    req = LBracketRequirements

    # ソリッド数（一体構造）
    solids = bracket.solids().vals()
    print(f"\nソリッド数: {len(solids)} 個 (期待: 1個)")
    assert len(solids) == 1, "❌ 一体構造ではない"
    print("  ✅ 一体構造")

    return bracket


def test_bounding_box(bracket):
    """バウンディングボックスのテスト"""

    print("\n" + "=" * 80)
    print("【テスト2】バウンディングボックス")
    print("=" * 80)

    req = LBracketRequirements
    bb = bracket.val().BoundingBox()

    tests = [
        ("X最小", bb.xmin, req.BBOX_X_MIN),
        ("X最大", bb.xmax, req.BBOX_X_MAX),
        ("Y最小", bb.ymin, req.BBOX_Y_MIN),
        ("Y最大", bb.ymax, req.BBOX_Y_MAX),
        ("Z最小", bb.zmin, req.BBOX_Z_MIN),
        ("Z最大", bb.zmax, req.BBOX_Z_MAX),
    ]

    all_pass = True
    for name, actual, expected in tests:
        diff = abs(actual - expected)
        passed = diff < req.TOLERANCE_DIMENSION
        status = "✅" if passed else "❌"
        print(f"\n{name}: {actual:.2f} mm (期待: {expected:.2f} mm, 誤差: {diff:.2f} mm)")
        print(f"  {status} {'PASS' if passed else 'FAIL'}")

        if not passed:
            all_pass = False

    # Z方向の特別なチェック（L字 vs T字）
    print("\n" + "-" * 80)
    if bb.zmin < -1:
        print("❌ 警告: Z最小値が0より大幅に小さい → T字形状の可能性")
        all_pass = False
    elif abs(bb.zmin - 0) < req.TOLERANCE_DIMENSION and abs(bb.zmax - req.BBOX_Z_MAX) < req.TOLERANCE_DIMENSION:
        print("✅ L字形状（水平板の上に垂直板が立っている）")
    else:
        print("⚠️  L字形状の位置が仕様と異なる")
        all_pass = False

    assert all_pass, "❌ バウンディングボックステスト失敗"
    print("\n✅ バウンディングボックステスト合格")


def test_tripod_hole(bracket):
    """三脚穴のテスト"""

    print("\n" + "=" * 80)
    print("【テスト3】三脚穴")
    print("=" * 80)

    req = LBracketRequirements
    output_dir = Path("outputs/test_requirements")
    output_dir.mkdir(parents=True, exist_ok=True)

    # XY断面でDXFエクスポート（Z=1mm、水平板の中央）
    dxf_path = output_dir / "tripod_hole_xy.dxf"
    export_dxf(bracket, str(dxf_path), "XY", 1.0)

    # DXF解析
    parser = parse_dxf(str(dxf_path))
    circles = parser.get_circles()

    print(f"\n検出された円: {len(circles)} 個 (期待: {req.TRIPOD_HOLE_COUNT}個)")

    # 穴の数
    assert len(circles) >= req.TRIPOD_HOLE_COUNT, f"❌ 三脚穴が不足（{len(circles)}個）"

    # 穴の直径とwosition
    tripod_holes = [c for c in circles if abs(c['diameter'] - req.TRIPOD_HOLE_DIAMETER) < req.TOLERANCE_HOLE_DIAMETER]

    if len(tripod_holes) == 0:
        print(f"❌ φ{req.TRIPOD_HOLE_DIAMETER}mmの穴が見つからない")
        for i, c in enumerate(circles, 1):
            print(f"  円{i}: φ{c['diameter']:.2f}mm at ({c['center'][0]:.1f}, {c['center'][1]:.1f})")
        assert False, "三脚穴の直径が不正"

    hole = tripod_holes[0]
    print(f"\n三脚穴: φ{hole['diameter']:.2f}mm at ({hole['center'][0]:.1f}, {hole['center'][1]:.1f})")

    # 位置チェック
    x_diff = abs(hole['center'][0] - req.TRIPOD_HOLE_X)
    y_diff = abs(hole['center'][1] - req.TRIPOD_HOLE_Y)

    print(f"  X位置誤差: {x_diff:.2f} mm (許容: {req.TOLERANCE_HOLE_POSITION} mm)")
    print(f"  Y位置誤差: {y_diff:.2f} mm (許容: {req.TOLERANCE_HOLE_POSITION} mm)")

    assert x_diff < req.TOLERANCE_HOLE_POSITION, f"❌ X位置が不正（誤差{x_diff:.2f}mm）"
    assert y_diff < req.TOLERANCE_HOLE_POSITION, f"❌ Y位置が不正（誤差{y_diff:.2f}mm）"

    print("\n✅ 三脚穴テスト合格")


def test_camera_holes(bracket):
    """カメラ穴のテスト"""

    print("\n" + "=" * 80)
    print("【テスト4】カメラ穴")
    print("=" * 80)

    req = LBracketRequirements
    output_dir = Path("outputs/test_requirements")
    output_dir.mkdir(parents=True, exist_ok=True)

    # XZ断面でDXFエクスポート（Y=-24mm、垂直板の中央）
    dxf_path = output_dir / "camera_holes_xz.dxf"
    export_dxf(bracket, str(dxf_path), "XZ", -24.0)

    # DXF解析
    parser = parse_dxf(str(dxf_path))
    circles = parser.get_circles()

    print(f"\n検出された円: {len(circles)} 個 (期待: {req.CAMERA_HOLE_COUNT}個)")

    # 穴の数
    assert len(circles) >= req.CAMERA_HOLE_COUNT, f"❌ カメラ穴が不足（{len(circles)}個）"

    # 穴の直径
    camera_holes = [c for c in circles if abs(c['diameter'] - req.CAMERA_HOLE_DIAMETER) < req.TOLERANCE_HOLE_DIAMETER]

    if len(camera_holes) < req.CAMERA_HOLE_COUNT:
        print(f"❌ φ{req.CAMERA_HOLE_DIAMETER}mmの穴が{req.CAMERA_HOLE_COUNT}個未満")
        for i, c in enumerate(circles, 1):
            print(f"  円{i}: φ{c['diameter']:.2f}mm at ({c['center'][0]:.1f}, {c['center'][1]:.1f})")
        assert False, "カメラ穴の直径が不正"

    print(f"\nφ{req.CAMERA_HOLE_DIAMETER}mmの穴: {len(camera_holes)} 個")
    for i, c in enumerate(camera_holes, 1):
        print(f"  穴{i}: ({c['center'][0]:.1f}, {c['center'][1]:.1f})")

    # 位置チェック（期待される4箇所）
    expected_positions = [
        (req.CAMERA_HOLE_X_LEFT, -req.CAMERA_HOLE_Z_BOTTOM),  # 左下（DXF座標系でZ反転）
        (req.CAMERA_HOLE_X_LEFT, -req.CAMERA_HOLE_Z_TOP),     # 左上
        (req.CAMERA_HOLE_X_RIGHT, -req.CAMERA_HOLE_Z_BOTTOM), # 右下
        (req.CAMERA_HOLE_X_RIGHT, -req.CAMERA_HOLE_Z_TOP),    # 右上
    ]

    print("\n位置検証:")
    for i, (exp_x, exp_y) in enumerate(expected_positions, 1):
        # 最も近い穴を探す
        min_dist = float('inf')
        closest_hole = None
        for hole in camera_holes:
            dist = ((hole['center'][0] - exp_x)**2 + (hole['center'][1] - exp_y)**2)**0.5
            if dist < min_dist:
                min_dist = dist
                closest_hole = hole

        print(f"  穴{i}: 期待({exp_x:.1f}, {exp_y:.1f}), 実際({closest_hole['center'][0]:.1f}, {closest_hole['center'][1]:.1f}), 誤差{min_dist:.2f}mm")
        assert min_dist < req.TOLERANCE_HOLE_POSITION, f"❌ 穴{i}の位置が不正"

    print("\n✅ カメラ穴テスト合格")


def test_l_shape_verification(bracket):
    """L字形状の検証"""

    print("\n" + "=" * 80)
    print("【テスト5】L字形状の検証")
    print("=" * 80)

    req = LBracketRequirements

    # 各方向の面を確認
    faces_y_min = bracket.faces("<Y").vals()
    faces_z_max = bracket.faces(">Z").vals()

    print(f"\nY最小面（垂直板の背面）: {len(faces_y_min)} 個")
    print(f"Z最大面（水平板の上面）: {len(faces_z_max)} 個")

    # L字の判定
    is_l_shape = len(faces_y_min) == 1 and len(faces_z_max) == 1

    if is_l_shape:
        print("\n✅ L字形状として正しい")
    else:
        print("\n❌ L字形状ではない可能性")
        assert False, "L字形状の検証失敗"


def run_all_tests():
    """全テストを実行"""

    print("=" * 80)
    print("L字ブラケット仕様要件テスト")
    print("=" * 80)
    print()

    try:
        # テスト実行
        bracket = test_basic_structure()
        test_bounding_box(bracket)
        test_tripod_hole(bracket)
        test_camera_holes(bracket)
        test_l_shape_verification(bracket)

        print("\n" + "=" * 80)
        print("🎉 全テスト合格！")
        print("=" * 80)
        print("\nL字ブラケットは仕様要件を満たしています。")
        return True

    except AssertionError as e:
        print("\n" + "=" * 80)
        print("❌ テスト失敗")
        print("=" * 80)
        print(f"\nエラー: {e}")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
