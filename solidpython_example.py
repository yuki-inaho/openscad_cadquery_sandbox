#!/usr/bin/env python3
"""
SolidPython2を使用した3Dモデル生成と2D図面出力の例
"""

from solid2 import *
from solid2.extensions.bosl2 import *


def create_mechanical_part():
    """機械部品のサンプルモデルを作成"""

    # ベースプレート
    base = cube([80, 60, 5], center=True)

    # 取り付け穴（四隅）
    mounting_holes = []
    hole_positions = [
        [-30, -20, 0],
        [30, -20, 0],
        [-30, 20, 0],
        [30, 20, 0]
    ]

    for pos in hole_positions:
        hole = translate(pos)(cylinder(h=6, r=3, segments=30, center=True))
        mounting_holes.append(hole)

    # ボス（中央の突起）
    boss = translate([0, 0, 7])(cylinder(h=10, r=12, segments=50, center=True))

    # ボスの中央穴
    center_hole = translate([0, 0, 7])(cylinder(h=12, r=6, segments=40, center=True))

    # リブ（補強材）
    rib1 = translate([0, 0, 2.5])(cube([4, 60, 10], center=True))
    rib2 = translate([0, 0, 2.5])(cube([80, 4, 10], center=True))

    # 部品を組み立て（差集合と和集合を使用）
    part = base + boss + rib1 + rib2
    for hole in mounting_holes:
        part = part - hole
    part = part - center_hole

    return part


def create_simple_box():
    """簡単な箱のモデル"""
    outer = cube([50, 40, 30], center=True)
    inner = translate([0, 0, 2])(cube([44, 34, 30], center=True))
    box = outer - inner
    return box


def create_gear_like_shape():
    """歯車風の形状"""
    # 中心のシリンダー
    center = cylinder(h=5, r=15, segments=50, center=True)

    # 外周の歯
    teeth = []
    num_teeth = 12
    for i in range(num_teeth):
        angle = i * (360 / num_teeth)
        tooth = rotate([0, 0, angle])(
            translate([18, 0, 0])(
                cube([6, 4, 5], center=True)
            )
        )
        teeth.append(tooth)

    # 中央穴
    center_hole = cylinder(h=6, r=5, segments=40, center=True)

    # 組み立て
    gear = center
    for tooth in teeth:
        gear = gear + tooth
    gear = gear - center_hole

    return gear


def create_2d_projection_scad(model_3d, output_filename):
    """
    3DモデルをOpenSCADコードに変換し、2D投影を含める

    Args:
        model_3d: 3Dモデルオブジェクト
        output_filename: 出力する.scadファイル名
    """
    # 3Dモデルのコード生成
    scad_code_3d = scad_render(model_3d)

    # 2D投影用のコードを追加
    scad_code_with_2d = f"""
// 3Dモデル
{scad_code_3d}

// 2D投影（トップビュー）
// 以下のコメントを外すと2D投影が表示されます
// projection(cut=false) {{ object(); }}
"""

    # ファイルに保存
    with open(output_filename, 'w') as f:
        f.write(scad_code_with_2d)

    print(f"OpenSCADファイルを生成しました: {output_filename}")


def main():
    """メイン処理"""

    print("=== SolidPython2で3Dモデルを生成 ===\n")

    # モデル1: 機械部品
    print("1. 機械部品モデルを生成...")
    mechanical_part = create_mechanical_part()
    mechanical_part.save_as_scad("mechanical_part.scad")
    print("   → mechanical_part.scad に保存\n")

    # モデル2: 簡単な箱
    print("2. 箱モデルを生成...")
    box = create_simple_box()
    box.save_as_scad("box.scad")
    print("   → box.scad に保存\n")

    # モデル3: 歯車風の形状
    print("3. 歯車風モデルを生成...")
    gear = create_gear_like_shape()
    gear.save_as_scad("gear.scad")
    print("   → gear.scad に保存\n")

    # 2D投影用のSCADファイルを作成
    print("4. 2D投影用のOpenSCADファイルを生成...")

    # 機械部品の2D投影用ファイル
    create_2d_projection_file("mechanical_part.scad", "mechanical_part_2d.scad")
    create_2d_projection_file("box.scad", "box_2d.scad")
    create_2d_projection_file("gear.scad", "gear_2d.scad")

    print("\n✓ すべてのモデル生成が完了しました！")
    print("\n次のステップ:")
    print("  - 3D画像: python3 openscad_renderer.py mechanical_part.scad mechanical_part_3d.png")
    print("  - 2D図面: python3 openscad_renderer.py mechanical_part_2d.scad mechanical_part_2d.png")


def create_2d_projection_file(input_scad, output_scad):
    """
    既存のSCADファイルを読み込んで2D投影版を作成

    Args:
        input_scad: 入力する3D SCADファイル
        output_scad: 出力する2D投影SCADファイル
    """
    with open(input_scad, 'r') as f:
        original_code = f.read()

    # 2D投影コードを生成
    # projection()を使用して、上面図（トップビュー）を生成
    projection_code = f"""// 2D投影（トップビュー）
// Original 3D model code:
module original_3d_model() {{
{original_code}
}}

// 2D projection from top
projection(cut=false) {{
    original_3d_model();
}}
"""

    with open(output_scad, 'w') as f:
        f.write(projection_code)

    print(f"   → {output_scad} に2D投影版を保存")


if __name__ == "__main__":
    main()
