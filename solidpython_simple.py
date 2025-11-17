#!/usr/bin/env python3
"""
SolidPython2を使用した3Dモデル生成と2D図面出力の例（BOSL2なし版）
"""

from solid2 import *


def create_mechanical_part():
    """機械部品のサンプルモデルを作成（標準OpenSCAD関数のみ使用）"""

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
        hole = translate(pos)(cylinder(h=6, r=3, _fn=30, center=True))
        mounting_holes.append(hole)

    # ボス（中央の突起）
    boss = translate([0, 0, 7])(cylinder(h=10, r=12, _fn=50, center=True))

    # ボスの中央穴
    center_hole = translate([0, 0, 7])(cylinder(h=12, r=6, _fn=40, center=True))

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
    center = cylinder(h=5, r=15, _fn=50, center=True)

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
    center_hole = cylinder(h=6, r=5, _fn=40, center=True)

    # 組み立て
    gear = center
    for tooth in teeth:
        gear = gear + tooth
    gear = gear - center_hole

    return gear


def save_model_and_2d(model, name_prefix):
    """
    3Dモデルと2D投影版の両方を保存

    Args:
        model: 3Dモデルオブジェクト
        name_prefix: ファイル名のプレフィックス
    """
    # 3Dモデルを保存
    scad_3d = f"{name_prefix}_3d.scad"
    model.save_as_scad(scad_3d)
    print(f"   → {scad_3d} に3Dモデルを保存")

    # 2D投影版を作成
    scad_2d = f"{name_prefix}_2d.scad"

    # OpenSCADのprojection()を使用した2D投影コードを生成
    scad_code = scad_render(model)

    projection_code = f"""// 2D投影（トップビュー）
// Original 3D model
module model_3d() {{
{scad_code}
}}

// Top view projection
projection(cut=false) model_3d();
"""

    with open(scad_2d, 'w') as f:
        f.write(projection_code)

    print(f"   → {scad_2d} に2D投影版を保存")


def main():
    """メイン処理"""

    print("=== SolidPython2で3Dモデルと2D図面を生成 ===\n")

    # モデル1: 機械部品
    print("1. 機械部品モデルを生成...")
    mechanical_part = create_mechanical_part()
    save_model_and_2d(mechanical_part, "mech_part")
    print()

    # モデル2: 簡単な箱
    print("2. 箱モデルを生成...")
    box = create_simple_box()
    save_model_and_2d(box, "simple_box")
    print()

    # モデル3: 歯車風の形状
    print("3. 歯車風モデルを生成...")
    gear = create_gear_like_shape()
    save_model_and_2d(gear, "gear_shape")
    print()

    print("✓ すべてのモデル生成が完了しました！\n")
    print("次のステップ: レンダリング")
    print("  3D画像の生成:")
    print("    python3 openscad_renderer.py mech_part_3d.scad mech_part_3d.png")
    print("  2D図面の生成:")
    print("    python3 openscad_renderer.py mech_part_2d.scad mech_part_2d.png")


if __name__ == "__main__":
    main()
