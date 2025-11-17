#!/usr/bin/env python3
"""
現状確認スクリプト: L字ブラケットの形状を詳細に解析

確認項目:
- ソリッド数（1個か複数か）
- 面の数と方向
- エッジの数
- フィレットの有無
- バウンディングボックス
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import cadquery as cq
from examples.cadquery.l_bracket_camera_mount import create_l_bracket_camera_mount


def analyze_model_geometry():
    """モデルの幾何形状を詳細に解析"""

    print("=" * 80)
    print("L字ブラケット形状解析")
    print("=" * 80)
    print()

    # L字ブラケット生成
    print("[1] モデル生成中...")
    bracket = create_l_bracket_camera_mount()
    print()

    # ソリッド数を確認
    print("=" * 80)
    print("【基本情報】")
    print("=" * 80)

    try:
        solids = bracket.solids().vals()
        print(f"ソリッド数: {len(solids)} 個")
        if len(solids) == 1:
            print("  ✅ 一体構造（L字として正しい）")
        else:
            print(f"  ⚠️  複数のソリッド（T字の可能性）")
    except Exception as e:
        print(f"  ❌ エラー: {e}")

    print()

    # バウンディングボックス
    print("=" * 80)
    print("【バウンディングボックス】")
    print("=" * 80)

    try:
        bb = bracket.val().BoundingBox()
        print(f"X方向: {bb.xmin:.2f} 〜 {bb.xmax:.2f} mm (幅: {bb.xmax - bb.xmin:.2f} mm)")
        print(f"Y方向: {bb.ymin:.2f} 〜 {bb.ymax:.2f} mm (奥行: {bb.ymax - bb.ymin:.2f} mm)")
        print(f"Z方向: {bb.zmin:.2f} 〜 {bb.zmax:.2f} mm (高さ: {bb.zmax - bb.zmin:.2f} mm)")
        print()

        # 期待値との比較
        print("期待値との比較:")
        width_expected = 80.0
        depth_expected = 50.0
        height_expected = 42.0  # 水平板2mm + 垂直板40mm

        width_actual = bb.xmax - bb.xmin
        depth_actual = bb.ymax - bb.ymin
        height_actual = bb.zmax - bb.zmin

        print(f"  幅: {width_actual:.2f} mm (期待: {width_expected} mm) {'✅' if abs(width_actual - width_expected) < 1 else '❌'}")
        print(f"  奥行: {depth_actual:.2f} mm (期待: {depth_expected} mm) {'✅' if abs(depth_actual - depth_expected) < 1 else '❌'}")
        print(f"  高さ: {height_actual:.2f} mm (期待: {height_expected} mm) {'✅' if abs(height_actual - height_expected) < 1 else '❌'}")

    except Exception as e:
        print(f"  ❌ エラー: {e}")

    print()

    # 面の解析
    print("=" * 80)
    print("【面の解析】")
    print("=" * 80)

    try:
        # 全ての面を取得
        all_faces = bracket.faces().vals()
        print(f"総面数: {len(all_faces)} 個")
        print()

        # 方向別の面をカウント
        directions = [">X", "<X", ">Y", "<Y", ">Z", "<Z"]
        for direction in directions:
            faces = bracket.faces(direction).vals()
            print(f"  {direction}方向の面: {len(faces)} 個")

    except Exception as e:
        print(f"  ❌ エラー: {e}")

    print()

    # エッジの解析（フィレット検出）
    print("=" * 80)
    print("【エッジ解析（フィレット検出）】")
    print("=" * 80)

    try:
        all_edges = bracket.edges().vals()
        print(f"総エッジ数: {len(all_edges)} 個")
        print()

        # エッジの種類をカウント
        straight_edges = 0
        curved_edges = 0

        for edge in all_edges:
            try:
                # エッジが直線か曲線かを判定
                if hasattr(edge, 'geomType'):
                    geom_type = edge.geomType()
                    if geom_type == 'LINE':
                        straight_edges += 1
                    else:
                        curved_edges += 1
                else:
                    # 別の方法で判定
                    if edge.Length() > 0:
                        try:
                            # 曲線の場合はradiusが取得できる
                            radius = edge.radius()
                            curved_edges += 1
                        except:
                            straight_edges += 1
            except:
                pass

        print(f"  直線エッジ: {straight_edges} 個")
        print(f"  曲線エッジ: {curved_edges} 個")

        if curved_edges > 0:
            print(f"  ✅ フィレットあり（曲線エッジが {curved_edges} 個検出）")
        else:
            print(f"  ⚠️  フィレットなし（すべて直線エッジ）")

    except Exception as e:
        print(f"  ❌ エラー: {e}")

    print()

    # L字形状の確認
    print("=" * 80)
    print("【L字形状の確認】")
    print("=" * 80)

    try:
        # Y方向の最小値と最大値の面を取得
        y_min_faces = bracket.faces("<Y").vals()
        y_max_faces = bracket.faces(">Y").vals()

        print(f"Y最小面（背面）: {len(y_min_faces)} 個")
        print(f"Y最大面（前面）: {len(y_max_faces)} 個")

        # Z方向の面を取得
        z_max_faces = bracket.faces(">Z").vals()
        z_min_faces = bracket.faces("<Z").vals()

        print(f"Z最大面（上面）: {len(z_max_faces)} 個")
        print(f"Z最小面（下面）: {len(z_min_faces)} 個")
        print()

        # L字の判定基準
        # - Y最小面が1個（垂直板の背面）
        # - Z最大面が1個（水平板の上面）
        # - 一体構造

        is_l_shape = (len(y_min_faces) == 1 and len(z_max_faces) == 1 and len(solids) == 1)

        if is_l_shape:
            print("  ✅ L字形状として正しい")
        else:
            print("  ⚠️  L字形状ではない可能性")
            print(f"     - 一体構造: {'✅' if len(solids) == 1 else '❌'}")
            print(f"     - Y最小面が1個: {'✅' if len(y_min_faces) == 1 else '❌'}")
            print(f"     - Z最大面が1個: {'✅' if len(z_max_faces) == 1 else '❌'}")

    except Exception as e:
        print(f"  ❌ エラー: {e}")

    print()

    # ワイヤー（穴）の検出
    print("=" * 80)
    print("【穴の検出】")
    print("=" * 80)

    try:
        wires = bracket.wires().vals()
        print(f"ワイヤー数: {len(wires)} 個")

        # 円形のワイヤーを探す
        circular_wires = 0
        for wire in wires:
            try:
                edges = wire.Edges()
                if len(edges) == 1:
                    edge = edges[0]
                    if hasattr(edge, 'geomType') and edge.geomType() == 'CIRCLE':
                        circular_wires += 1
                        # 半径を取得
                        try:
                            radius = edge.radius()
                            diameter = radius * 2
                            print(f"  円形穴: φ{diameter:.2f} mm")
                        except:
                            print(f"  円形穴: 半径取得失敗")
            except:
                pass

        print()
        print(f"検出された円形穴: {circular_wires} 個 (期待: 5個 = 三脚穴1 + カメラ穴4)")

    except Exception as e:
        print(f"  ❌ エラー: {e}")

    print()

    # STEP保存（確認用）
    print("=" * 80)
    print("【確認用ファイル保存】")
    print("=" * 80)

    output_dir = Path("outputs/verify_shape")
    output_dir.mkdir(parents=True, exist_ok=True)

    step_path = output_dir / "current_shape.step"
    cq.exporters.export(bracket, str(step_path))
    print(f"STEP: {step_path}")

    # SVGも保存（視覚確認用）
    svg_views = [
        ("top", (0, 0, 1)),
        ("front", (0, 1, 0)),
        ("side", (1, 0, 0)),
    ]

    for view_name, proj_dir in svg_views:
        svg_path = output_dir / f"current_shape_{view_name}.svg"
        svg_opts = {
            "width": 400,
            "height": 400,
            "marginLeft": 20,
            "marginTop": 20,
            "showAxes": True,
            "projectionDir": proj_dir,
            "strokeWidth": 0.5,
        }
        cq.exporters.export(bracket, str(svg_path), opt=svg_opts)
        print(f"SVG ({view_name}): {svg_path}")

    print()
    print("=" * 80)
    print("解析完了")
    print("=" * 80)


if __name__ == "__main__":
    analyze_model_geometry()
