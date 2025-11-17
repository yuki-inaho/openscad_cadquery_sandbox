#!/usr/bin/env python3
"""
トイプロブレム1: 単純な箱に穴を開けてDXFで検出

TDDステップ:
1. Red: テストを書いて実行（失敗確認）
2. Green: 最小限の実装でテスト通過
3. Refactor: コードをきれいに

目的:
- 基本的な穴開け→DXFエクスポート→検出が動作するか確認
- section()の高さ指定の理解
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import cadquery as cq
from tests.test_utils import export_and_verify_dxf, print_test_result, export_step_for_visual_check


def create_simple_box_with_hole():
    """
    10x10x10mmの箱の中央に直径6mmの穴を開ける

    座標系:
    - 箱: X=[-5, 5], Y=[-5, 5], Z=[0, 10]
    - 穴: 中心(0, 0)、Z方向を貫通、φ6mm
    """
    box = (
        cq.Workplane("XY")
        .box(10, 10, 10, centered=(True, True, False))
        .faces(">Z")
        .workplane()
        .circle(3)  # 半径3mm = 直径6mm
        .cutThruAll()
    )
    return box


def test_simple_box_with_hole():
    """
    テスト: XY断面で穴が検出できるか

    期待結果:
    - section(height=5): 箱の中央を通る
    - CIRCLE 1個検出
    - φ6mm
    """
    print("=" * 80)
    print("トイプロブレム1: 単純な箱に穴")
    print("=" * 80)
    print()

    # 実装
    model = create_simple_box_with_hole()

    # 目視確認用STEP
    step_path = export_step_for_visual_check(model, "toy_01")
    print(f"[INFO] STEP file: {step_path}\n")

    # テスト1: Z=5mmで穴が見えるか
    success, message = export_and_verify_dxf(
        model=model,
        test_name="toy_01",
        section_plane="XY",
        section_height=5.0,
        expected_circles=1,
        expected_diameter=6.0,
        tolerance=0.1
    )

    print_test_result("Test 1: XY断面 (height=5mm)", success, message)

    if not success:
        print("❌ トイプロブレム1 失敗")
        print("\nデバッグヒント:")
        print("  - section(height=5)で箱の中央を通るはず")
        print("  - 穴がZ方向を貫通しているか確認")
        print("  - STEPファイルを目視確認")
        return False

    print("=" * 80)
    print("✅ トイプロブレム1 成功!")
    print("=" * 80)
    return True


if __name__ == "__main__":
    success = test_simple_box_with_hole()
    sys.exit(0 if success else 1)
