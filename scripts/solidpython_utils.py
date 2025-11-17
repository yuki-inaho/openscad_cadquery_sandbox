#!/usr/bin/env python3
"""
SolidPython共通ユーティリティモジュール

SolidPython2モデルの保存、2D投影生成のための再利用可能な関数。
"""

from solid2 import scad_render
from pathlib import Path


def save_scad_3d(model, output_path: str):
    """
    3DモデルをSCADファイルとして保存

    Args:
        model: SolidPython2モデルオブジェクト
        output_path: 出力ファイルパス

    Returns:
        str: 保存されたファイルパス
    """
    model.save_as_scad(output_path)
    file_size = Path(output_path).stat().st_size / 1024
    print(f"[SUCCESS] 3D SCAD saved: {output_path} ({file_size:.1f} KB)")
    return output_path


def create_2d_projection_scad(model, output_path: str):
    """
    3DモデルからOpenSCAD projection()を使った2D投影版を作成

    Args:
        model: SolidPython2モデルオブジェクト
        output_path: 出力ファイルパス

    Returns:
        str: 保存されたファイルパス
    """
    # 3Dモデルのコード生成
    scad_code = scad_render(model)

    # 2D投影用のコードを追加
    projection_code = f"""// 2D投影（トップビュー）
// Original 3D model
module model_3d() {{
{scad_code}
}}

// Top view projection
projection(cut=false) model_3d();
"""

    with open(output_path, 'w') as f:
        f.write(projection_code)

    file_size = Path(output_path).stat().st_size / 1024
    print(f"[SUCCESS] 2D projection SCAD saved: {output_path} ({file_size:.1f} KB)")
    return output_path


def save_model_with_2d(model, name_prefix: str, output_dir: str = "outputs/solidpython"):
    """
    3Dモデルと2D投影版の両方を保存

    Args:
        model: SolidPython2モデルオブジェクト
        name_prefix: ファイル名のプレフィックス
        output_dir: 出力ディレクトリ

    Returns:
        dict: {"3d": "3d_path", "2d": "2d_path"}
    """
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    # 3Dモデルを保存
    scad_3d = f"{output_dir}/{name_prefix}_3d.scad"
    save_scad_3d(model, scad_3d)

    # 2D投影版を作成
    scad_2d = f"{output_dir}/{name_prefix}_2d.scad"
    create_2d_projection_scad(model, scad_2d)

    return {
        "3d": scad_3d,
        "2d": scad_2d
    }


def create_multiple_2d_projections(
    model,
    name_prefix: str,
    output_dir: str = "outputs/solidpython"
):
    """
    複数の2D投影（トップ、フロント、サイド）を生成

    Args:
        model: SolidPython2モデルオブジェクト
        name_prefix: ファイル名のプレフィックス
        output_dir: 出力ディレクトリ

    Returns:
        dict: {"top": "path", "front": "path", "side": "path"}
    """
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    scad_code = scad_render(model)
    projections = {}

    # トップビュー（上面図）
    top_code = f"""// {name_prefix} - トップビュー (2D投影)

module model_3d() {{
{scad_code}
}}

projection(cut=false) model_3d();
"""
    top_path = f"{output_dir}/{name_prefix}_2d_top.scad"
    with open(top_path, 'w') as f:
        f.write(top_code)
    projections["top"] = top_path

    # フロントビュー（正面図）
    front_code = f"""// {name_prefix} - フロントビュー (2D投影)

module model_3d() {{
{scad_code}
}}

projection(cut=false) {{
    rotate([90, 0, 0]) model_3d();
}}
"""
    front_path = f"{output_dir}/{name_prefix}_2d_front.scad"
    with open(front_path, 'w') as f:
        f.write(front_code)
    projections["front"] = front_path

    # サイドビュー（側面図）
    side_code = f"""// {name_prefix} - サイドビュー (2D投影)

module model_3d() {{
{scad_code}
}}

projection(cut=false) {{
    rotate([90, 0, 90]) model_3d();
}}
"""
    side_path = f"{output_dir}/{name_prefix}_2d_side.scad"
    with open(side_path, 'w') as f:
        f.write(side_code)
    projections["side"] = side_path

    print(f"[SUCCESS] Created {len(projections)} 2D projection files")

    return projections


def batch_save_models(models: dict, output_dir: str = "outputs/solidpython"):
    """
    複数のモデルを一括保存

    Args:
        models: {"model_name": model_object}の辞書
        output_dir: 出力ディレクトリ

    Returns:
        dict: {"model_name": {"3d": "path", "2d": "path"}}
    """
    results = {}

    for name, model in models.items():
        print(f"\n=== Saving {name} ===")
        results[name] = save_model_with_2d(model, name, output_dir)

    print(f"\n[SUCCESS] Batch saved {len(models)} models")

    return results
