#!/usr/bin/env python3
"""
CadQueryを使用した3Dモデル生成の例
STEP、STL、DXF形式での出力をサポート
"""

import cadquery as cq
from pathlib import Path


def create_simple_box():
    """シンプルな箱を作成"""
    result = (
        cq.Workplane("XY")
        .box(50, 40, 30)
        .faces(">Z")
        .shell(-2)  # 厚さ2mmの箱
    )
    return result


def create_mechanical_bracket():
    """機械部品のブラケットを作成"""
    result = (
        cq.Workplane("XY")
        # ベースプレート
        .box(80, 60, 5, centered=(True, True, False))
        # 四隅の取り付け穴
        .faces(">Z")
        .workplane()
        .rect(60, 40, forConstruction=True)
        .vertices()
        .circle(3)
        .cutThruAll()
        # 中央のボス
        .faces(">Z")
        .workplane()
        .circle(12)
        .extrude(10)
        # ボスの中央穴
        .faces(">Z")
        .workplane()
        .circle(6)
        .cutThruAll()
        # エッジのフィレット
        .edges("|Z")
        .fillet(2)
    )
    return result


def create_parametric_flange():
    """パラメトリックなフランジを作成"""
    # パラメータ
    outer_diameter = 80
    inner_diameter = 40
    thickness = 10
    bolt_circle_diameter = 65
    bolt_hole_diameter = 8
    num_bolts = 6

    result = (
        cq.Workplane("XY")
        # 外側のシリンダー
        .circle(outer_diameter / 2)
        .extrude(thickness)
        # 内側の穴
        .faces(">Z")
        .workplane()
        .circle(inner_diameter / 2)
        .cutThruAll()
        # ボルト穴を配置
        .faces(">Z")
        .workplane()
        .polarArray(bolt_circle_diameter / 2, 0, 360, num_bolts)
        .circle(bolt_hole_diameter / 2)
        .cutThruAll()
        # 面取り
        .edges(">Z")
        .chamfer(1.5)
    )
    return result


def create_gear():
    """簡単な歯車を作成"""
    num_teeth = 16
    tooth_depth = 3
    gear_radius = 20

    # 基本の円盤
    result = cq.Workplane("XY").circle(gear_radius).extrude(5)

    # 歯を追加
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

    # 中央穴
    result = result.faces(">Z").workplane().circle(5).cutThruAll()

    return result


def create_lego_brick():
    """レゴブロック風の部品を作成"""
    length = 32  # 4スタッド分
    width = 16   # 2スタッド分
    height = 9.6
    stud_diameter = 4.8
    stud_height = 1.8

    result = (
        cq.Workplane("XY")
        # ベース
        .box(length, width, height, centered=(True, True, False))
        # 上面のスタッド（突起）
        .faces(">Z")
        .workplane()
        .rarray(8, 8, 4, 2)  # 4x2のグリッド
        .circle(stud_diameter / 2)
        .extrude(stud_height)
        # 内部を空洞に
        .faces("<Z")
        .workplane()
        .rect(length - 3, width - 3)
        .extrude(height - 1)
        # エッジを丸く
        .edges("|Z")
        .fillet(0.5)
    )
    return result


def save_model_all_formats(model, name_prefix, output_dir="cadquery_outputs"):
    """
    モデルを各種形式で保存

    Args:
        model: CadQueryモデル
        name_prefix: ファイル名のプレフィックス
        output_dir: 出力ディレクトリ
    """
    Path(output_dir).mkdir(exist_ok=True)

    # STEP形式で保存（CADソフトで編集可能な高品質形式）
    step_path = f"{output_dir}/{name_prefix}.step"
    cq.exporters.export(model, step_path)
    print(f"   → {step_path} (STEP形式)")

    # STL形式で保存（3Dプリント用）
    stl_path = f"{output_dir}/{name_prefix}.stl"
    cq.exporters.export(model, stl_path)
    print(f"   → {stl_path} (STL形式)")

    # DXF形式で保存（2D図面）
    try:
        # トップビューの2D投影を作成
        dxf_path = f"{output_dir}/{name_prefix}_top.dxf"
        cq.exporters.export(model.projectToWorkplane(cq.Workplane("XY")), dxf_path)
        print(f"   → {dxf_path} (DXF形式 - トップビュー)")
    except Exception as e:
        print(f"   [WARNING] DXF出力でエラー: {e}")

    # SVG形式で保存（2D図面）
    try:
        svg_path = f"{output_dir}/{name_prefix}_top.svg"
        cq.exporters.export(
            model.projectToWorkplane(cq.Workplane("XY")),
            svg_path,
            opt={
                "width": 300,
                "height": 300,
                "marginLeft": 10,
                "marginTop": 10,
                "showAxes": False,
                "projectionDir": (0, 0, 1),
                "strokeWidth": 0.25,
            }
        )
        print(f"   → {svg_path} (SVG形式 - トップビュー)")
    except Exception as e:
        print(f"   [WARNING] SVG出力でエラー: {e}")


def convert_to_openscad(model, output_path):
    """
    CadQueryモデルをSTL経由でOpenSCADで使用可能にする

    Args:
        model: CadQueryモデル
        output_path: 出力する.scadファイルのパス
    """
    # まずSTLファイルを生成
    stl_path = output_path.replace('.scad', '.stl')
    cq.exporters.export(model, stl_path)

    # STLをインポートするOpenSCADコードを生成
    scad_code = f"""// CadQueryから生成されたモデル
// STLファイルをインポート

import("{Path(stl_path).name}");
"""

    with open(output_path, 'w') as f:
        f.write(scad_code)

    print(f"   → {output_path} (OpenSCAD形式)")
    print(f"   → {stl_path} (STL形式)")


def main():
    """メイン処理"""
    print("=== CadQueryで3Dモデルを生成 ===\n")

    # モデル1: シンプルな箱
    print("1. シンプルな箱を生成...")
    simple_box = create_simple_box()
    save_model_all_formats(simple_box, "cq_simple_box")
    print()

    # モデル2: 機械部品のブラケット
    print("2. 機械部品のブラケットを生成...")
    bracket = create_mechanical_bracket()
    save_model_all_formats(bracket, "cq_bracket")
    print()

    # モデル3: パラメトリックフランジ
    print("3. パラメトリックフランジを生成...")
    flange = create_parametric_flange()
    save_model_all_formats(flange, "cq_flange")
    print()

    # モデル4: 歯車
    print("4. 歯車を生成...")
    gear = create_gear()
    save_model_all_formats(gear, "cq_gear")
    print()

    # モデル5: レゴブロック風
    print("5. レゴブロック風の部品を生成...")
    lego = create_lego_brick()
    save_model_all_formats(lego, "cq_lego_brick")
    print()

    # OpenSCAD形式でも出力（STLインポート方式）
    print("6. OpenSCAD形式での出力...")
    convert_to_openscad(bracket, "cadquery_outputs/cq_bracket_for_openscad.scad")
    print()

    print("[SUCCESS] すべてのモデル生成が完了しました!")
    print("\n生成されたファイル:")
    print("  - STEP形式: CADソフトで編集可能")
    print("  - STL形式: 3Dプリント用")
    print("  - DXF形式: 2D CAD用")
    print("  - SVG形式: 2D図面（ブラウザで表示可能）")
    print("\nOpenSCADでの使用:")
    print("  python3 openscad_renderer.py cadquery_outputs/cq_bracket_for_openscad.scad cq_bracket.png")


if __name__ == "__main__":
    main()
