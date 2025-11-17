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
    L字カメラマウントブラケットを生成

    仕様:
    - 外形: 80mm x 50mm、板厚2.0mm
    - L字形状（90度曲げ）
    - 水平板: 三脚取り付け用穴 φ6.5
    - 垂直板: カメラ固定用穴 4-M3

    座標系:
    - 原点: L字内側コーナー（曲げ内側）
    - X: 幅方向（0〜80mm）
    - Y: 水平板長さ方向（0〜50mm）
    - Z: 垂直板高さ方向（0〜40mm）
    """

    # パラメータ定義
    # 板厚
    t = 2.0

    # 水平板（底板）寸法
    horizontal_width = 80.0      # X方向
    horizontal_depth = 50.0      # Y方向

    # 垂直板（背板）寸法
    vertical_width = 80.0        # X方向
    vertical_height = 40.0       # Z方向（図面の側面図値）

    # 三脚用穴（水平板）
    tripod_hole_diameter = 6.5
    # 図面上の絶対座標：左端から40mm、曲げ部から20mm
    tripod_abs_x = 40.0
    tripod_abs_y = 20.0

    # カメラ固定用穴（垂直板）4-M3パターン
    camera_hole_diameter = 3.2  # M3通し穴（若干の余裕）

    # 図面上の絶対座標（端面基準）
    # X方向: 左端から8.5mm、右列は左端から71.5mm（= 右端から8.5mm）
    camera_abs_x_left = 8.5
    camera_abs_x_right = 71.5

    # Z方向: 下端から8mm（下穴）、16mm（上穴）
    camera_abs_z_bottom = 8.0
    camera_abs_z_top = 16.0

    # 曲げR（板金らしさを表現）
    bend_radius = 4.0  # R4以下の仕様

    # ステップ1: 水平板（底板）を作成
    # centered=Falseで作成すると、板の実座標は(0,0,0)〜(80,50,2)
    # .faces(">Z").workplane()すると、原点が板上面中心(40, 25, 2)に移動
    horizontal_plate = (
        cq.Workplane("XY")
        .box(horizontal_width, horizontal_depth, t, centered=False)
        # 三脚用穴を開ける
        # Workplane原点(40, 25)からの相対座標を計算
        .faces(">Z")
        .workplane()
        .pushPoints([
            (tripod_abs_x - horizontal_width/2,
             tripod_abs_y - horizontal_depth/2)  # (0, -5)
        ])
        .circle(tripod_hole_diameter / 2)
        .cutThruAll()
    )

    # ステップ2: 垂直板（背板）を作成
    # 水平板の後端（Y=0）に接続するように配置
    # centered=Falseで作成し、Y方向に-t移動
    # 実座標は(0, -2, 0)〜(80, 0, 40)
    # .faces("<Y").workplane()すると、原点が板背面中心(40, -1, 20)に移動
    vertical_plate = (
        cq.Workplane("XZ")
        .box(vertical_width, vertical_height, t, centered=False)
        # Y方向に-t移動して水平板と接続
        .translate((0, -t, 0))
        # カメラ固定用4穴を開ける
        # Workplane原点(40, 20)からの相対座標を計算
        .faces("<Y")
        .workplane()
        .pushPoints([
            (camera_abs_x_left - vertical_width/2,
             camera_abs_z_bottom - vertical_height/2),    # 左下 (-31.5, -12)
            (camera_abs_x_left - vertical_width/2,
             camera_abs_z_top - vertical_height/2),       # 左上 (-31.5, -4)
            (camera_abs_x_right - vertical_width/2,
             camera_abs_z_bottom - vertical_height/2),    # 右下 (31.5, -12)
            (camera_abs_x_right - vertical_width/2,
             camera_abs_z_top - vertical_height/2),       # 右上 (31.5, -4)
        ])
        .circle(camera_hole_diameter / 2)
        .cutThruAll()
    )

    # ステップ3: 水平板と垂直板を結合
    bracket = horizontal_plate.union(vertical_plate)

    # ステップ4: L字の曲げ部分にフィレットを追加（板金らしさを表現）
    # L字内側のエッジを選択してR4のフィレットを追加
    try:
        # L字内側角エッジを選択
        bracket = (
            bracket
            .edges("|X and <Y and <Z")  # L字内側角（Y=0, Z=0付近）
            .fillet(bend_radius)
        )
    except Exception as e:
        print(f"[WARNING] 内側フィレット失敗: {e}")
        pass

    # ステップ5: 外側エッジも軽く丸める（板金加工の現実性）
    edge_radius = 1.5  # R2以下
    try:
        bracket = (
            bracket
            .edges("|Z and >Y")  # 水平板の外側エッジ
            .fillet(edge_radius)
        )
    except Exception as e:
        print(f"[WARNING] 外側フィレット失敗: {e}")
        pass

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
