#!/usr/bin/env python3
"""
シンプル版L字ブラケットのテスト
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from examples.cadquery.l_bracket_camera_mount import create_l_bracket_camera_mount
from scripts.cadquery_utils import export_dxf
from scripts.dxf_parser import parse_dxf


def main():
    print("="*80)
    print("シンプル版L字ブラケット テスト")
    print("="*80)

    # 生成
    print("\n[1] L字ブラケット生成中...")
    bracket = create_l_bracket_camera_mount()

    # 出力
    output_dir = Path("outputs/test_simple")
    output_dir.mkdir(parents=True, exist_ok=True)

    print("\n[2] DXFエクスポート中...")
    dxf_xy = output_dir / "bracket_xy.dxf"
    dxf_xz = output_dir / "bracket_xz.dxf"

    # XY断面: Z=1mm（水平板の中央）
    # XZ断面: Y=-24mm（垂直板の中央、回転後はZ=-24mm）
    export_dxf(bracket, str(dxf_xy), "XY", 1.0)
    export_dxf(bracket, str(dxf_xz), "XZ", -24.0)

    # 解析
    print("\n" + "="*80)
    print("【テスト1】XY断面: 三脚穴検出")
    print("="*80)
    parser_xy = parse_dxf(str(dxf_xy), str(output_dir / "report_xy.txt"))
    circles_xy = parser_xy.get_circles() if parser_xy else []

    print(f"\n検出された円: {len(circles_xy)} 個（期待値: 1個）")
    test1_pass = False
    if circles_xy:
        for i, c in enumerate(circles_xy, 1):
            print(f"  円{i}: 中心=({c['center'][0]:.2f}, {c['center'][1]:.2f}), φ{c['diameter']:.2f}mm")
        if len(circles_xy) == 1 and abs(circles_xy[0]['diameter'] - 6.5) < 0.1:
            print("\n✅ テスト1 成功")
            test1_pass = True
        else:
            print("\n⚠️  テスト1 部分成功")
    else:
        print("\n❌ テスト1 失敗")

    print("\n" + "="*80)
    print("【テスト2】XZ断面: カメラ穴検出")
    print("="*80)
    parser_xz = parse_dxf(str(dxf_xz), str(output_dir / "report_xz.txt"))
    circles_xz = parser_xz.get_circles() if parser_xz else []

    print(f"\n検出された円: {len(circles_xz)} 個（期待値: 4個）")
    test2_pass = False
    if circles_xz:
        for i, c in enumerate(circles_xz, 1):
            print(f"  円{i}: 中心=({c['center'][0]:.2f}, {c['center'][1]:.2f}), φ{c['diameter']:.2f}mm")
        if len(circles_xz) == 4 and all(abs(c['diameter'] - 3.2) < 0.1 for c in circles_xz):
            print("\n✅ テスト2 成功")
            test2_pass = True
        else:
            print(f"\n⚠️  テスト2 部分成功")
    else:
        print("\n❌ テスト2 失敗")

    # 総合結果
    print("\n" + "="*80)
    print("【総合結果】")
    print("="*80)
    print(f"  テスト1（三脚穴）: {'✅ PASS' if test1_pass else '❌ FAIL'}")
    print(f"  テスト2（カメラ穴）: {'✅ PASS' if test2_pass else '❌ FAIL'}")

    if test1_pass and test2_pass:
        print("\n" + "="*80)
        print("🎉 全テスト成功！シンプル版は正常に動作しています")
        print("="*80)
        return True
    else:
        print("\n" + "="*80)
        print("❌ 一部テスト失敗")
        print("="*80)
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
