#!/usr/bin/env python3
"""
エッジデバッグスクリプト

目的:
- L字ブラケットの全エッジを解析
- L字内側角のエッジを特定
- 正しいフィレットセレクタを見つける
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import cadquery as cq
from OCP.TopoDS import TopoDS_Edge
from OCP.BRep import BRep_Tool
from OCP.GeomAbs import GeomAbs_Line, GeomAbs_Circle, GeomAbs_Ellipse, GeomAbs_BSplineCurve


def get_edge_info(edge):
    """エッジの詳細情報を取得"""
    # エッジの始点・終点（CadQueryのネイティブメソッドを使用）
    start_vec = edge.startPoint()
    end_vec = edge.endPoint()
    start_pt = (start_vec.x, start_vec.y, start_vec.z)
    end_pt = (end_vec.x, end_vec.y, end_vec.z)

    # エッジの長さ
    length = edge.Length()

    # エッジのタイプ（簡易判定）
    geom_type = edge.geomType()
    if geom_type == "LINE":
        edge_type = "Line"
    elif geom_type == "CIRCLE":
        edge_type = "Circle"
    elif geom_type == "ELLIPSE":
        edge_type = "Ellipse"
    elif geom_type == "BSPLINE":
        edge_type = "Spline"
    else:
        edge_type = geom_type

    # 方向ベクトル（Lineの場合）
    if edge_type == "Line":
        direction = (
            end_pt[0] - start_pt[0],
            end_pt[1] - start_pt[1],
            end_pt[2] - start_pt[2]
        )
        # 正規化
        mag = (direction[0]**2 + direction[1]**2 + direction[2]**2)**0.5
        if mag > 1e-6:
            direction = tuple(d / mag for d in direction)
    else:
        direction = None

    return {
        'type': edge_type,
        'start': start_pt,
        'end': end_pt,
        'length': length,
        'direction': direction
    }


def analyze_bracket_edges():
    """L字ブラケットのエッジを解析"""
    print("=" * 80)
    print("L字ブラケット エッジ解析")
    print("=" * 80)

    # L字ブラケット生成（穴なし、フィレットなし）
    t = 2.0
    horizontal_width = 80.0
    horizontal_depth = 50.0
    vertical_width = 80.0
    vertical_height = 40.0

    camera_hole_diameter = 3.2
    camera_x_left = -31.5
    camera_x_right = 31.5
    camera_z_bottom = 15.0
    camera_z_top = 25.0

    # 回転前Y座標
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
    tripod_hole_diameter = 6.5
    tripod_x = 0.0
    tripod_y = -5.0
    bracket = (
        bracket
        .faces(">Z")
        .workplane()
        .center(tripod_x, tripod_y)
        .circle(tripod_hole_diameter / 2)
        .cutThruAll()
    )

    print("\n" + "=" * 80)
    print("【ステップ1】全エッジの解析")
    print("=" * 80)

    all_edges = bracket.edges().vals()
    print(f"\n総エッジ数: {len(all_edges)}")

    # エッジをタイプ別に分類
    edges_by_type = {}
    for i, edge in enumerate(all_edges):
        info = get_edge_info(edge)
        edge_type = info['type']
        if edge_type not in edges_by_type:
            edges_by_type[edge_type] = []
        edges_by_type[edge_type].append((i, info))

    print("\nエッジタイプ別:")
    for edge_type, edges in sorted(edges_by_type.items()):
        print(f"  {edge_type}: {len(edges)}個")

    print("\n" + "=" * 80)
    print("【ステップ2】L字内側角エッジの候補")
    print("=" * 80)
    print("\nL字内側角の予想位置:")
    print("  Z ≈ 2mm (水平板と垂直板の接合部)")
    print("  Y ≈ -25mm (垂直板の位置)")
    print("  X方向に伸びる (|X)")
    print("  長さ ≈ 80mm")

    # L字内側角エッジの候補を探す
    print("\n候補エッジ:")
    candidates = []
    for i, info in edges_by_type.get('Line', []):
        # Z座標が2mm付近
        if abs(info['start'][2] - 2.0) < 0.5 and abs(info['end'][2] - 2.0) < 0.5:
            # Y座標が-25mm付近
            if abs(info['start'][1] + 25.0) < 0.5 and abs(info['end'][1] + 25.0) < 0.5:
                # X方向（長さが長い）
                if info['length'] > 60:
                    candidates.append((i, info))
                    print(f"\n  候補{len(candidates)}: エッジ#{i}")
                    print(f"    始点: ({info['start'][0]:.2f}, {info['start'][1]:.2f}, {info['start'][2]:.2f})")
                    print(f"    終点: ({info['end'][0]:.2f}, {info['end'][1]:.2f}, {info['end'][2]:.2f})")
                    print(f"    長さ: {info['length']:.2f}mm")
                    print(f"    方向: X方向")

    if not candidates:
        print("\n  ✗ 候補が見つかりませんでした")
        print("\n  全Lineエッジを表示:")
        for i, info in edges_by_type.get('Line', [])[:20]:  # 最初の20個
            print(f"\n  エッジ#{i}:")
            print(f"    始点: ({info['start'][0]:.2f}, {info['start'][1]:.2f}, {info['start'][2]:.2f})")
            print(f"    終点: ({info['end'][0]:.2f}, {info['end'][1]:.2f}, {info['end'][2]:.2f})")
            print(f"    長さ: {info['length']:.2f}mm")

    print("\n" + "=" * 80)
    print("【ステップ3】各セレクタの動作確認")
    print("=" * 80)

    selectors = [
        "|X",
        "|Y",
        "|Z",
        ">Z",
        "<Y",
        "|X and >Z",
        "|X and <Y",
        ">Z and <Y",
        "|X and >Z and <Y",  # 現在のセレクタ
        "#Z",  # Z方向に平行
        "not #Z",  # Z方向に平行でない
    ]

    for selector in selectors:
        try:
            selected_edges = bracket.edges(selector).vals()
            print(f"\n'{selector}': {len(selected_edges)}個")
            if len(selected_edges) > 0 and len(selected_edges) <= 5:
                for i, edge in enumerate(selected_edges[:5]):
                    info = get_edge_info(edge)
                    print(f"  {i+1}. ({info['start'][0]:.1f}, {info['start'][1]:.1f}, {info['start'][2]:.1f}) → "
                          f"({info['end'][0]:.1f}, {info['end'][1]:.1f}, {info['end'][2]:.1f}), "
                          f"長さ{info['length']:.1f}mm, {info['type']}")
        except Exception as e:
            print(f"\n'{selector}': エラー - {e}")

    print("\n" + "=" * 80)
    print("【ステップ4】フィレット適用テスト")
    print("=" * 80)

    # 候補セレクタでフィレットを試行
    test_selectors = [
        ("|X and >Z and <Y", "現在のセレクタ"),
        ("(>Z[-0.1:2.5] and <Y[-26:-24])", "位置ベース（Z=2, Y=-25付近）"),
    ]

    # 候補エッジの手動選択
    if candidates:
        idx = candidates[0][0]
        test_selectors.append((None, f"手動選択（エッジ#{idx}）", idx))

    for item in test_selectors:
        if len(item) == 2:
            selector, label = item
            manual_idx = None
        else:
            selector, label, manual_idx = item

        print(f"\n{label}:")
        try:
            bracket_test = horizontal_plate.union(vertical_plate)
            bracket_test = (
                bracket_test
                .faces(">Z")
                .workplane()
                .center(tripod_x, tripod_y)
                .circle(tripod_hole_diameter / 2)
                .cutThruAll()
            )

            if manual_idx is not None:
                # 手動選択
                all_edges_test = bracket_test.edges().vals()
                edge_to_fillet = all_edges_test[manual_idx]
                # 手動でのフィレットは複雑なので、スキップ
                print(f"  手動選択されたエッジはフィレット適用のテストをスキップ")
            else:
                # セレクタでフィレット
                bracket_test = bracket_test.edges(selector).fillet(3.0)
                print(f"  ✓ フィレット適用成功!")

        except Exception as e:
            print(f"  ✗ フィレット失敗: {e}")

    print("\n" + "=" * 80)
    print("結論")
    print("=" * 80)
    if candidates:
        print(f"\nL字内側角エッジの候補: {len(candidates)}個見つかりました")
        print("しかし、現在のセレクタ '|X and >Z and <Y' ではフィレットが失敗します。")
        print("\n推奨アクション:")
        print("  1. セレクタを変更する")
        print("  2. またはフィレットを穴開け前に適用する")
        print("  3. または手動でエッジを選択する")
    else:
        print("\nL字内側角エッジが見つかりませんでした。")
        print("union操作により、期待されるエッジが生成されていない可能性があります。")


if __name__ == "__main__":
    analyze_bracket_edges()
