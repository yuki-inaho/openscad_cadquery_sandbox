#!/usr/bin/env python3
"""
垂直板の回転・配置を修正する方法の検証

3つの方法を比較:
A. 回転の中心を変更: rotate((0, 0, 20), ...)
B. translate後にZ方向移動: translate((0, -25, 20))
C. 回転後に別途Z移動: rotate() → translate((0, -25, 0)) → translate((0, 0, 20))
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import cadquery as cq


def test_rotation_methods():
    """3つの回転・配置方法を比較"""

    print("=" * 80)
    print("垂直板の配置方法の検証")
    print("=" * 80)
    print()

    t = 2.0

    # 水平板
    h_plate = cq.Workplane("XY").box(80, 50, t, centered=(True, True, False))

    print("【水平板】")
    bb = h_plate.val().BoundingBox()
    print(f"  Z: {bb.zmin:.2f} 〜 {bb.zmax:.2f}")
    print()

    # 現在の方法（問題あり）
    print("【現在の方法（問題あり）】")
    v_plate_current = (
        cq.Workplane("XY")
        .box(80, 40, t, centered=(True, True, False))
        .rotate((0, 0, 0), (1, 0, 0), -90)
        .translate((0, -25, 0))
    )

    bb = v_plate_current.val().BoundingBox()
    print(f"  Y: {bb.ymin:.2f} 〜 {bb.ymax:.2f}")
    print(f"  Z: {bb.zmin:.2f} 〜 {bb.zmax:.2f}")
    print(f"  期待: Y=[-25, -23], Z=[0, 40]")
    print(f"  結果: {'❌ 不正' if bb.zmin < -1 or bb.zmax < 30 else '✅ 正常'}")
    print()

    # 方法A: 回転の中心を(0, 0, 20)に変更
    print("【方法A: 回転中心を(0, 0, 20)に変更】")
    v_plate_a = (
        cq.Workplane("XY")
        .box(80, 40, t, centered=(True, True, False))
        .rotate((0, 0, 20), (1, 0, 0), -90)
        .translate((0, -25, 0))
    )

    bb = v_plate_a.val().BoundingBox()
    print(f"  Y: {bb.ymin:.2f} 〜 {bb.ymax:.2f}")
    print(f"  Z: {bb.zmin:.2f} 〜 {bb.zmax:.2f}")
    print(f"  期待: Y=[-25, -23], Z=[0, 40]")
    print(f"  結果: {'✅ 正常' if abs(bb.zmin - 0) < 1 and abs(bb.zmax - 40) < 1 else '❌ 不正'}")
    print()

    # 方法B: translate(0, -25, 20)
    print("【方法B: translate(0, -25, 20)】")
    v_plate_b = (
        cq.Workplane("XY")
        .box(80, 40, t, centered=(True, True, False))
        .rotate((0, 0, 0), (1, 0, 0), -90)
        .translate((0, -25, 20))
    )

    bb = v_plate_b.val().BoundingBox()
    print(f"  Y: {bb.ymin:.2f} 〜 {bb.ymax:.2f}")
    print(f"  Z: {bb.zmin:.2f} 〜 {bb.zmax:.2f}")
    print(f"  期待: Y=[-25, -23], Z=[0, 40]")
    print(f"  結果: {'✅ 正常' if abs(bb.zmin - 0) < 1 and abs(bb.zmax - 40) < 1 else '❌ 不正'}")
    print()

    # 方法C: 2段階translate
    print("【方法C: 2段階translate】")
    v_plate_c = (
        cq.Workplane("XY")
        .box(80, 40, t, centered=(True, True, False))
        .rotate((0, 0, 0), (1, 0, 0), -90)
        .translate((0, -25, 0))
        .translate((0, 0, 20))
    )

    bb = v_plate_c.val().BoundingBox()
    print(f"  Y: {bb.ymin:.2f} 〜 {bb.ymax:.2f}")
    print(f"  Z: {bb.zmin:.2f} 〜 {bb.zmax:.2f}")
    print(f"  期待: Y=[-25, -23], Z=[0, 40]")
    print(f"  結果: {'✅ 正常' if abs(bb.zmin - 0) < 1 and abs(bb.zmax - 40) < 1 else '❌ 不正'}")
    print()

    # 各方法でunion後のバウンディングボックスを確認
    print("=" * 80)
    print("【union後のバウンディングボックス比較】")
    print("=" * 80)
    print()

    methods = [
        ("現在の方法", v_plate_current),
        ("方法A", v_plate_a),
        ("方法B", v_plate_b),
        ("方法C", v_plate_c),
    ]

    for method_name, v_plate in methods:
        bracket = h_plate.union(v_plate)
        bb = bracket.val().BoundingBox()

        is_correct = (
            abs(bb.zmin - 0) < 1 and
            abs(bb.zmax - 42) < 1
        )

        print(f"{method_name}:")
        print(f"  Z: {bb.zmin:.2f} 〜 {bb.zmax:.2f} (期待: 0.00 〜 42.00)")
        print(f"  {'✅ L字形状' if is_correct else '❌ T字形状'}")
        print()

    # 推奨方法でSTEP保存
    print("=" * 80)
    print("【推奨方法: 方法B】")
    print("=" * 80)
    print("理由: 最もシンプルで分かりやすい")
    print()

    output_dir = Path("outputs/verify_shape")
    output_dir.mkdir(parents=True, exist_ok=True)

    # 方法Bでunion
    bracket_correct = h_plate.union(v_plate_b)
    step_path = output_dir / "correct_l_shape.step"
    cq.exporters.export(bracket_correct, str(step_path))
    print(f"STEP保存: {step_path}")


if __name__ == "__main__":
    test_rotation_methods()
