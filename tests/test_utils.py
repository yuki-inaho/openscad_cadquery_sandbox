#!/usr/bin/env python3
"""
テスト共通ユーティリティ
TDDトイプロブレム用の再利用可能な検証関数
"""

import sys
from pathlib import Path
from typing import Optional, List, Tuple

# プロジェクトルートをパスに追加
sys.path.insert(0, str(Path(__file__).parent.parent))

import cadquery as cq
from scripts.dxf_parser import parse_dxf


def export_and_verify_dxf(
    model,
    test_name: str,
    section_plane: str,
    section_height: float,
    expected_circles: int,
    expected_diameter: Optional[float] = None,
    tolerance: float = 0.1
) -> Tuple[bool, str]:
    """
    DXFエクスポートして穴を検証

    Args:
        model: CadQueryモデル
        test_name: テスト名（出力ファイル名に使用）
        section_plane: "XY" or "XZ"
        section_height: 断面の高さ
        expected_circles: 期待される円の数
        expected_diameter: 期待される直径（Noneなら検証しない）
        tolerance: 許容誤差

    Returns:
        Tuple[bool, str]: (テストが成功したか, メッセージ)
    """
    output_dir = Path(f"outputs/tests/{test_name}")
    output_dir.mkdir(parents=True, exist_ok=True)

    dxf_filename = f"{section_plane.lower()}_h{section_height:.1f}.dxf"
    dxf_path = output_dir / dxf_filename

    try:
        # DXFエクスポート（translate()アプローチを使用）
        from scripts.cadquery_utils import export_dxf

        success = export_dxf(model, str(dxf_path), section_plane, section_height)
        if not success:
            return False, "DXF export failed"

        # DXF解析
        parser = parse_dxf(str(dxf_path))
        if not parser:
            return False, "DXF parse failed"

        circles = parser.get_circles()

        # 円の数を検証
        if len(circles) != expected_circles:
            return False, f"Expected {expected_circles} circles, got {len(circles)}"

        # 直径を検証（指定されている場合）
        if expected_diameter is not None:
            for i, circle in enumerate(circles):
                diameter = circle['diameter']
                if abs(diameter - expected_diameter) > tolerance:
                    return False, f"Circle {i+1}: Expected φ{expected_diameter}mm, got φ{diameter:.2f}mm"

        return True, f"✅ PASS: {len(circles)} circles detected, φ{circles[0]['diameter']:.2f}mm"

    except Exception as e:
        return False, f"Exception: {str(e)}"


def print_test_result(test_name: str, success: bool, message: str):
    """テスト結果を整形して表示"""
    print("=" * 80)
    print(f"【{test_name}】")
    print("=" * 80)
    if success:
        print(f"✅ PASS: {message}")
    else:
        print(f"❌ FAIL: {message}")
    print()


def export_step_for_visual_check(model, test_name: str) -> str:
    """目視確認用にSTEPファイルをエクスポート"""
    output_dir = Path(f"outputs/tests/{test_name}")
    output_dir.mkdir(parents=True, exist_ok=True)

    step_path = output_dir / f"{test_name}.step"
    cq.exporters.export(model, str(step_path))

    return str(step_path)


def print_dxf_stats(
    model,
    test_name: str,
    section_plane: str,
    section_height: float
):
    """DXF統計情報を表示（デバッグ用）"""
    output_dir = Path(f"outputs/tests/{test_name}")
    output_dir.mkdir(parents=True, exist_ok=True)

    dxf_filename = f"{section_plane.lower()}_h{section_height:.1f}.dxf"
    dxf_path = output_dir / dxf_filename

    # DXFエクスポート
    if section_plane == "XY":
        section = model.section(height=section_height)
    elif section_plane == "XZ":
        section = model.rotate((0, 0, 0), (1, 0, 0), 90).section(height=section_height)

    cq.exporters.export(section, str(dxf_path))

    # DXF解析
    parser = parse_dxf(str(dxf_path))
    if parser:
        circles = parser.get_circles()
        arcs = parser.get_arcs()
        lines = parser.get_lines()

        print(f"  {section_plane} section (height={section_height}):")
        print(f"    CIRCLE: {len(circles)}個")
        print(f"    ARC: {len(arcs)}個")
        print(f"    LINE: {len(lines)}個")

        if circles:
            for i, c in enumerate(circles, 1):
                print(f"      Circle {i}: φ{c['diameter']:.2f}mm at ({c['center'][0]:.1f}, {c['center'][1]:.1f})")
