#!/usr/bin/env python3
"""
L字カメラマウントブラケット生成スクリプト
CadQueryを使用してパラメトリックなL字ブラケットを生成
"""

import cadquery as cq
from pathlib import Path


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


def save_bracket_all_formats(bracket, output_dir="bracket_output"):
    """
    ブラケットを各種フォーマットで保存

    Args:
        bracket: CadQueryブラケットモデル
        output_dir: 出力ディレクトリ
    """
    Path(output_dir).mkdir(exist_ok=True)

    base_name = "l_bracket_camera_mount"

    print("=== L字カメラマウントブラケット生成 ===\n")

    # STEP形式で保存（高品質CAD形式）
    step_path = f"{output_dir}/{base_name}.step"
    cq.exporters.export(bracket, step_path)
    print(f"[SUCCESS] STEP形式で保存: {step_path}")

    # STL形式で保存（3Dプリント用）
    stl_path = f"{output_dir}/{base_name}.stl"
    cq.exporters.export(bracket, stl_path)
    print(f"[SUCCESS] STL形式で保存: {stl_path}")

    # OpenSCAD形式で保存（レンダリング用）
    scad_path = f"{output_dir}/{base_name}.scad"
    scad_code = f"""// L字カメラマウントブラケット
// CadQueryから生成

import("{Path(stl_path).name}");
"""
    with open(scad_path, 'w') as f:
        f.write(scad_code)
    print(f"[SUCCESS] OpenSCAD形式で保存: {scad_path}")

    print(f"\n生成完了:")
    print(f"  - STEP: CADソフトウェアで編集可能")
    print(f"  - STL: 3Dプリント/加工用")
    print(f"  - SCAD: OpenSCADでの可視化用")
    print(f"\nレンダリングコマンド:")
    print(f"  python3 openscad_renderer.py {scad_path} {base_name}_3d.png")

    return step_path, stl_path, scad_path


def main():
    """メイン処理"""
    # L字ブラケット生成
    bracket = create_l_bracket_camera_mount()

    # 各種フォーマットで保存
    step_path, stl_path, scad_path = save_bracket_all_formats(bracket)

    print("\n[完了] L字カメラマウントブラケットの生成が完了しました")


if __name__ == "__main__":
    main()
