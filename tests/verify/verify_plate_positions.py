#!/usr/bin/env python3
"""
板の位置を詳細確認: 水平板と垂直板がどこにあるか
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import cadquery as cq


def verify_plate_positions():
    """各ステップごとに板の位置を確認"""

    print("=" * 80)
    print("板の位置確認")
    print("=" * 80)
    print()

    t = 2.0

    # ステップ1: 水平板（穴なし）
    print("[ステップ1] 水平板（穴なし）")
    h_plate = cq.Workplane("XY").box(80, 50, t, centered=(True, True, False))

    bb = h_plate.val().BoundingBox()
    print(f"  X: {bb.xmin:.2f} 〜 {bb.xmax:.2f}")
    print(f"  Y: {bb.ymin:.2f} 〜 {bb.ymax:.2f}")
    print(f"  Z: {bb.zmin:.2f} 〜 {bb.zmax:.2f}")
    print(f"  期待: X=[-40, 40], Y=[-25, 25], Z=[0, 2]")
    print()

    # ステップ2: 垂直板（回転前、穴なし）
    print("[ステップ2] 垂直板（回転前）")
    v_plate_before_rotate = (
        cq.Workplane("XY")
        .box(80, 40, t, centered=(True, True, False))
    )

    bb = v_plate_before_rotate.val().BoundingBox()
    print(f"  X: {bb.xmin:.2f} 〜 {bb.xmax:.2f}")
    print(f"  Y: {bb.ymin:.2f} 〜 {bb.ymax:.2f}")
    print(f"  Z: {bb.zmin:.2f} 〜 {bb.zmax:.2f}")
    print(f"  期待: X=[-40, 40], Y=[-20, 20], Z=[0, 2]")
    print()

    # ステップ3: 垂直板（回転後、移動前）
    print("[ステップ3] 垂直板（回転後、移動前）")
    v_plate_after_rotate = (
        cq.Workplane("XY")
        .box(80, 40, t, centered=(True, True, False))
        .rotate((0, 0, 0), (1, 0, 0), -90)
    )

    bb = v_plate_after_rotate.val().BoundingBox()
    print(f"  X: {bb.xmin:.2f} 〜 {bb.xmax:.2f}")
    print(f"  Y: {bb.ymin:.2f} 〜 {bb.ymax:.2f}")
    print(f"  Z: {bb.zmin:.2f} 〜 {bb.zmax:.2f}")
    print(f"  回転: X軸周りに-90度")
    print(f"  期待: Y方向が→Z方向、Z方向が→-Y方向")
    print()

    # ステップ4: 垂直板（移動後）
    print("[ステップ4] 垂直板（移動後）")
    v_plate = (
        cq.Workplane("XY")
        .box(80, 40, t, centered=(True, True, False))
        .rotate((0, 0, 0), (1, 0, 0), -90)
        .translate((0, -25, 0))
    )

    bb = v_plate.val().BoundingBox()
    print(f"  X: {bb.xmin:.2f} 〜 {bb.xmax:.2f}")
    print(f"  Y: {bb.ymin:.2f} 〜 {bb.ymax:.2f}")
    print(f"  Z: {bb.zmin:.2f} 〜 {bb.zmax:.2f}")
    print(f"  translate: (0, -25, 0)")
    print(f"  期待: Y=[-25, -23], Z=[0, 40]")
    print()

    # ステップ5: union後
    print("[ステップ5] union後")
    bracket = h_plate.union(v_plate)

    bb = bracket.val().BoundingBox()
    print(f"  X: {bb.xmin:.2f} 〜 {bb.xmax:.2f}")
    print(f"  Y: {bb.ymin:.2f} 〜 {bb.ymax:.2f}")
    print(f"  Z: {bb.zmin:.2f} 〜 {bb.zmax:.2f}")
    print(f"  期待: X=[-40, 40], Y=[-25, 25], Z=[0, 42]")
    print()

    # L字判定
    print("=" * 80)
    print("【L字判定】")
    print("=" * 80)

    is_correct_l = (
        abs(bb.xmin - (-40)) < 0.1 and
        abs(bb.xmax - 40) < 0.1 and
        abs(bb.ymin - (-25)) < 0.1 and
        abs(bb.ymax - 25) < 0.1 and
        abs(bb.zmin - 0) < 0.1 and
        abs(bb.zmax - 42) < 0.1
    )

    if is_correct_l:
        print("✅ L字形状が正しい位置にあります")
    else:
        print("❌ L字形状の位置が不正です")
        print()
        print("問題点:")
        if abs(bb.zmin - 0) > 0.1:
            print(f"  - Z最小値が0ではない: {bb.zmin:.2f}")
        if abs(bb.zmax - 42) > 0.1:
            print(f"  - Z最大値が42ではない: {bb.zmax:.2f}")
            print(f"    → 垂直板の高さまたは位置が誤っている可能性")

    print()

    # 視覚確認用にSTEP保存
    output_dir = Path("outputs/verify_shape")
    output_dir.mkdir(parents=True, exist_ok=True)

    # 各ステップを保存
    step_files = [
        (h_plate, "step1_horizontal_plate.step"),
        (v_plate_before_rotate, "step2_vertical_before_rotate.step"),
        (v_plate_after_rotate, "step3_vertical_after_rotate.step"),
        (v_plate, "step4_vertical_after_translate.step"),
        (bracket, "step5_union.step"),
    ]

    print("=" * 80)
    print("【STEP保存】")
    print("=" * 80)

    for model, filename in step_files:
        path = output_dir / filename
        cq.exporters.export(model, str(path))
        print(f"  {filename}")

    print()


if __name__ == "__main__":
    verify_plate_positions()
