#!/usr/bin/env python3
"""
CadQueryを使用した3Dモデル生成の例
STEP、STL、DXF形式での出力をサポート
"""

import sys
from pathlib import Path

# scriptsモジュールをインポート可能にする
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import cadquery as cq
from scripts.cadquery_utils import save_model_with_openscad_support


def create_simple_box():
    """シンプルな箱を作成"""
    return (
        cq.Workplane("XY")
        .box(50, 40, 30)
        .faces(">Z")
        .shell(-2)
    )


def create_mechanical_bracket():
    """機械部品のブラケットを作成"""
    return (
        cq.Workplane("XY")
        .box(80, 60, 5, centered=(True, True, False))
        .faces(">Z").workplane()
        .rect(60, 40, forConstruction=True).vertices()
        .circle(3).cutThruAll()
        .faces(">Z").workplane()
        .circle(12).extrude(10)
        .faces(">Z").workplane()
        .circle(6).cutThruAll()
        .edges("|Z").fillet(2)
    )


def create_parametric_flange(outer_d=80, inner_d=40, thickness=10, num_bolts=6):
    """パラメトリックなフランジを作成"""
    bolt_circle_d = outer_d * 0.8125
    bolt_hole_d = 8

    return (
        cq.Workplane("XY")
        .circle(outer_d / 2).extrude(thickness)
        .faces(">Z").workplane()
        .circle(inner_d / 2).cutThruAll()
        .faces(">Z").workplane()
        .polarArray(bolt_circle_d / 2, 0, 360, num_bolts)
        .circle(bolt_hole_d / 2).cutThruAll()
        .edges(">Z").chamfer(1.5)
    )


def create_gear(num_teeth=16, tooth_depth=3, gear_radius=20):
    """簡単な歯車を作成"""
    result = cq.Workplane("XY").circle(gear_radius).extrude(5)

    for i in range(num_teeth):
        angle = i * (360 / num_teeth)
        tooth = (
            cq.Workplane("XY")
            .transformed(rotate=(0, 0, angle))
            .workplane(offset=0)
            .moveTo(gear_radius, 0)
            .rect(tooth_depth * 2, 4)
            .extrude(5)
        )
        result = result.union(tooth)

    return result.faces(">Z").workplane().circle(5).cutThruAll()


def create_lego_brick(length=32, width=16, height=9.6):
    """レゴブロック風の部品を作成"""
    stud_d, stud_h = 4.8, 1.8

    return (
        cq.Workplane("XY")
        .box(length, width, height, centered=(True, True, False))
        .faces(">Z").workplane()
        .rarray(8, 8, 4, 2)
        .circle(stud_d / 2).extrude(stud_h)
        .faces("<Z").workplane()
        .rect(length - 3, width - 3).extrude(height - 1)
        .edges("|Z").fillet(0.5)
    )


def main():
    """メイン処理"""
    print("=== CadQueryで3Dモデルを生成 ===\n")

    models = {
        "cq_simple_box": create_simple_box(),
        "cq_bracket": create_mechanical_bracket(),
        "cq_flange": create_parametric_flange(),
        "cq_gear": create_gear(),
        "cq_lego_brick": create_lego_brick(),
    }

    for name, model in models.items():
        print(f"\n=== {name} ===")
        save_model_with_openscad_support(
            model,
            name,
            output_dir="outputs/cadquery",
            create_projections=False  # 大量の2D投影は省略
        )

    print("\n[SUCCESS] すべてのモデル生成が完了しました!")
    print("\n生成されたファイル:")
    print("  - STEP形式: CADソフトで編集可能")
    print("  - STL形式: 3Dプリント用")
    print("\nOpenSCADでの使用:")
    print("  python3 scripts/renderer.py outputs/cadquery/cq_bracket.scad output.png")


if __name__ == "__main__":
    main()
