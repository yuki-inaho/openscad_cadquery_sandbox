#!/usr/bin/env python3
"""
CadQuery共通ユーティリティモジュール

CadQueryモデルの保存、エクスポート、OpenSCAD連携のための再利用可能な関数。
"""

import cadquery as cq
from pathlib import Path


def export_step(model, output_path: str):
    """
    STEP形式でエクスポート（CADソフトで編集可能な高品質形式）

    Args:
        model: CadQueryモデル
        output_path: 出力ファイルパス

    Returns:
        bool: 成功時True
    """
    try:
        cq.exporters.export(model, output_path)
        file_size = Path(output_path).stat().st_size / 1024
        print(f"[SUCCESS] STEP export: {output_path} ({file_size:.1f} KB)")
        return True
    except Exception as e:
        print(f"[FAILED] STEP export failed: {e}")
        return False


def export_stl(model, output_path: str):
    """
    STL形式でエクスポート（3Dプリント用）

    Args:
        model: CadQueryモデル
        output_path: 出力ファイルパス

    Returns:
        bool: 成功時True
    """
    try:
        cq.exporters.export(model, output_path)
        file_size = Path(output_path).stat().st_size / 1024
        print(f"[SUCCESS] STL export: {output_path} ({file_size:.1f} KB)")
        return True
    except Exception as e:
        print(f"[FAILED] STL export failed: {e}")
        return False


def export_dxf(model, output_path: str, section_plane: str = "XY"):
    """
    DXF形式でエクスポート（2D断面専用）

    注意: DXFエクスポートは2D断面のみ対応。3D投影機能はありません。
    3D投影が必要な場合はexport_svg()を使用してください。

    Args:
        model: CadQueryモデル（3Dまたは2D）
        output_path: 出力ファイルパス
        section_plane: 断面平面 ("XY", "XZ", "YZ")

    Returns:
        bool: 成功時True
    """
    try:
        # 3Dソリッドがあるかチェック
        try:
            solids = model.solids().vals()
            has_solids = len(solids) > 0
        except:
            has_solids = False

        # 3Dモデルの場合は断面を取得
        if has_solids:
            # 平面に応じてモデルを回転
            if section_plane == "XY":
                section = model.section()
            elif section_plane == "XZ":
                section = model.rotate((0,0,0), (1,0,0), 90).section()
            elif section_plane == "YZ":
                section = model.rotate((0,0,0), (0,1,0), 90).section()
            else:
                section = model.section()

            cq.exporters.export(section, output_path)
            print(f"[SUCCESS] DXF export ({section_plane} section): {output_path}")
        else:
            # 2Dスケッチやワイヤーの場合はそのまま出力
            cq.exporters.export(model, output_path)
            print(f"[SUCCESS] DXF export (2D): {output_path}")

        return True
    except Exception as e:
        print(f"[WARNING] DXF export failed: {e}")
        return False


def export_svg(model, output_path: str, svg_opts: dict = None):
    """
    SVG形式でエクスポート（2D図面、ブラウザで表示可能）

    Args:
        model: CadQueryモデル
        output_path: 出力ファイルパス
        svg_opts: SVG出力オプション

    Returns:
        bool: 成功時True
    """
    if svg_opts is None:
        svg_opts = {
            "width": 300,
            "height": 300,
            "marginLeft": 10,
            "marginTop": 10,
            "showAxes": False,
            "projectionDir": (0, 0, 1),
            "strokeWidth": 0.25,
        }

    try:
        cq.exporters.export(model, output_path, opt=svg_opts)
        print(f"[SUCCESS] SVG export: {output_path}")
        return True
    except Exception as e:
        print(f"[WARNING] SVG export failed: {e}")
        return False


def export_all_formats(model, name_prefix: str, output_dir: str = "outputs/cadquery"):
    """
    モデルを各種形式で一括エクスポート

    Args:
        model: CadQueryモデル
        name_prefix: ファイル名のプレフィックス
        output_dir: 出力ディレクトリ

    Returns:
        dict: エクスポートされたファイルのパス {"format": "path"}
    """
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    results = {}

    # STEP形式
    step_path = f"{output_dir}/{name_prefix}.step"
    if export_step(model, step_path):
        results["step"] = step_path

    # STL形式
    stl_path = f"{output_dir}/{name_prefix}.stl"
    if export_stl(model, stl_path):
        results["stl"] = stl_path

    # DXF形式（オプション）
    dxf_path = f"{output_dir}/{name_prefix}_top.dxf"
    if export_dxf(model, dxf_path):
        results["dxf"] = dxf_path

    # SVG形式（オプション）
    svg_path = f"{output_dir}/{name_prefix}_top.svg"
    if export_svg(model, svg_path):
        results["svg"] = svg_path

    return results


