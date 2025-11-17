#!/usr/bin/env python3
"""
カメラ穴位置の検証スクリプト v2

目的:
- 現在の穴位置を視覚的に確認
- 複数の候補位置を生成して比較
- フィレット領域との干渉をチェック
- 適切な穴位置を特定
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import cadquery as cq
from scripts.cadquery_utils import export_dxf, save_model_with_openscad_support
from scripts.dxf_parser import parse_dxf


def create_bracket_with_custom_holes(camera_z_bottom, camera_z_top, include_fillet=False):
    """カスタム穴位置でL字ブラケットを生成"""
    t = 2.0
    horizontal_width = 80.0
    horizontal_depth = 50.0
    vertical_width = 80.0
    vertical_height = 40.0

    tripod_hole_diameter = 6.5
    tripod_x = 0.0
    tripod_y = -5.0

    camera_hole_diameter = 3.2
    camera_x_left = -31.5
    camera_x_right = 31.5

    # カメラ穴の回転前Y座標を計算
    vertical_plate_before_rotation_y_bottom = vertical_height/2 + t - camera_z_bottom
    vertical_plate_before_rotation_y_top = vertical_height/2 + t - camera_z_top

    # 水平板
    horizontal_plate = (
        cq.Workplane("XY")
        .box(horizontal_width, horizontal_depth, t, centered=(True, True, False))
    )

    # 垂直板
    vertical_plate = (
        cq.Workplane("XY")
        .box(vertical_width, vertical_height, t, centered=(True, True, False))
        .faces(">Z")
        .workplane()
        .pushPoints([
            (camera_x_left, vertical_plate_before_rotation_y_bottom),
            (camera_x_left, vertical_plate_before_rotation_y_top),
            (camera_x_right, vertical_plate_before_rotation_y_bottom),
            (camera_x_right, vertical_plate_before_rotation_y_top),
        ])
        .circle(camera_hole_diameter / 2)
        .cutThruAll()
        .rotate((0, 0, 0), (1, 0, 0), -90)
        .translate((0, -horizontal_depth/2, vertical_height/2 + t))
    )

    # Union
    bracket = horizontal_plate.union(vertical_plate)

    # 三脚穴
    bracket = (
        bracket
        .faces(">Z")
        .workplane()
        .center(tripod_x, tripod_y)
        .circle(tripod_hole_diameter / 2)
        .cutThruAll()
    )

    # フィレット（オプション）
    if include_fillet:
        try:
            # 内側フィレット
            bracket = bracket.edges("|X and >Z and <Y").fillet(3.0)
            print(f"  ✓ 内側フィレット適用成功: R3.0mm")
        except Exception as e:
            print(f"  ✗ 内側フィレット失敗: {e}")

        try:
            # 外側フィレット
            bracket = bracket.edges("|Z and >Y").fillet(1.5)
            print(f"  ✓ 外側フィレット適用成功: R1.5mm")
        except Exception as e:
            print(f"  ✗ 外側フィレット失敗: {e}")

    return bracket


def analyze_hole_position(z_bottom, z_top, label):
    """穴位置を解析"""
    print(f"\n=== {label} ===")
    print(f"  下穴: Z={z_bottom}mm (角から{z_bottom - 2}mm)")
    print(f"  上穴: Z={z_top}mm (角から{z_top - 2}mm)")
    print(f"  穴間隔: {z_top - z_bottom}mm")

    # 垂直板の範囲：Z=2～42mm（高さ40mm）
    vertical_range = 40.0
    relative_bottom = (z_bottom - 2) / vertical_range * 100
    relative_top = (z_top - 2) / vertical_range * 100

    print(f"  垂直板内の相対位置:")
    print(f"    下穴: {relative_bottom:.1f}%（下端からの位置）")
    print(f"    上穴: {relative_top:.1f}%（下端からの位置）")

    # フィレット（R3.0mm）との距離
    fillet_end_z = 2 + 3.0  # 5mm
    clearance_bottom = z_bottom - fillet_end_z
    print(f"  フィレット領域（Z=2～5mm）からのクリアランス:")
    print(f"    下穴: {clearance_bottom:.1f}mm")

    if clearance_bottom < 3:
        print(f"  ⚠️  下穴がフィレット領域に近すぎる（推奨: 3mm以上）")
    elif clearance_bottom < 5:
        print(f"  ⚠️  下穴のクリアランスがやや不足（推奨: 5mm以上）")
    else:
        print(f"  ✓ フィレット領域から十分離れている")


def export_comparison_dxf(bracket, z_bottom, z_top, prefix, output_dir):
    """比較用DXFをエクスポート"""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # XZ断面（Y=-24mm、垂直板中央）
    dxf_path = output_dir / f"{prefix}_xz_y-24.dxf"
    export_dxf(bracket, str(dxf_path), "XZ", -24.0)

    # YZ断面（X=0mm、中心）
    dxf_path_yz = output_dir / f"{prefix}_yz_x0.dxf"
    export_dxf(bracket, str(dxf_path_yz), "YZ", 0.0)

    return dxf_path


def verify_holes_in_dxf(dxf_path, expected_z_bottom, expected_z_top):
    """DXFファイルで穴位置を検証"""
    parser = parse_dxf(str(dxf_path))
    circles = parser.get_circles()

    # カメラ穴を抽出（φ3.2mm）
    camera_holes = [c for c in circles if abs(c['diameter'] - 3.2) < 0.2]

    print(f"\n  DXF検証: {dxf_path.name}")
    print(f"    検出されたカメラ穴: {len(camera_holes)}個")

    if len(camera_holes) >= 2:
        # Z座標を抽出（DXF座標系では符号反転）
        z_coords = sorted([abs(c['center'][1]) for c in camera_holes], reverse=True)
        print(f"    検出Z座標: {z_coords}")

        if len(z_coords) >= 2:
            actual_top = z_coords[0]
            actual_bottom = z_coords[1]

            error_bottom = abs(actual_bottom - expected_z_bottom)
            error_top = abs(actual_top - expected_z_top)

            print(f"    位置誤差:")
            print(f"      下穴: {error_bottom:.2f}mm")
            print(f"      上穴: {error_top:.2f}mm")

            if error_bottom < 0.5 and error_top < 0.5:
                print(f"    ✓ 穴位置が正確")
                return True
            else:
                print(f"    ⚠️  穴位置に誤差あり")
                return False
    else:
        print(f"    ✗ カメラ穴が不足")
        return False


def main():
    print("=" * 80)
    print("カメラ穴位置検証 v2")
    print("=" * 80)

    output_dir = Path("outputs/verify_camera_position")
    output_dir.mkdir(parents=True, exist_ok=True)

    # 候補リスト
    candidates = [
        ("current", 10.0, 18.0, "現在の実装"),
        ("option1", 15.0, 25.0, "案1: 中央寄り（角から13mm, 23mm）"),
        ("option2", 18.0, 28.0, "案2: さらに上（角から16mm, 26mm）"),
        ("option3", 20.0, 30.0, "案3: 中央～上部（角から18mm, 28mm）"),
        ("option4", 12.0, 22.0, "案4: やや上（角から10mm, 20mm）"),
    ]

    print("\n" + "=" * 80)
    print("【ステップ1】各候補の解析")
    print("=" * 80)

    for prefix, z_bottom, z_top, label in candidates:
        analyze_hole_position(z_bottom, z_top, label)

    print("\n" + "=" * 80)
    print("【ステップ2】各候補のモデル生成とDXF出力")
    print("=" * 80)

    for prefix, z_bottom, z_top, label in candidates:
        print(f"\n{label}...")
        bracket = create_bracket_with_custom_holes(z_bottom, z_top, include_fillet=False)
        dxf_path = export_comparison_dxf(bracket, z_bottom, z_top, prefix, output_dir)
        verify_holes_in_dxf(dxf_path, z_bottom, z_top)

    print("\n" + "=" * 80)
    print("【ステップ3】フィレット適用テスト")
    print("=" * 80)

    # 各候補でフィレットを試行
    for prefix, z_bottom, z_top, label in candidates:
        print(f"\n{label} + フィレット...")
        try:
            bracket = create_bracket_with_custom_holes(z_bottom, z_top, include_fillet=True)
            print(f"  ✓ フィレット適用成功")

            # フィレット付きモデルも保存
            dxf_path = export_comparison_dxf(bracket, z_bottom, z_top, f"{prefix}_fillet", output_dir)
        except Exception as e:
            print(f"  ✗ フィレット適用失敗: {e}")

    print("\n" + "=" * 80)
    print("推奨事項")
    print("=" * 80)
    print("\nDXFファイルを確認してください:")
    print(f"  {output_dir}/*_xz_y-24.dxf")
    print(f"  {output_dir}/*_yz_x0.dxf")
    print("\nL字の形状と穴位置を視覚的に比較し、最適な位置を選択してください。")
    print("\nフィレット（R3.0mm）が成功する候補を優先してください。")


if __name__ == "__main__":
    main()
