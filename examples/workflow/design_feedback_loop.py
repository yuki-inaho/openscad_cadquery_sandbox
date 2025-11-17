#!/usr/bin/env python3
"""
設計フィードバックループのワークフロー例

CadQueryでモデル設計 → エクスポート → パース → レポート生成 → フィードバック
のサイクルを自動化し、Claude Codeが設計情報を読み取れるようにします。
"""

import sys
from pathlib import Path

# scriptsモジュールをインポート可能にする
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import cadquery as cq
from scripts.cadquery_utils import export_step, export_stl, export_dxf, export_svg
from scripts.dxf_parser import parse_dxf
from scripts.svg_parser import parse_svg


def design_simple_bracket(width=80, height=60, thickness=10, hole_diameter=8):
    """
    パラメトリックなブラケットを設計

    Args:
        width: 幅
        height: 高さ
        thickness: 厚さ
        hole_diameter: 取り付け穴の直径

    Returns:
        CadQueryモデル
    """
    print(f"\n=== ブラケット設計 ===")
    print(f"パラメータ: 幅={width}, 高さ={height}, 厚さ={thickness}, 穴径={hole_diameter}")

    bracket = (
        cq.Workplane("XY")
        .box(width, height, thickness, centered=(True, True, False))
        .faces(">Z").workplane()
        .rect(width * 0.75, height * 0.67, forConstruction=True).vertices()
        .circle(hole_diameter / 2).cutThruAll()
        .edges("|Z").fillet(2)
    )

    print(f"[SUCCESS] ブラケット設計完了")
    return bracket


def export_design(model, name_prefix: str, output_dir: str):
    """
    設計を各種形式でエクスポート

    Args:
        model: CadQueryモデル
        name_prefix: ファイル名プレフィックス
        output_dir: 出力ディレクトリ

    Returns:
        dict: エクスポートされたファイルパス
    """
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    print(f"\n=== 各種形式でエクスポート ===")

    results = {}

    # STEP形式（CADソフトで編集可能）
    step_path = f"{output_dir}/{name_prefix}.step"
    if export_step(model, step_path):
        results["step"] = step_path

    # STL形式（3Dプリント用）
    stl_path = f"{output_dir}/{name_prefix}.stl"
    if export_stl(model, stl_path):
        results["stl"] = stl_path

    # DXF形式（2D断面）- XY、XZ、YZ平面
    for plane in ["XY", "XZ", "YZ"]:
        dxf_path = f"{output_dir}/{name_prefix}_{plane.lower()}.dxf"
        if export_dxf(model, dxf_path, section_plane=plane):
            results[f"dxf_{plane.lower()}"] = dxf_path

    # SVG形式（3D投影）
    svg_path = f"{output_dir}/{name_prefix}_top.svg"
    if export_svg(model, svg_path):
        results["svg"] = svg_path

    print(f"[SUCCESS] {len(results)} ファイルをエクスポートしました")
    return results


def analyze_exports(exported_files: dict, report_dir: str):
    """
    エクスポートされたファイルを解析してレポート生成

    Args:
        exported_files: エクスポートされたファイルのパス辞書
        report_dir: レポート出力ディレクトリ

    Returns:
        dict: 生成されたレポートのパス
    """
    Path(report_dir).mkdir(parents=True, exist_ok=True)

    print(f"\n=== エクスポートファイルを解析 ===")

    reports = {}

    # DXFファイルを解析
    for key, path in exported_files.items():
        if key.startswith("dxf_"):
            plane = key.split("_")[1].upper()
            report_path = f"{report_dir}/dxf_{plane}_report.txt"
            print(f"\n--- DXF解析: {plane}平面 ---")
            parser = parse_dxf(path, report_path)
            if parser:
                reports[f"dxf_{plane}"] = report_path

    # SVGファイルを解析
    if "svg" in exported_files:
        report_path = f"{report_dir}/svg_report.txt"
        print(f"\n--- SVG解析 ---")
        parser = parse_svg(exported_files["svg"], report_path)
        if parser:
            reports["svg"] = report_path

    print(f"\n[SUCCESS] {len(reports)} 個のレポートを生成しました")
    return reports


def generate_summary_report(exported_files: dict, reports: dict, output_path: str):
    """
    統合サマリーレポートを生成

    Args:
        exported_files: エクスポートされたファイル辞書
        reports: 生成されたレポート辞書
        output_path: サマリーレポート出力先
    """
    lines = []
    lines.append("=" * 80)
    lines.append("設計フィードバックループ - 統合サマリーレポート")
    lines.append("=" * 80)
    lines.append("")

    # エクスポートファイル一覧
    lines.append("## エクスポートされたファイル")
    for key, path in sorted(exported_files.items()):
        file_size = Path(path).stat().st_size / 1024
        lines.append(f"- {key}: {path} ({file_size:.1f} KB)")
    lines.append("")

    # 解析レポート一覧
    lines.append("## 生成された解析レポート")
    for key, path in sorted(reports.items()):
        lines.append(f"- {key}: {path}")
    lines.append("")

    # レポート内容を統合
    lines.append("## 解析結果詳細")
    lines.append("")
    for key, report_path in sorted(reports.items()):
        lines.append(f"### {key.upper()} 解析結果")
        lines.append("")
        with open(report_path, 'r', encoding='utf-8') as f:
            lines.append(f.read())
        lines.append("")
        lines.append("-" * 80)
        lines.append("")

    lines.append("=" * 80)
    lines.append("[完了] 設計フィードバックループ完了")
    lines.append("=" * 80)
    lines.append("")
    lines.append("次のステップ:")
    lines.append("1. このレポートをClaude Codeで読み込み")
    lines.append("2. 設計の妥当性を確認（寸法、形状、エンティティ数）")
    lines.append("3. 必要に応じてパラメータを調整して再設計")
    lines.append("4. フィードバックループを繰り返す")
    lines.append("")

    summary = "\n".join(lines)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(summary)

    print(f"\n[SUCCESS] 統合サマリーレポート生成: {output_path}")
    return summary


def main():
    """メイン処理 - 設計からフィードバックまでの完全なワークフロー"""
    print("=" * 80)
    print("設計フィードバックループ - ワークフロー実行")
    print("=" * 80)

    # 出力ディレクトリ
    output_dir = "outputs/workflow"
    report_dir = "outputs/workflow/reports"

    # ステップ1: 設計
    bracket = design_simple_bracket(
        width=80,
        height=60,
        thickness=10,
        hole_diameter=8
    )

    # ステップ2: エクスポート
    exported_files = export_design(bracket, "feedback_bracket", output_dir)

    # ステップ3: 解析
    reports = analyze_exports(exported_files, report_dir)

    # ステップ4: 統合レポート生成
    summary_path = f"{report_dir}/SUMMARY_REPORT.txt"
    summary = generate_summary_report(exported_files, reports, summary_path)

    # サマリーを表示
    print("\n" + "=" * 80)
    print("統合サマリーレポート（抜粋）")
    print("=" * 80)
    print(summary[:2000])
    if len(summary) > 2000:
        print(f"\n... （全 {len(summary)} 文字、詳細は {summary_path} を参照）")

    print("\n" + "=" * 80)
    print("[完了] ワークフロー完了!")
    print("=" * 80)
    print(f"\nClaude Codeで以下のファイルを読み込んでフィードバックを受けてください:")
    print(f"  {summary_path}")


if __name__ == "__main__":
    main()
