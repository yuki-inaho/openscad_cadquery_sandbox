#!/usr/bin/env python3
"""
正しいZ移動量を計算
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import cadquery as cq


def calculate_translation():
    """正しいZ移動量を計算"""

    print("=" * 80)
    print("正しいZ移動量の計算")
    print("=" * 80)
    print()

    t = 2.0
    vertical_height = 40.0

    # 回転前の垂直板
    print("【回転前の垂直板】")
    print(f"  Y: [-{vertical_height/2}, {vertical_height/2}] = [-20, 20]")
    print(f"  Z: [0, {t}] = [0, 2]")
    print()

    # X軸周りに-90度回転後
    print("【X軸周りに-90度回転後】")
    print("  回転公式:")
    print("    Y' = Z")
    print("    Z' = -Y")
    print()
    print(f"  元のY=[-20, 20] → Z'=[-(-20), -(20)] = [20, -20]")
    print(f"  元のZ=[0, 2] → Y'=[0, 2]")
    print()
    print(f"  回転後の座標:")
    print(f"    Y: [0, 2]")
    print(f"    Z: [-20, 20]")
    print()

    # 目標位置
    print("【目標位置】")
    print(f"  垂直板: Y=[-25, -23], Z=[2, 42]")
    print(f"  (水平板の上端Z=2から垂直に立つ)")
    print()

    # 必要な移動量
    print("【必要な移動量】")
    current_y = [0, 2]
    target_y = [-25, -23]
    dy = target_y[0] - current_y[0]
    print(f"  Y方向: {current_y} → {target_y} = {dy}mm")

    current_z = [-20, 20]
    target_z = [2, 42]
    dz = target_z[0] - current_z[0]
    print(f"  Z方向: {current_z} → {target_z} = {dz}mm")
    print()

    print(f"  translate({0}, {dy}, {dz})")
    print()

    # 検証
    print("=" * 80)
    print("【検証】")
    print("=" * 80)

    v_plate = (
        cq.Workplane("XY")
        .box(80, vertical_height, t, centered=(True, True, False))
        .rotate((0, 0, 0), (1, 0, 0), -90)
        .translate((0, dy, dz))
    )

    bb = v_plate.val().BoundingBox()
    print(f"  Y: {bb.ymin:.2f} 〜 {bb.ymax:.2f} (期待: -25 〜 -23)")
    print(f"  Z: {bb.zmin:.2f} 〜 {bb.zmax:.2f} (期待: 2 〜 42)")

    is_correct = (
        abs(bb.ymin - (-25)) < 0.1 and
        abs(bb.ymax - (-23)) < 0.1 and
        abs(bb.zmin - 2) < 0.1 and
        abs(bb.zmax - 42) < 0.1
    )

    print(f"  結果: {'✅ 正しい' if is_correct else '❌ 不正'}")
    print()

    # union後も確認
    h_plate = cq.Workplane("XY").box(80, 50, t, centered=(True, True, False))
    bracket = h_plate.union(v_plate)

    bb = bracket.val().BoundingBox()
    print(f"  union後 Z: {bb.zmin:.2f} 〜 {bb.zmax:.2f} (期待: 0 〜 42)")

    is_correct_union = abs(bb.zmin - 0) < 0.1 and abs(bb.zmax - 42) < 0.1
    print(f"  結果: {'✅ L字' if is_correct_union else '❌ 不正'}")
    print()

    # STEP保存
    output_dir = Path("outputs/verify_shape")
    output_dir.mkdir(parents=True, exist_ok=True)

    step_path = output_dir / "verified_l_shape.step"
    cq.exporters.export(bracket, str(step_path))
    print(f"  STEP: {step_path}")

    print()
    print("=" * 80)
    print("【結論】")
    print("=" * 80)
    print(f"  修正コード: .translate((0, -25, {dz}))")
    print()


if __name__ == "__main__":
    calculate_translation()
