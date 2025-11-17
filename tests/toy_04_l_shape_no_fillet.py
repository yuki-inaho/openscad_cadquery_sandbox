#!/usr/bin/env python3
"""
トイプロブレム4: L字（フィレットなし）でDXF穴検出

目的:
- 実際のL字形状で穴が検出できるか確認
- 適切なsection高さを特定
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import cadquery as cq
from tests.test_utils import export_and_verify_dxf, print_test_result, export_step_for_visual_check


def create_l_shape_no_fillet():
    """
    L字ブラケット（フィレットなし）

    グローバル座標系:
    - 水平板: X=[-40, 40], Y=[-25, 25], Z=[0, 2]
    - 垂直板: X=[-40, 40], Y=[-25, -23], Z=[2, 42]
    - 三脚穴: (0, -5), φ6.5mm, Z方向貫通
    - カメラ穴: X={-31.5, 31.5}, Z={10, 18}, φ3.2mm, Y方向貫通
    """

    t = 2.0

    # 水平板（穴なし）
    h_plate = cq.Workplane("XY").box(80, 50, t, centered=(True, True, False))

    # 垂直板（穴なし）
    v_plate = (
        cq.Workplane("XY")
        .box(80, 40, t, centered=(True, True, False))
        .rotate((0, 0, 0), (1, 0, 0), -90)
        .translate((0, -25, 0))
    )

    # union
    bracket = h_plate.union(v_plate)

    # 三脚穴（union後）
    bracket = (
        bracket
        .faces(">Z")
        .workplane()
        .center(0, -5)
        .circle(3.25)
        .cutThruAll()
    )

    # カメラ穴（union後）
    bracket = (
        bracket
        .faces("<Y")
        .workplane()
        .pushPoints([(-31.5, 10), (-31.5, 18), (31.5, 10), (31.5, 18)])
        .circle(1.6)
        .cutThruAll()
    )

    return bracket


def test_l_shape_no_fillet():
    """
    テスト: L字ブラケットの穴検出

    期待結果:
    - XY断面（Z=1mm）: CIRCLE 1個、φ6.5mm（三脚穴）
    - XZ断面（Y=-24mm）: CIRCLE 4個、φ3.2mm（カメラ穴）
    """
    print("=" * 80)
    print("トイプロブレム4: L字（フィレットなし）")
    print("=" * 80)
    print()

    # 実装
    model = create_l_shape_no_fillet()

    # 目視確認用STEP
    step_path = export_step_for_visual_check(model, "toy_04")
    print(f"[INFO] STEP file: {step_path}\n")

    # テスト1: XY断面（Z=1mm）で三脚穴
    success1, message1 = export_and_verify_dxf(
        model=model,
        test_name="toy_04",
        section_plane="XY",
        section_height=1.0,  # 水平板の中央
        expected_circles=1,
        expected_diameter=6.5,
        tolerance=0.1
    )

    print_test_result("Test 1: XY断面 (Z=1mm) - 三脚穴", success1, message1)

    # テスト2: XZ断面（Y=-24mm）でカメラ穴
    # 垂直板はY=[-25, -23]なので、Y=-24が中央
    # rotate(X軸, 90度)するとY→Zになるので、section(height=-24)
    success2, message2 = export_and_verify_dxf(
        model=model,
        test_name="toy_04",
        section_plane="XZ",
        section_height=-24.0,  # 垂直板の中央（回転後のZ座標）
        expected_circles=4,
        expected_diameter=3.2,
        tolerance=0.1
    )

    print_test_result("Test 2: XZ断面 (Y=-24mm) - カメラ穴", success2, message2)

    if success1 and success2:
        print("=" * 80)
        print("✅ トイプロブレム4 成功!")
        print("=" * 80)
        return True
    else:
        print("=" * 80)
        print("❌ トイプロブレム4 失敗")
        print("=" * 80)
        return False


if __name__ == "__main__":
    success = test_l_shape_no_fillet()
    sys.exit(0 if success else 1)
