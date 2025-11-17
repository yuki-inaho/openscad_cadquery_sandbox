#!/usr/bin/env python3
"""
最終確認: 正しいL字形状になるか
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import cadquery as cq


def verify_final_fix():
    """正しい配置を検証"""

    print("=" * 80)
    print("最終確認: 正しいL字形状")
    print("=" * 80)
    print()

    t = 2.0

    # 水平板
    h_plate = cq.Workplane("XY").box(80, 50, t, centered=(True, True, False))

    print("【水平板】")
    bb = h_plate.val().BoundingBox()
    print(f"  Z: {bb.zmin:.2f} 〜 {bb.zmax:.2f}")
    print()

    # 現在の実装（問題あり）
    print("【現在の実装】")
    v_plate_current = (
        cq.Workplane("XY")
        .box(80, 40, t, centered=(True, True, False))
        .rotate((0, 0, 0), (1, 0, 0), -90)
        .translate((0, -25, 0))  # ← 問題: Z方向の移動がない
    )

    bb = v_plate_current.val().BoundingBox()
    print(f"  垂直板 Y: {bb.ymin:.2f} 〜 {bb.ymax:.2f}")
    print(f"  垂直板 Z: {bb.zmin:.2f} 〜 {bb.zmax:.2f}")

    bracket_current = h_plate.union(v_plate_current)
    bb = bracket_current.val().BoundingBox()
    print(f"  union後 Z: {bb.zmin:.2f} 〜 {bb.zmax:.2f} (期待: 0 〜 42)")
    print(f"  結果: {'❌ T字（水平板の下に伸びている）' if bb.zmin < -1 else '❌ 不明'}")
    print()

    # 正しい実装
    print("【正しい実装】")
    v_plate_correct = (
        cq.Workplane("XY")
        .box(80, 40, t, centered=(True, True, False))
        .rotate((0, 0, 0), (1, 0, 0), -90)
        .translate((0, -25, 2))  # ← 修正: Z方向に2mm移動（水平板の厚さ）
    )

    bb = v_plate_correct.val().BoundingBox()
    print(f"  垂直板 Y: {bb.ymin:.2f} 〜 {bb.ymax:.2f}")
    print(f"  垂直板 Z: {bb.zmin:.2f} 〜 {bb.zmax:.2f}")

    bracket_correct = h_plate.union(v_plate_correct)
    bb = bracket_correct.val().BoundingBox()
    print(f"  union後 Z: {bb.zmin:.2f} 〜 {bb.zmax:.2f} (期待: 0 〜 42)")

    is_correct_l = abs(bb.zmin - 0) < 1 and abs(bb.zmax - 42) < 1

    print(f"  結果: {'✅ L字（水平板の上に垂直板が立っている）' if is_correct_l else '❌ 不正'}")
    print()

    # 視覚確認用にSTEP保存
    print("=" * 80)
    print("【STEP保存】")
    print("=" * 80)

    output_dir = Path("outputs/verify_shape")
    output_dir.mkdir(parents=True, exist_ok=True)

    # 現在の実装（T字）
    path_current = output_dir / "current_t_shape.step"
    cq.exporters.export(bracket_current, str(path_current))
    print(f"現在（T字）: {path_current}")

    # 正しい実装（L字）
    path_correct = output_dir / "correct_l_shape_final.step"
    cq.exporters.export(bracket_correct, str(path_correct))
    print(f"修正後（L字）: {path_correct}")

    print()

    # 修正内容のまとめ
    print("=" * 80)
    print("【修正内容のまとめ】")
    print("=" * 80)
    print()
    print("現在のコード:")
    print("  .translate((0, -25, 0))")
    print()
    print("修正後のコード:")
    print("  .translate((0, -25, 2))  # Z方向に水平板の厚さ分移動")
    print()
    print("または:")
    print("  .translate((0, -25, t))  # tは板厚パラメータ")
    print()

    # SVGも保存
    print("=" * 80)
    print("【SVG保存（視覚確認用）】")
    print("=" * 80)

    svg_views = [
        ("front", (0, 1, 0)),
        ("side", (1, 0, 0)),
    ]

    for shape_name, bracket in [("current", bracket_current), ("correct", bracket_correct)]:
        for view_name, proj_dir in svg_views:
            svg_path = output_dir / f"{shape_name}_{view_name}.svg"
            svg_opts = {
                "width": 400,
                "height": 400,
                "marginLeft": 20,
                "marginTop": 20,
                "showAxes": True,
                "projectionDir": proj_dir,
                "strokeWidth": 0.5,
            }
            cq.exporters.export(bracket, str(svg_path), opt=svg_opts)
            print(f"  {svg_path.name}")

    print()


if __name__ == "__main__":
    verify_final_fix()
