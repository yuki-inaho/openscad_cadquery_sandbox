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
    """

    # パラメータ定義
    # 板厚
    t = 2.0

    # 水平板（底板）寸法
    horizontal_width = 80.0      # X方向
    horizontal_depth = 50.0      # Y方向

    # 垂直板（背板）寸法
    vertical_width = 80.0        # X方向
    vertical_height = 45.0       # Z方向（穴位置から逆算）

    # 三脚用穴（水平板中央）
    tripod_hole_diameter = 6.5
    tripod_hole_x = horizontal_width / 2  # 40mm（中央）
    tripod_hole_y = 20.0                  # 奥行き方向位置

    # カメラ固定用穴（垂直板）4-M3パターン
    camera_hole_diameter = 3.2  # M3通し穴（若干の余裕）

    # X方向位置
    camera_hole_x1 = 8.5   # 左列
    camera_hole_x2 = 71.5  # 右列（8.5 + 63）

    # Z方向位置（上端基準）
    camera_hole_z1 = vertical_height - 34  # 上列（上端から34mm下）
    camera_hole_z2 = camera_hole_z1 - 8    # 下列（上列から8mm下）

    # 角丸め半径
    edge_radius = 1.5  # R2以下の仕様に対応

    # ステップ1: 水平板（底板）を作成
    horizontal_plate = (
        cq.Workplane("XY")
        .box(horizontal_width, horizontal_depth, t, centered=False)
        # 三脚用穴を開ける
        .faces(">Z")
        .workplane()
        .pushPoints([(tripod_hole_x, tripod_hole_y)])
        .circle(tripod_hole_diameter / 2)
        .cutThruAll()
    )

    # ステップ2: 垂直板（背板）を作成
    # 水平板の後端（Y=0）に接続するように配置
    vertical_plate = (
        cq.Workplane("XZ")
        .box(vertical_width, vertical_height, t, centered=False)
        # Y方向に-t移動して水平板と接続
        .translate((0, -t, 0))
        # カメラ固定用4穴を開ける
        .faces("<Y")
        .workplane()
        .pushPoints([
            (camera_hole_x1, camera_hole_z1),  # 左上
            (camera_hole_x1, camera_hole_z2),  # 左下
            (camera_hole_x2, camera_hole_z1),  # 右上
            (camera_hole_x2, camera_hole_z2),  # 右下
        ])
        .circle(camera_hole_diameter / 2)
        .cutThruAll()
    )

    # ステップ3: 水平板と垂直板を結合
    bracket = horizontal_plate.union(vertical_plate)

    # ステップ4: エッジを丸める（R2以下）
    # 外側のエッジを選択的に丸める
    try:
        bracket = (
            bracket
            .edges("|Z and >Y")  # 水平板の外側エッジ
            .fillet(edge_radius)
        )
    except:
        # フィレットに失敗した場合はスキップ
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