def convert_to_openscad(model, output_scad_path: str, output_dir: str = None):
    """
    CadQueryモデルをSTL経由でOpenSCADで使用可能にする

    Args:
        model: CadQueryモデル
        output_scad_path: 出力するSCADファイルのパス
        output_dir: STLファイルの出力ディレクトリ（Noneの場合はSCADと同じ）

    Returns:
        tuple: (scad_path, stl_path)
    """
    scad_path = Path(output_scad_path)

    if output_dir is None:
        output_dir = scad_path.parent

    # STLファイルを生成
    stl_filename = scad_path.stem + ".stl"
    stl_path = Path(output_dir) / stl_filename

    export_stl(model, str(stl_path))

    # STLをインポートするOpenSCADコードを生成
    scad_code = f"""// CadQueryから生成されたモデル
// STLファイルをインポート

import("{stl_filename}");
"""

    with open(scad_path, 'w') as f:
        f.write(scad_code)

    print(f"[SUCCESS] OpenSCAD file created: {scad_path}")

    return str(scad_path), str(stl_path)


def create_2d_projections(stl_path: str, output_dir: str = None):
    """
    STLファイルから2D投影用のSCADファイルを生成

    Args:
        stl_path: STLファイルのパス
        output_dir: 出力ディレクトリ（Noneの場合はSTLと同じ）

    Returns:
        dict: {"view_name": "scad_file_path"}
    """
    stl_path = Path(stl_path)

    if output_dir is None:
        output_dir = stl_path.parent
    else:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

    stl_filename = stl_path.name
    base_name = stl_path.stem

    projections = {}

    # トップビュー（上面図）
    top_view_code = f"""// {base_name} - トップビュー (2D投影)

module model_3d() {{
    import("{stl_filename}");
}}

// トップビュー (上から見た図)
projection(cut=false) {{
    model_3d();
}}
"""
    top_path = output_dir / f"{base_name}_2d_top.scad"
    with open(top_path, 'w') as f:
        f.write(top_view_code)
    projections["top"] = str(top_path)

    # フロントビュー（正面図）
    front_view_code = f"""// {base_name} - フロントビュー (2D投影)

module model_3d() {{
    import("{stl_filename}");
}}

// フロントビュー (正面から見た図)
projection(cut=false) {{
    rotate([90, 0, 0]) model_3d();
}}
"""
    front_path = output_dir / f"{base_name}_2d_front.scad"
    with open(front_path, 'w') as f:
        f.write(front_view_code)
    projections["front"] = str(front_path)

    # サイドビュー（側面図）
    side_view_code = f"""// {base_name} - サイドビュー (2D投影)

module model_3d() {{
    import("{stl_filename}");
}}

// サイドビュー (側面から見た図)
projection(cut=false) {{
    rotate([90, 0, 90]) model_3d();
}}
"""
    side_path = output_dir / f"{base_name}_2d_side.scad"
    with open(side_path, 'w') as f:
        f.write(side_view_code)
    projections["side"] = str(side_path)

    print(f"[SUCCESS] Created 2D projection files: {len(projections)}")

    return projections


def save_model_with_openscad_support(
    model,
    name_prefix: str,
    output_dir: str = "outputs/cadquery",
    create_projections: bool = True
):
    """
    モデルをSTEP/STL形式で保存し、OpenSCAD連携ファイルも生成

    Args:
        model: CadQueryモデル
        name_prefix: ファイル名のプレフィックス
        output_dir: 出力ディレクトリ
        create_projections: 2D投影ファイルも作成するか

    Returns:
        dict: 生成されたファイルのパス
    """
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    results = {}

    # STEP/STL形式で保存
    print(f"\n=== Exporting {name_prefix} ===")

    step_path = f"{output_dir}/{name_prefix}.step"
    if export_step(model, step_path):
        results["step"] = step_path

    stl_path = f"{output_dir}/{name_prefix}.stl"
    if export_stl(model, stl_path):
        results["stl"] = stl_path

    # OpenSCAD用ファイル生成
    scad_path = f"{output_dir}/{name_prefix}.scad"
    scad_file, stl_file = convert_to_openscad(model, scad_path, output_dir)
    results["scad"] = scad_file

    # 2D投影ファイル生成
    if create_projections:
        projections = create_2d_projections(stl_path, output_dir)
        results["projections"] = projections

    return results
