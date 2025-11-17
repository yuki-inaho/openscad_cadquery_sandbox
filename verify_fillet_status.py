#!/usr/bin/env python3
"""
L字ブラケットのフィレット状況を検証するスクリプト

目的:
- フィレットが正しく適用されているかを確認
- エッジ数の変化を確認
- DXF断面でフィレット形状を視覚的に確認
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import cadquery as cq
from scripts.cadquery_utils import export_dxf
from scripts.dxf_parser import parse_dxf


def create_bracket_without_fillet():
    """フィレットなしL字ブラケット"""
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
    camera_z_bottom = t + 8.0
    camera_z_top = t + 16.0

    # カメラ穴の回転前Y座標
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

    return bracket


def create_bracket_with_fillet(bend_radius=3.0, edge_radius=1.5):
    """フィレット付きL字ブラケット"""
    bracket = create_bracket_without_fillet()

    # 内側フィレット
    try:
        bracket = bracket.edges("|X and >Z and <Y").fillet(bend_radius)
        print(f"✓ 内側フィレット適用成功: R{bend_radius}mm")
    except Exception as e:
        print(f"✗ 内側フィレット失敗: {e}")

    # 外側フィレット
    try:
        bracket = bracket.edges("|Z and >Y").fillet(edge_radius)
        print(f"✓ 外側フィレット適用成功: R{edge_radius}mm")
    except Exception as e:
        print(f"✗ 外側フィレット失敗: {e}")

    return bracket


def analyze_edges(bracket, label):
    """エッジ情報を分析"""
    print(f"\n=== {label} ===")

    # 全エッジ数
    all_edges = bracket.edges().vals()
    print(f"総エッジ数: {len(all_edges)}")

    # エッジタイプ別に分類
    edge_types = {}
    for edge in all_edges:
        edge_type = type(edge.wrapped).__name__
        edge_types[edge_type] = edge_types.get(edge_type, 0) + 1

    print("エッジタイプ別:")
    for edge_type, count in sorted(edge_types.items()):
        print(f"  {edge_type}: {count}")

    # 特定方向のエッジをカウント
    try:
        x_edges = bracket.edges("|X").vals()
        print(f"X方向エッジ (|X): {len(x_edges)}")
    except:
        print("X方向エッジ (|X): 選択不可")

    try:
        y_edges = bracket.edges("|Y").vals()
        print(f"Y方向エッジ (|Y): {len(y_edges)}")
    except:
        print("Y方向エッジ (|Y): 選択不可")

    try:
        z_edges = bracket.edges("|Z").vals()
        print(f"Z方向エッジ (|Z): {len(z_edges)}")
    except:
        print("Z方向エッジ (|Z): 選択不可")

    # L字内側角のエッジ
    try:
        inner_edges = bracket.edges("|X and >Z and <Y").vals()
        print(f"L字内側角エッジ (|X and >Z and <Y): {len(inner_edges)}")
    except:
        print("L字内側角エッジ (|X and >Z and <Y): 選択不可")

    # 外側エッジ
    try:
        outer_edges = bracket.edges("|Z and >Y").vals()
        print(f"外側エッジ (|Z and >Y): {len(outer_edges)}")
    except:
        print("外側エッジ (|Z and >Y): 選択不可")


def export_cross_sections(bracket, prefix, output_dir):
    """断面をDXFエクスポート"""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n=== {prefix} 断面エクスポート ===")

    sections = [
        ("XY_z1", "XY", 1.0),      # 水平板中央
        ("XZ_y0", "XZ", 0.0),      # 中心断面（L字の角が見える）
        ("XZ_y-25", "XZ", -25.0),  # 垂直板背面
        ("YZ_x0", "YZ", 0.0),      # 側面（L字シルエット）
    ]

    for name, plane, height in sections:
        dxf_file = output_dir / f"{prefix}_{name}.dxf"
        try:
            export_dxf(bracket, str(dxf_file), section_plane=plane, section_height=height)
            print(f"  ✓ {name}: {dxf_file.name}")
        except Exception as e:
            print(f"  ✗ {name}: {e}")


def compare_dxf_complexity(file1, file2, label1, label2):
    """2つのDXFファイルのエンティティ数を比較"""
    print(f"\n=== DXF比較: {label1} vs {label2} ===")

    try:
        parser1 = parse_dxf(str(file1))
        parser2 = parse_dxf(str(file2))

        entities1 = parser1.get_entity_count()
        entities2 = parser2.get_entity_count()

        print(f"{label1}:")
        for entity_type, count in sorted(entities1.items()):
            print(f"  {entity_type}: {count}")

        print(f"\n{label2}:")
        for entity_type, count in sorted(entities2.items()):
            diff = count - entities1.get(entity_type, 0)
            diff_str = f" ({diff:+d})" if diff != 0 else ""
            print(f"  {entity_type}: {count}{diff_str}")

        # ARCやSPLINEの増加はフィレット適用の証拠
        if entities2.get('ARC', 0) > entities1.get('ARC', 0):
            print("\n✓ ARCエンティティ増加 → フィレットが適用されている可能性あり")
        elif entities2.get('SPLINE', 0) > entities1.get('SPLINE', 0):
            print("\n✓ SPLINEエンティティ増加 → フィレットが適用されている可能性あり")
        else:
            print("\n✗ 曲線エンティティの増加なし → フィレットが適用されていない可能性")

    except Exception as e:
        print(f"✗ DXF比較エラー: {e}")


def main():
    print("=" * 60)
    print("L字ブラケット フィレット検証")
    print("=" * 60)

    output_dir = Path("outputs/verify_fillet")
    output_dir.mkdir(parents=True, exist_ok=True)

    # 1. フィレットなし生成
    print("\n[1/4] フィレットなしブラケット生成中...")
    bracket_no_fillet = create_bracket_without_fillet()
    analyze_edges(bracket_no_fillet, "フィレットなし")
    export_cross_sections(bracket_no_fillet, "no_fillet", output_dir)

    # 2. フィレット付き生成
    print("\n[2/4] フィレット付きブラケット生成中...")
    bracket_with_fillet = create_bracket_with_fillet(bend_radius=3.0, edge_radius=1.5)
    analyze_edges(bracket_with_fillet, "フィレット付き")
    export_cross_sections(bracket_with_fillet, "with_fillet", output_dir)

    # 3. DXF比較
    print("\n[3/4] DXF断面比較...")
    dxf_sections = ["XZ_y0", "YZ_x0"]
    for section in dxf_sections:
        file1 = output_dir / f"no_fillet_{section}.dxf"
        file2 = output_dir / f"with_fillet_{section}.dxf"
        if file1.exists() and file2.exists():
            compare_dxf_complexity(file1, file2, "フィレットなし", "フィレット付き")

    # 4. 結論
    print("\n" + "=" * 60)
    print("検証結果サマリー")
    print("=" * 60)
    print(f"出力ディレクトリ: {output_dir}")
    print("\n確認項目:")
    print("  1. エッジ数の変化（フィレットで減少するはず）")
    print("  2. エッジタイプの変化（Circle/Ellipseが増えるはず）")
    print("  3. DXFのARC/SPLINEエンティティ増加")
    print("\nDXFファイルをCADソフトで開いて視覚的に確認してください:")
    print(f"  - {output_dir}/no_fillet_YZ_x0.dxf")
    print(f"  - {output_dir}/with_fillet_YZ_x0.dxf")
    print("\nL字の角がR形状になっていればフィレットが正しく適用されています。")


if __name__ == "__main__":
    main()
