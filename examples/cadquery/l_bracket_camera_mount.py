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
    L字カメラマウントブラケットを生成（シンプル版）

    仕様:
    - 外形: 80mm x 50mm、板厚2.0mm
    - L字形状（90度曲げ）
    - 水平板: 三脚取り付け用穴 φ6.5
    - 垂直板: カメラ固定用穴 4-M3

    座標系（グローバル、原点は水平板中心底面）:
    - X: 幅方向（-40〜+40mm）
    - Y: 奥行き方向（-25〜+25mm）
    - Z: 高さ方向（0〜42mm）

    修正履歴:
    - 2025-11-17: union後に穴を開ける方式に変更（穴消失問題の修正）
    - 2025-11-17: Workplane("XY")のみ使用、rotate()で回転（座標系シンプル化）
    """

    # パラメータ定義
    t = 2.0  # 板厚

    # 水平板（底板）寸法
    horizontal_width = 80.0      # X方向
    horizontal_depth = 50.0      # Y方向

    # 垂直板（背板）寸法
    vertical_width = 80.0        # X方向
    vertical_height = 40.0       # Z方向

    # 三脚用穴（水平板）- グローバル座標
    tripod_hole_diameter = 6.5
    tripod_x = 0.0               # X中央
    tripod_y = -5.0              # 曲げ部から20mm（-25 + 20 = -5）

    # カメラ固定用穴（垂直板）- グローバル座標
    camera_hole_diameter = 3.2
    camera_x_left = -31.5        # 左端から8.5mm（-40 + 8.5 = -31.5）
    camera_x_right = 31.5        # 右端から8.5mm（40 - 8.5 = 31.5）
    camera_z_bottom = t + 8.0    # 下端から8mm（2 + 8 = 10）
    camera_z_top = t + 16.0      # 下端から16mm（2 + 16 = 18）

    # 曲げR
    bend_radius = 3.0  # R4以下（少し小さくして安全に）
    edge_radius = 1.5

    print("[INFO] シンプル版L字ブラケット生成開始（修正版: union後穴開け）")

    # ====================================================================
    # ステップ1: 水平板（穴なし）
    # ====================================================================
    print("[1/7] 水平板作成中（穴なし）...")
    horizontal_plate = (
        cq.Workplane("XY")
        .box(horizontal_width, horizontal_depth, t, centered=(True, True, False))
    )
    print("  水平板作成完了（穴なし）")

    # ====================================================================
    # ステップ2: 垂直板（穴あり）
    # ====================================================================
    print("[2/7] 垂直板作成中（穴あり）...")
    # XY平面で作成し、回転前に穴を開ける
    # 回転前の座標系でカメラ穴を計算
    # X軸周りに-90度回転の変換: Y' = Z, Z' = -Y
    # 回転後にグローバルZ={10, 18}になるように、回転前のY座標を計算:
    #   Z' = -Y → Y = -Z'
    # グローバルZ=10（translate後） → translate前Z'=10-22=-12 → 回転前Y=-(-12)=12
    # しかし、これは複雑なので、直接計算:
    # 回転後のZ = translate前のZ + 22
    # translate前のZ = -回転前のY
    # したがって: 回転後のZ = -回転前のY + 22
    # → 回転前のY = 22 - 回転後のZ
    vertical_plate_before_rotation_y_bottom = vertical_height/2 + t - camera_z_bottom  # 22 - 10 = 12
    vertical_plate_before_rotation_y_top = vertical_height/2 + t - camera_z_top        # 22 - 18 = 4

    vertical_plate = (
        cq.Workplane("XY")
        .box(vertical_width, vertical_height, t, centered=(True, True, False))
        # 回転前に穴を開ける
        .faces(">Z")  # 上面（Z=2の面）
        .workplane()
        .pushPoints([
            (camera_x_left, vertical_plate_before_rotation_y_bottom),   # 左下（回転後Z=10）
            (camera_x_left, vertical_plate_before_rotation_y_top),      # 左上（回転後Z=18）
            (camera_x_right, vertical_plate_before_rotation_y_bottom),  # 右下（回転後Z=10）
            (camera_x_right, vertical_plate_before_rotation_y_top),     # 右上（回転後Z=18）
        ])
        .circle(camera_hole_diameter / 2)
        .cutThruAll()
        # X軸周りに-90度回転（XY平面 → XZ平面）
        .rotate((0, 0, 0), (1, 0, 0), -90)
        # Y=-25の位置、Z=22mmに移動（水平板の後端、上端から立つL字形状）
        # Z移動量 = vertical_height/2 + t = 40/2 + 2 = 22mm
        .translate((0, -horizontal_depth/2, vertical_height/2 + t))
    )
    print("  垂直板作成完了（穴あり）")
    print(f"    カメラ穴（回転前Y座標）: {vertical_plate_before_rotation_y_bottom}, {vertical_plate_before_rotation_y_top}")

    # ====================================================================
    # ステップ3: union
    # ====================================================================
    print("[3/7] 水平板と垂直板をunion中...")
    bracket = horizontal_plate.union(vertical_plate)
    print("  union完了（L字一体構造）")

    # ====================================================================
    # ステップ4: union後に三脚穴を開ける
    # ====================================================================
    print("[4/7] 三脚穴作成中（union後）...")
    bracket = (
        bracket
        .faces(">Z")
        .workplane()
        .center(tripod_x, tripod_y)
        .circle(tripod_hole_diameter / 2)
        .cutThruAll()
    )
    print(f"  三脚穴: φ{tripod_hole_diameter}mm at ({tripod_x}, {tripod_y}, {t})")

    # ====================================================================
    # ステップ5: （スキップ - カメラ穴は垂直板作成時に開け済み）
    # ====================================================================
    print("[5/7] カメラ穴作成完了（垂直板作成時に開け済み）...")
    print(f"  カメラ穴: φ{camera_hole_diameter}mm × 4個")
    print(f"    左列 X={camera_x_left}mm, 右列 X={camera_x_right}mm")
    print(f"    下列 Z={camera_z_bottom}mm, 上列 Z={camera_z_top}mm")

    # ====================================================================
    # ステップ6: フィレット（内側）
    # ====================================================================
    print("[6/7] 内側フィレット適用中...")
    try:
        # L字内側角のエッジを選択
        bracket = bracket.edges("|X and >Z and <Y").fillet(bend_radius)
        print(f"  内側フィレット完了: R{bend_radius}mm")
    except Exception as e:
        print(f"  [WARNING] 内側フィレット失敗: {e}")

    # ====================================================================
    # ステップ7: フィレット（外側エッジ）
    # ====================================================================
    print("[7/7] 外側フィレット適用中...")
    try:
        bracket = bracket.edges("|Z and >Y").fillet(edge_radius)
        print(f"  外側フィレット完了: R{edge_radius}mm")
    except Exception as e:
        print(f"  [WARNING] 外側フィレット失敗: {e}")

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
