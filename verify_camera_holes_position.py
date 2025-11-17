#!/usr/bin/env python3
"""
カメラ穴の実際の3D座標を確認するスクリプト

垂直板の移動によるカメラ穴位置への影響を分析
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import cadquery as cq
from examples.cadquery.l_bracket_camera_mount import create_l_bracket_camera_mount


def analyze_camera_holes():
    """カメラ穴の実際の3D座標を分析"""

    print("=" * 80)
    print("カメラ穴位置の詳細分析")
    print("=" * 80)
    print()

    # パラメータ定義（l_bracket_camera_mount.pyと同じ）
    t = 2.0
    vertical_height = 40.0
    horizontal_depth = 50.0

    camera_z_bottom = t + 8.0    # 2 + 8 = 10
    camera_z_top = t + 16.0      # 2 + 16 = 18
    camera_x_left = -31.5
    camera_x_right = 31.5

    print("【仕様要件】")
    print(f"  カメラ穴（グローバル座標）:")
    print(f"    下列 Z = {camera_z_bottom}mm")
    print(f"    上列 Z = {camera_z_top}mm")
    print(f"    左列 X = {camera_x_left}mm")
    print(f"    右列 X = {camera_x_right}mm")
    print()

    print("【垂直板の位置】")
    print(f"  修正前（T字）: Z=[-20, 20]、中心 Z=0")
    print(f"  修正後（L字）: Z=[{t}, {t + vertical_height}]、中心 Z={vertical_height/2 + t}")
    print(f"  移動量: {vertical_height/2 + t}mm")
    print()

    print("【faces('<Y').workplane() の座標系】")
    print(f"  選択される面: Y=-{horizontal_depth/2}（垂直板の背面）")
    print(f"  workplane原点:")
    print(f"    - 修正前: グローバル(X=0, Y=-25, Z=0)")
    print(f"    - 修正後: グローバル(X=0, Y=-25, Z={vertical_height/2 + t})")
    print()

    print("【workplane座標 → グローバル座標の変換】")
    print(f"  グローバルZ = workplane原点Z - workplane Y座標")
    print(f"  （workplaneのY軸は、グローバルZの逆向き）")
    print()

    # 修正前の座標変換
    print("【修正前（T字）の座標変換】")
    print(f"  workplane原点Z = 0")
    print(f"  pushPoints座標: (-10, -18)")
    print(f"    workplane Y=-10 → グローバルZ = 0 - (-10) = 10 ✅")
    print(f"    workplane Y=-18 → グローバルZ = 0 - (-18) = 18 ✅")
    print()

    # 修正後の座標変換
    print("【修正後（L字）の座標変換】")
    workplane_origin_z = vertical_height/2 + t
    print(f"  workplane原点Z = {workplane_origin_z}")
    print(f"  pushPoints座標: (-10, -18)（変更なし）")
    print(f"    workplane Y=-10 → グローバルZ = {workplane_origin_z} - (-10) = {workplane_origin_z + 10} ❌")
    print(f"    workplane Y=-18 → グローバルZ = {workplane_origin_z} - (-18) = {workplane_origin_z + 18} ❌")
    print()

    print("【期待されるworkplane座標（修正後）】")
    # グローバルZ=10にするには
    workplane_y_for_z10 = -(camera_z_bottom - workplane_origin_z)
    workplane_y_for_z18 = -(camera_z_top - workplane_origin_z)
    print(f"  グローバルZ=10にするには:")
    print(f"    workplane Y = -(10 - {workplane_origin_z}) = {workplane_y_for_z10}")
    print(f"  グローバルZ=18にするには:")
    print(f"    workplane Y = -(18 - {workplane_origin_z}) = {workplane_y_for_z18}")
    print()

    print("=" * 80)
    print("【結論】")
    print("=" * 80)
    print(f"垂直板が{workplane_origin_z}mm上に移動したため、")
    print(f"カメラ穴のworkplane座標も調整する必要があります。")
    print()
    print(f"修正前: pushPoints([..., -10, -18])")
    print(f"修正後: pushPoints([..., {workplane_y_for_z10}, {workplane_y_for_z18}])")
    print()
    print(f"または、グローバル座標ベースで再計算:")
    print(f"  camera_z_bottom = {camera_z_bottom}（グローバル座標、変更なし）")
    print(f"  camera_z_top = {camera_z_top}（グローバル座標、変更なし）")
    print(f"  workplane座標 = -(グローバルZ - 垂直板中心Z)")
    print(f"  workplane座標 = -(グローバルZ - {workplane_origin_z})")
    print()

    # 実際のブラケットを生成して確認
    print("=" * 80)
    print("【実際のブラケットで確認】")
    print("=" * 80)

    bracket = create_l_bracket_camera_mount()
    bb = bracket.val().BoundingBox()

    print(f"\nバウンディングボックス:")
    print(f"  Z: [{bb.zmin:.2f}, {bb.zmax:.2f}]")
    print()

    # XZ断面でのDXF出力と解析
    from scripts.cadquery_utils import export_dxf
    from scripts.dxf_parser import parse_dxf

    output_dir = Path("outputs/verify_camera_holes")
    output_dir.mkdir(parents=True, exist_ok=True)

    dxf_path = output_dir / "camera_holes_xz.dxf"
    export_dxf(bracket, str(dxf_path), "XZ", -24.0)

    parser = parse_dxf(str(dxf_path))
    circles = parser.get_circles()

    print(f"XZ断面（Y=-24mm）で検出された円: {len(circles)}個")
    for i, c in enumerate(circles, 1):
        print(f"  {i}. X={c['center'][0]:.1f}, DXF_Y={c['center'][1]:.1f}, φ={c['diameter']:.2f}mm")

    if len(circles) >= 4:
        print()
        print("DXF Y座標（負値）→ グローバルZ座標の推定:")
        for i, c in enumerate(circles, 1):
            dxf_y = c['center'][1]
            estimated_global_z = -dxf_y  # DXFのYは負のグローバルZ
            print(f"  {i}. DXF Y={dxf_y:.1f} → グローバルZ≈{estimated_global_z:.1f}mm")

    print()


if __name__ == "__main__":
    analyze_camera_holes()
