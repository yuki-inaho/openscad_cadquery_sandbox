#!/usr/bin/env python3
"""
SolidPython2を使用した3Dモデル生成と2D図面出力の例
"""

import sys
from pathlib import Path

# scriptsモジュールをインポート可能にする
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from solid2 import *
from scripts.solidpython_utils import batch_save_models


def create_mechanical_part():
    """機械部品のサンプルモデルを作成"""
    base = cube([80, 60, 5], center=True)

    # 取り付け穴（四隅）
    hole_positions = [[-30, -20, 0], [30, -20, 0], [-30, 20, 0], [30, 20, 0]]
    mounting_holes = [
        translate(pos)(cylinder(h=6, r=3, _fn=30, center=True))
        for pos in hole_positions
    ]

    # ボス（中央の突起）と中央穴
    boss = translate([0, 0, 7])(cylinder(h=10, r=12, _fn=50, center=True))
    center_hole = translate([0, 0, 7])(cylinder(h=12, r=6, _fn=40, center=True))

    # リブ（補強材）
    rib1 = translate([0, 0, 2.5])(cube([4, 60, 10], center=True))
    rib2 = translate([0, 0, 2.5])(cube([80, 4, 10], center=True))

    # 組み立て
    part = base + boss + rib1 + rib2
    for hole in mounting_holes:
        part = part - hole
    part = part - center_hole

    return part


def create_simple_box():
    """簡単な箱のモデル"""
    outer = cube([50, 40, 30], center=True)
    inner = translate([0, 0, 2])(cube([44, 34, 30], center=True))
    return outer - inner


def create_gear_like_shape():
    """歯車風の形状"""
    gear = cylinder(h=5, r=15, _fn=50, center=True)

    num_teeth = 12
    for i in range(num_teeth):
        tooth = rotate([0, 0, i * (360 / num_teeth)])(
            translate([18, 0, 0])(cube([6, 4, 5], center=True))
        )
        gear = gear + tooth

    center_hole = cylinder(h=6, r=5, _fn=40, center=True)
    gear = gear - center_hole

    return gear


def main():
    """メイン処理"""
    print("=== SolidPython2で3Dモデルと2D図面を生成 ===\n")

    models = {
        "mech_part": create_mechanical_part(),
        "simple_box": create_simple_box(),
        "gear_shape": create_gear_like_shape(),
    }

    batch_save_models(models, output_dir="outputs/solidpython")

    print("\n[SUCCESS] すべてのモデル生成が完了しました!\n")
    print("次のステップ: レンダリング")
    print("  3D画像の生成:")
    print("    python3 scripts/renderer.py outputs/solidpython/mech_part_3d.scad output_3d.png")
    print("  2D図面の生成:")
    print("    python3 scripts/renderer.py outputs/solidpython/mech_part_2d.scad output_2d.png --projection o")


if __name__ == "__main__":
    main()
