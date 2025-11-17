#!/usr/bin/env python3
"""
L字ブラケットの形状解析スクリプト
DXF/SVGパーサーを使って自己フィードバック
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import cadquery as cq
from scripts.cadquery_utils import export_dxf, export_svg
from scripts.dxf_parser import parse_dxf
from scripts.svg_parser import parse_svg

# L字ブラケット生成（現在のコードをコピー）
def create_l_bracket_camera_mount():
    """
    L字カメラマウントブラケットを生成
    """
    # パラメータ定義
    t = 2.0
    horizontal_width = 80.0
    horizontal_depth = 50.0
    vertical_width = 80.0
    vertical_height = 40.0

    tripod_hole_diameter = 6.5
    tripod_abs_x = 40.0
    tripod_abs_y = 20.0

    camera_hole_diameter = 3.2
    camera_abs_x_left = 8.5
    camera_abs_x_right = 71.5
    camera_abs_z_bottom = 8.0
    camera_abs_z_top = 16.0

    bend_radius = 4.0
    edge_radius = 1.5

    # 水平板作成
    horizontal_plate = (
        cq.Workplane("XY")
        .box(horizontal_width, horizontal_depth, t, centered=False)
        .faces(">Z")
        .workplane()
        .pushPoints([
            (tripod_abs_x - horizontal_width/2,
             tripod_abs_y - horizontal_depth/2)
        ])
        .circle(tripod_hole_diameter / 2)
        .cutThruAll()
    )

    # 垂直板作成
    vertical_plate = (
        cq.Workplane("XZ")
        .box(vertical_width, vertical_height, t, centered=False)
        .translate((0, -t, 0))
        .faces("<Y")
        .workplane()
        .pushPoints([
            (camera_abs_x_left - vertical_width/2,
             camera_abs_z_bottom - vertical_height/2),
            (camera_abs_x_left - vertical_width/2,
             camera_abs_z_top - vertical_height/2),
            (camera_abs_x_right - vertical_width/2,
             camera_abs_z_bottom - vertical_height/2),
            (camera_abs_x_right - vertical_width/2,
             camera_abs_z_top - vertical_height/2),
        ])
        .circle(camera_hole_diameter / 2)
        .cutThruAll()
    )

    # 結合
    bracket = horizontal_plate.union(vertical_plate)

    # フィレット
    try:
        bracket = bracket.edges("|X and <Y and <Z").fillet(bend_radius)
    except Exception as e:
        print(f"[WARNING] 内側フィレット失敗: {e}")

    try:
        bracket = bracket.edges("|Z and >Y").fillet(edge_radius)
    except Exception as e:
        print(f"[WARNING] 外側フィレット失敗: {e}")

    return bracket


def main():
    print("=== L字ブラケット形状解析 ===\n")

    # L字ブラケット生成
    print("[1] L字ブラケット生成中...")
    bracket = create_l_bracket_camera_mount()
    print("[SUCCESS] L字ブラケット生成完了\n")

    # 出力ディレクトリ
    output_dir = Path("outputs/analysis")
    output_dir.mkdir(parents=True, exist_ok=True)

    # DXFエクスポート（3断面）
    print("[2] DXFエクスポート中...")
    dxf_xy = output_dir / "bracket_analysis_xy.dxf"
    dxf_xz = output_dir / "bracket_analysis_xz.dxf"
    dxf_yz = output_dir / "bracket_analysis_yz.dxf"

    export_dxf(bracket, str(dxf_xy), section_plane="XY")
    export_dxf(bracket, str(dxf_xz), section_plane="XZ")
    export_dxf(bracket, str(dxf_yz), section_plane="YZ")
    print()

    # SVGエクスポート（複数視点）
    print("[3] SVGエクスポート中...")
    svg_top = output_dir / "bracket_analysis_top.svg"
    svg_front = output_dir / "bracket_analysis_front.svg"
    svg_side = output_dir / "bracket_analysis_side.svg"

    export_svg(bracket, str(svg_top), {"projectionDir": (0, 0, 1)})
    export_svg(bracket, str(svg_front), {"projectionDir": (0, -1, 0)})
    export_svg(bracket, str(svg_side), {"projectionDir": (1, 0, 0)})
    print()

    # DXF解析
    print("[4] DXF解析中...")
    print("\n--- XY断面（トップビュー）---")
    parser_xy = parse_dxf(str(dxf_xy), str(output_dir / "report_xy.txt"))

    print("\n--- XZ断面（フロントビュー）---")
    parser_xz = parse_dxf(str(dxf_xz), str(output_dir / "report_xz.txt"))

    print("\n--- YZ断面（サイドビュー）---")
    parser_yz = parse_dxf(str(dxf_yz), str(output_dir / "report_yz.txt"))
    print()

    # SVG解析
    print("[5] SVG解析中...")
    print("\n--- トップビューSVG ---")
    parser_svg_top = parse_svg(str(svg_top), str(output_dir / "report_svg_top.txt"))

    print("\n--- フロントビューSVG ---")
    parser_svg_front = parse_svg(str(svg_front), str(output_dir / "report_svg_front.txt"))

    print("\n--- サイドビューSVG ---")
    parser_svg_side = parse_svg(str(svg_side), str(output_dir / "report_svg_side.txt"))
    print()

    # 統合分析レポート生成
    print("[6] 統合分析レポート生成中...")
    report_path = output_dir / "ANALYSIS_REPORT.txt"

    with open(report_path, "w", encoding="utf-8") as f:
        f.write("=" * 80 + "\n")
        f.write("L字ブラケット形状解析レポート\n")
        f.write("=" * 80 + "\n\n")

        # DXF XY断面分析
        f.write("【1】XY断面（トップビュー）分析\n")
        f.write("-" * 80 + "\n")
        if parser_xy:
            circles = parser_xy.get_circles()
            lines = parser_xy.get_lines()
            f.write(f"円: {len(circles)}個\n")
            f.write(f"線分: {len(lines)}個\n")
            if circles:
                f.write("\n円の詳細:\n")
                for i, c in enumerate(circles, 1):
                    f.write(f"  円{i}: 中心=({c['center'][0]:.2f}, {c['center'][1]:.2f}), "
                           f"半径={c['radius']:.2f}mm, 直径={c['diameter']:.2f}mm\n")
            else:
                f.write("  ⚠️ 警告: 穴（円）が検出されませんでした\n")
        f.write("\n")

        # DXF XZ断面分析
        f.write("【2】XZ断面（フロントビュー）分析\n")
        f.write("-" * 80 + "\n")
        if parser_xz:
            circles = parser_xz.get_circles()
            lines = parser_xz.get_lines()
            f.write(f"円: {len(circles)}個\n")
            f.write(f"線分: {len(lines)}個\n")
            if circles:
                f.write("\n円の詳細:\n")
                for i, c in enumerate(circles, 1):
                    f.write(f"  円{i}: 中心=({c['center'][0]:.2f}, {c['center'][1]:.2f}), "
                           f"半径={c['radius']:.2f}mm, 直径={c['diameter']:.2f}mm\n")
            else:
                f.write("  ⚠️ 警告: 穴（円）が検出されませんでした\n")
        f.write("\n")

        # 問題診断
        f.write("【診断結果】\n")
        f.write("-" * 80 + "\n")

        issues = []

        # XY断面の穴チェック（三脚穴が1個あるはず）
        xy_circles = parser_xy.get_circles() if parser_xy else []
        if len(xy_circles) == 0:
            issues.append("❌ XY断面: 三脚用穴（φ6.5）が検出されませんでした")
        elif len(xy_circles) == 1:
            issues.append(f"✓ XY断面: 三脚用穴を検出 (φ{xy_circles[0]['diameter']:.2f}mm)")

        # XZ断面の穴チェック（カメラ固定穴が4個あるはず）
        xz_circles = parser_xz.get_circles() if parser_xz else []
        if len(xz_circles) == 0:
            issues.append("❌ XZ断面: カメラ固定用穴（4-M3）が検出されませんでした")
        elif len(xz_circles) < 4:
            issues.append(f"⚠️ XZ断面: カメラ固定用穴が{len(xz_circles)}個のみ検出（期待値: 4個）")
        elif len(xz_circles) == 4:
            issues.append(f"✓ XZ断面: カメラ固定用穴4個を検出")
            f.write("\nカメラ固定用穴の位置:\n")
            for i, c in enumerate(xz_circles, 1):
                f.write(f"  穴{i}: X={c['center'][0]:.2f}mm, Z={c['center'][1]:.2f}mm, φ{c['diameter']:.2f}mm\n")

        # L字形状チェック（XZ断面の線分数で判断）
        xz_lines = parser_xz.get_lines() if parser_xz else []
        if len(xz_lines) < 4:
            issues.append(f"⚠️ XZ断面: L字形状が不完全な可能性（線分数: {len(xz_lines)}）")
        else:
            issues.append(f"✓ XZ断面: L字形状を確認（線分数: {len(xz_lines)}）")

        f.write("\n")
        for issue in issues:
            f.write(f"{issue}\n")

        f.write("\n" + "=" * 80 + "\n")
        f.write("レポート生成完了\n")
        f.write("=" * 80 + "\n")

    print(f"[SUCCESS] 統合レポート生成: {report_path}")
    print(f"\n統合レポートの内容:\n")

    # レポートを表示
    with open(report_path, "r", encoding="utf-8") as f:
        print(f.read())

    print("\n=== 解析完了 ===")
    print(f"\n生成ファイル:")
    print(f"  - outputs/analysis/bracket_analysis_*.dxf (3種)")
    print(f"  - outputs/analysis/bracket_analysis_*.svg (3種)")
    print(f"  - outputs/analysis/report_*.txt (6種)")
    print(f"  - outputs/analysis/ANALYSIS_REPORT.txt (統合レポート)")


if __name__ == "__main__":
    main()
