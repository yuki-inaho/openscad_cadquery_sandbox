#!/usr/bin/env python3
"""
L字カメラマウントブラケット生成スクリプト
CadQueryを使用してパラメトリックなL字ブラケットを生成
"""

import sys
from pathlib import Path

# scriptsモジュールをインポート可能にする
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import cadquery as cq
from scripts.cadquery_utils import save_model_with_openscad_support


def create_l_bracket_camera_mount():
    """
    L字カメラマウントブラケットを生成（修正版）

    仕様:
    - 外形: 80mm x 50mm、板厚2.0mm
    - L字形状（90度曲げ）
    - 水平板: 三脚取り付け用穴 φ6.5
    - 垂直板: カメラ固定用穴 4-M3

    座標系:
    - 原点: L字の中心（centered=True使用）
    - X: 幅方向（-40〜+40mm）
    - Y: 奥行き方向（-26〜+25mm）
    - Z: 高さ方向（-1〜+21mm）

    修正履歴:
    - 2025-11-17: union後に穴を開ける方式に変更（穴消失問題の修正）
    """

    # パラメータ定義
    t = 2.0  # 板厚

    # 水平板（底板）寸法
    horizontal_width = 80.0      # X方向
    horizontal_depth = 50.0      # Y方向

    # 垂直板（背板）寸法
    vertical_width = 80.0        # X方向
    vertical_height = 40.0       # Z方向

    # 三脚用穴（水平板）
    tripod_hole_diameter = 6.5
    # centered=True基準での位置（中心からのオフセット）
    tripod_offset_x = 0.0        # X中央
    tripod_offset_y = -5.0       # Y中央から-5mm（20-25=-5）

    # カメラ固定用穴（垂直板）4-M3パターン
    camera_hole_diameter = 3.2  # M3通し穴

    # centered=True基準での位置（中心からのオフセット）
    camera_offset_x_left = -31.5   # 8.5 - 40 = -31.5
    camera_offset_x_right = 31.5   # 71.5 - 40 = 31.5
    camera_offset_z_bottom = -12.0 # 8 - 20 = -12
    camera_offset_z_top = -4.0     # 16 - 20 = -4

    # 曲げR
    bend_radius = 4.0
    edge_radius = 1.5

    # ====================================================================
    # 修正案A: union後に穴を開ける方式
    # ====================================================================

    print("[INFO] 修正版L字ブラケット生成開始（union後穴あけ方式）")

    # ステップ1: 水平板（穴なし）
    print("[1/6] 水平板作成中（穴なし）...")
    horizontal_base = (
        cq.Workplane("XY")
        .box(horizontal_width, horizontal_depth, t, centered=True)
    )

    # ステップ2: 垂直板（穴なし）
    print("[2/6] 垂直板作成中（穴なし）...")
    vertical_base = (
        cq.Workplane("XZ")
        .box(vertical_width, vertical_height, t, centered=True)
        # 位置調整: Y=-26mm（水平板の後端-2mmと接続）
        .translate((0, -(horizontal_depth/2 + t/2), vertical_height/2 + t/2))
    )

    # ステップ3: union（穴なし状態で結合）
    print("[3/6] 水平板と垂直板をunion中...")
    bracket = horizontal_base.union(vertical_base)
    print("[SUCCESS] union完了（穴なし状態）")

    # ステップ4: union後に三脚穴を開ける
    print("[4/6] 三脚穴を開ける中...")
    bracket = (
        bracket
        .faces(">Z")  # 水平板の上面を選択
        .workplane()
        .center(tripod_offset_x, tripod_offset_y)  # (0, -5)
        .circle(tripod_hole_diameter / 2)
        .cutThruAll()
    )
    print(f"[SUCCESS] 三脚穴完了: φ{tripod_hole_diameter}mm at ({tripod_offset_x}, {tripod_offset_y})")

    # ステップ5: union後にカメラ固定穴を開ける
    print("[5/6] カメラ固定穴4個を開ける中...")
    bracket = (
        bracket
        .faces("<Y")  # 垂直板の背面を選択
        .workplane()
        .pushPoints([
            (camera_offset_x_left, camera_offset_z_bottom),   # 左下
            (camera_offset_x_left, camera_offset_z_top),      # 左上
            (camera_offset_x_right, camera_offset_z_bottom),  # 右下
            (camera_offset_x_right, camera_offset_z_top),     # 右上
        ])
        .circle(camera_hole_diameter / 2)
        .cutThruAll()
    )
    print(f"[SUCCESS] カメラ穴完了: φ{camera_hole_diameter}mm × 4個")
    print(f"  左列 X={camera_offset_x_left}mm, 右列 X={camera_offset_x_right}mm")
    print(f"  下列 Z={camera_offset_z_bottom}mm, 上列 Z={camera_offset_z_top}mm")

    # ステップ6: フィレット
    print("[6/6] フィレット適用中...")
    # 内側フィレット
    try:
        bracket = bracket.edges("|X and <Y and <Z").fillet(bend_radius)
        print(f"[SUCCESS] 内側フィレット完了: R{bend_radius}mm")
    except Exception as e:
        print(f"[WARNING] 内側フィレット失敗: {e}")

    # 外側エッジフィレット
    try:
        bracket = bracket.edges("|Z and >Y").fillet(edge_radius)
        print(f"[SUCCESS] 外側フィレット完了: R{edge_radius}mm")
    except Exception as e:
        print(f"[WARNING] 外側フィレット失敗: {e}")

    print("[INFO] L字ブラケット生成完了\n")

    return bracket




def main():
    """メイン処理"""
    print("=== L字カメラマウントブラケット生成 ===\n")

    # L字ブラケット生成
    bracket = create_l_bracket_camera_mount()

    # 各種フォーマットで保存（新しいユーティリティを使用）
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
    print("\nレンダリングコマンド:")
    print("  python3 scripts/renderer.py outputs/l_bracket/l_bracket_camera_mount.scad output.png")
    print("\n[完了] L字カメラマウントブラケットの生成が完了しました")


if __name__ == "__main__":
    main()
