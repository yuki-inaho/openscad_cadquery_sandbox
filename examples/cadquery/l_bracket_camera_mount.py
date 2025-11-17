#!/usr/bin/env python3
"""
L字カメラマウントブラケット生成スクリプト（フィレット優先版）
CadQueryを使用してパラメトリックなL字ブラケットを生成

実装順序:
1. 水平板・垂直板作成（穴なし）
2. union
3. フィレット適用（L字の角を丸める）
4. 穴を開ける
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import cadquery as cq
from scripts.cadquery_utils import save_model_with_openscad_support


def create_l_bracket_camera_mount():
    """L字カメラマウントブラケットを生成（フィレット優先版）"""

    # パラメータ定義
    t = 2.0  # 板厚

    # 水平板（底板）寸法
    horizontal_width = 80.0
    horizontal_depth = 50.0

    # 垂直板（背板）寸法
    vertical_width = 80.0
    vertical_height = 40.0

    # 三脚用穴（水平板）
    tripod_hole_diameter = 6.5
    tripod_x = 0.0
    tripod_y = -5.0

    # カメラ固定用穴（垂直板）- グローバル座標
    camera_hole_diameter = 3.2
    camera_x_left = -31.5
    camera_x_right = 31.5
    camera_z_bottom = t + 13.0  # Z=15mm
    camera_z_top = t + 23.0     # Z=25mm

    # フィレット
    bend_radius = 3.0
    edge_radius = 1.5

    print("[INFO] L字ブラケット生成開始（フィレット優先版）\n")

    # ====================================================================
    # ステップ1: 水平板（穴なし）
    # ====================================================================
    print("[1/6] 水平板作成中（穴なし）...")
    horizontal_plate = (
        cq.Workplane("XY")
        .box(horizontal_width, horizontal_depth, t, centered=(True, True, False))
    )
    print("  水平板作成完了")

    # ====================================================================
    # ステップ2: 垂直板（カメラ穴あり）
    # ====================================================================
    print("[2/6] 垂直板作成中（カメラ穴あり）...")
    # 回転前の座標でカメラ穴を計算: 回転前のY = 22 - グローバルZ
    vertical_plate_before_rotation_y_bottom = vertical_height/2 + t - camera_z_bottom  # 7.0
    vertical_plate_before_rotation_y_top = vertical_height/2 + t - camera_z_top        # -3.0

    vertical_plate = (
        cq.Workplane("XY")
        .box(vertical_width, vertical_height, t, centered=(True, True, False))
        # 回転前に穴を開ける
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
        # 回転・移動
        .rotate((0, 0, 0), (1, 0, 0), -90)
        .translate((0, -horizontal_depth/2, vertical_height/2 + t))
    )
    print("  垂直板作成完了（カメラ穴4個）")

    # ====================================================================
    # ステップ3: union
    # ====================================================================
    print("[3/6] 水平板と垂直板をunion中...")
    bracket = horizontal_plate.union(vertical_plate)
    print("  union完了（L字一体構造）")

    # ====================================================================
    # ステップ4: フィレット適用（穴開け前）
    # ====================================================================
    print("[4/6] フィレット適用中（全エッジ）...")

    # 4.1 L字内側角のフィレット（R3.0mm）
    print("  [4.1] L字内側角フィレット...")
    try:
        # 垂直板下端のエッジ（Z=2mm付近、Y<0）
        bracket = bracket.edges("|X and (not >Z) and <Y").fillet(bend_radius)
        print(f"    ✓ 内側角フィレット完了: R{bend_radius}mm")
    except Exception as e:
        print(f"    ✗ 内側角フィレット失敗: {e}")

    # 4.2 垂直板上端後ろのフィレット（R1.5mm）
    print("  [4.2] 垂直板上端後ろフィレット...")
    try:
        bracket = bracket.edges("|X and >Z and <Y").fillet(edge_radius)
        print(f"    ✓ 垂直板上端後ろフィレット完了: R{edge_radius}mm")
    except Exception as e:
        print(f"    ✗ 垂直板上端後ろフィレット失敗: {e}")

    # 4.3 水平板外側のフィレット（R1.5mm）
    print("  [4.3] 水平板外側フィレット...")
    try:
        bracket = bracket.edges("|Z and >Y").fillet(edge_radius)
        print(f"    ✓ 水平板外側フィレット完了: R{edge_radius}mm")
    except Exception as e:
        print(f"    ✗ 水平板外側フィレット失敗: {e}")

    print("  フィレット適用完了\n")

    # ====================================================================
    # ステップ5: 三脚穴を開ける
    # ====================================================================
    print("[5/6] 三脚穴作成中...")
    bracket = (
        bracket
        .faces(">Z")
        .workplane()
        .center(tripod_x, tripod_y)
        .circle(tripod_hole_diameter / 2)
        .cutThruAll()
    )
    print(f"  三脚穴: φ{tripod_hole_diameter}mm at ({tripod_x}, {tripod_y})")

    # ====================================================================
    # ステップ6: カメラ穴（スキップ - 垂直板作成時に開け済み）
    # ====================================================================
    print("[6/6] カメラ穴作成完了（垂直板作成時に開け済み）...")
    print(f"  カメラ穴: φ{camera_hole_diameter}mm × 4個")
    print(f"    位置: X={camera_x_left}/{camera_x_right}mm, Z={camera_z_bottom}/{camera_z_top}mm")

    print("\n[INFO] L字ブラケット生成完了\n")

    return bracket


def main():
    """メイン処理"""
    print("=== L字カメラマウントブラケット生成 ===\n")

    # L字ブラケット生成
    bracket = create_l_bracket_camera_mount()

    # 各種フォーマットで保存
    results = save_model_with_openscad_support(
        bracket,
        "l_bracket_camera_mount",
        output_dir="outputs/l_bracket",
        create_projections=True
    )

    print("\n=== 生成完了 ===")
    print("  - STEP: CADソフトウェアで編集可能")
    print("  - STL: 3Dプリント/加工用")
    print("  - SCAD: OpenSCADでの可視化用")
    print("  - 2D Projections: トップ/フロント/サイドビュー")
    print("\n[完了] L字カメラマウントブラケットの生成が完了しました")


if __name__ == "__main__":
    main()
