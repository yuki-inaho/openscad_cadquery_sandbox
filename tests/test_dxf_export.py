#!/usr/bin/env python3
"""
DXFエクスポート機能のテストスクリプト

修正されたexport_dxf()関数を検証します。
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import cadquery as cq
from scripts.cadquery_utils import export_dxf, export_all_formats

def create_test_l_bracket():
    """テスト用L字ブラケットを作成"""
    # ベースプレート
    base = cq.Workplane("XY").box(80, 60, 10, centered=(True, True, False))

    # 垂直プレート
    vertical = (
        cq.Workplane("XZ")
        .workplane(offset=-30)
        .moveTo(0, 10)
        .box(80, 60, 10, centered=(True, False, True))
    )

    # 結合
    bracket = base.union(vertical)

    # 取り付け穴（ベースプレート）
    bracket = (
        bracket.faces(">Z").workplane()
        .rect(60, 40, forConstruction=True).vertices()
        .circle(4).cutThruAll()
    )

    # 取り付け穴（垂直プレート）
    bracket = (
        bracket.faces(">Y").workplane()
        .rect(60, 40, forConstruction=True).vertices()
        .circle(4).cutThruAll()
    )

    return bracket


def test_dxf_export():
    """DXFエクスポートのテスト"""
    print("=== DXFエクスポート機能テスト ===\n")

    # テストモデル作成
    print("L字ブラケットモデルを作成中...")
    bracket = create_test_l_bracket()
    print("[SUCCESS] モデル作成完了\n")

    # 出力ディレクトリ作成
    output_dir = Path("outputs/test_dxf")
    output_dir.mkdir(parents=True, exist_ok=True)

    # XY平面（トップビュー）のDXFエクスポート
    print("--- XY平面（トップビュー）のDXFエクスポート ---")
    dxf_xy = str(output_dir / "bracket_xy.dxf")
    result_xy = export_dxf(bracket, dxf_xy, section_plane="XY")
    print(f"結果: {'成功' if result_xy else '失敗'}\n")

    # XZ平面（フロントビュー）のDXFエクスポート
    print("--- XZ平面（フロントビュー）のDXFエクスポート ---")
    dxf_xz = str(output_dir / "bracket_xz.dxf")
    result_xz = export_dxf(bracket, dxf_xz, section_plane="XZ")
    print(f"結果: {'成功' if result_xz else '失敗'}\n")

    # YZ平面（サイドビュー）のDXFエクスポート
    print("--- YZ平面（サイドビュー）のDXFエクスポート ---")
    dxf_yz = str(output_dir / "bracket_yz.dxf")
    result_yz = export_dxf(bracket, dxf_yz, section_plane="YZ")
    print(f"結果: {'成功' if result_yz else '失敗'}\n")

    # 全形式エクスポート（参照用）
    print("--- 全形式エクスポート（STEP/STL/DXF/SVG） ---")
    results = export_all_formats(bracket, "bracket_test", str(output_dir))
    print(f"エクスポートされたファイル数: {len(results)}")
    for fmt, path in results.items():
        print(f"  {fmt}: {path}")

    # 結果サマリー
    print("\n=== テスト結果サマリー ===")
    success_count = sum([result_xy, result_xz, result_yz])
    print(f"DXFエクスポート成功数: {success_count}/3")

    if success_count == 3:
        print("[SUCCESS] すべてのDXFエクスポートが成功しました!")
        return True
    else:
        print("[WARNING] 一部のDXFエクスポートが失敗しました")
        return False


def test_2d_sketch_export():
    """2DスケッチのDXFエクスポートテスト"""
    print("\n\n=== 2DスケッチDXFエクスポートテスト ===\n")

    # 2Dスケッチ作成
    sketch = (
        cq.Workplane("XY")
        .rect(100, 80)
        .rect(60, 40, forConstruction=True).vertices()
        .circle(5)
    )

    output_dir = Path("outputs/test_dxf")
    output_dir.mkdir(parents=True, exist_ok=True)

    dxf_2d = str(output_dir / "sketch_2d.dxf")
    result = export_dxf(sketch, dxf_2d)

    print(f"結果: {'成功' if result else '失敗'}\n")
    return result


if __name__ == "__main__":
    # 3Dモデルのテスト
    test_3d_success = test_dxf_export()

    # 2Dスケッチのテスト
    test_2d_success = test_2d_sketch_export()

    # 最終結果
    print("\n" + "="*50)
    if test_3d_success and test_2d_success:
        print("[SUCCESS] すべてのテストが成功しました!")
        print("\n生成されたファイル:")
        print("  outputs/test_dxf/bracket_xy.dxf    - XY平面断面")
        print("  outputs/test_dxf/bracket_xz.dxf    - XZ平面断面")
        print("  outputs/test_dxf/bracket_yz.dxf    - YZ平面断面")
        print("  outputs/test_dxf/sketch_2d.dxf     - 2Dスケッチ")
    else:
        print("[WARNING] 一部のテストが失敗しました")
        sys.exit(1)
