#!/usr/bin/env python3
"""
DXFファイルパーサー

ezdxfを使用してDXFファイルから形状情報、寸法、統計データを抽出し、
Claude Codeにフィードバック可能なテキストレポートを生成します。
"""

import ezdxf
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from collections import Counter


class DXFParser:
    """DXFファイル解析クラス"""

    def __init__(self, dxf_path: str):
        """
        Args:
            dxf_path: DXFファイルのパス
        """
        self.dxf_path = Path(dxf_path)
        self.doc = None
        self.msp = None
        self.entities = []
        self.entity_types = Counter()
        self.bbox = None

    def load(self) -> bool:
        """
        DXFファイルを読み込み

        Returns:
            bool: 成功時True
        """
        try:
            self.doc = ezdxf.readfile(str(self.dxf_path))
            self.msp = self.doc.modelspace()
            print(f"[SUCCESS] DXF loaded: {self.dxf_path}")
            return True
        except Exception as e:
            print(f"[FAILED] DXF load failed: {e}")
            return False

    def analyze(self):
        """DXFファイルを解析してエンティティ情報を抽出"""
        if not self.msp:
            print("[ERROR] DXF not loaded. Call load() first.")
            return

        # 全エンティティを取得
        self.entities = list(self.msp)

        # エンティティタイプをカウント
        for entity in self.entities:
            self.entity_types[entity.dxftype()] += 1

        # バウンディングボックスを計算
        self._calculate_bbox()

    def _calculate_bbox(self):
        """バウンディングボックスを計算"""
        try:
            extents = self.msp.extents()
            if extents is not None:
                self.bbox = {
                    "min": (extents[0].x, extents[0].y),
                    "max": (extents[1].x, extents[1].y),
                    "width": extents[1].x - extents[0].x,
                    "height": extents[1].y - extents[0].y,
                }
        except Exception as e:
            print(f"[WARNING] Bounding box calculation failed: {e}")
            self.bbox = None

    def get_lines(self) -> List[Dict]:
        """
        LINE エンティティを抽出

        Returns:
            List[Dict]: 線分情報のリスト [{start, end, length}, ...]
        """
        lines = []
        for entity in self.msp.query("LINE"):
            start = (entity.dxf.start.x, entity.dxf.start.y)
            end = (entity.dxf.end.x, entity.dxf.end.y)
            length = entity.dxf.start.distance(entity.dxf.end)
            lines.append({"start": start, "end": end, "length": length})
        return lines

    def get_circles(self) -> List[Dict]:
        """
        CIRCLE エンティティを抽出

        Returns:
            List[Dict]: 円情報のリスト [{center, radius, diameter}, ...]
        """
        circles = []
        for entity in self.msp.query("CIRCLE"):
            center = (entity.dxf.center.x, entity.dxf.center.y)
            radius = entity.dxf.radius
            circles.append({
                "center": center,
                "radius": radius,
                "diameter": radius * 2
            })
        return circles

    def get_arcs(self) -> List[Dict]:
        """
        ARC エンティティを抽出

        Returns:
            List[Dict]: 円弧情報のリスト [{center, radius, start_angle, end_angle}, ...]
        """
        arcs = []
        for entity in self.msp.query("ARC"):
            center = (entity.dxf.center.x, entity.dxf.center.y)
            radius = entity.dxf.radius
            start_angle = entity.dxf.start_angle
            end_angle = entity.dxf.end_angle
            arcs.append({
                "center": center,
                "radius": radius,
                "start_angle": start_angle,
                "end_angle": end_angle
            })
        return arcs

    def get_polylines(self) -> List[Dict]:
        """
        LWPOLYLINE エンティティを抽出

        Returns:
            List[Dict]: ポリライン情報のリスト [{points, is_closed, vertex_count}, ...]
        """
        polylines = []
        for entity in self.msp.query("LWPOLYLINE"):
            points = [(p[0], p[1]) for p in entity.get_points()]
            polylines.append({
                "points": points,
                "is_closed": entity.closed,
                "vertex_count": len(points)
            })
        return polylines

    def get_dimensions(self) -> List[Dict]:
        """
        DIMENSION エンティティを抽出

        Returns:
            List[Dict]: 寸法情報のリスト [{type, measurement, text}, ...]
        """
        dimensions = []
        for entity in self.msp.query("DIMENSION"):
            try:
                measurement = entity.get_measurement()
                dim_type = entity.dxftype()
                text = entity.dxf.text if hasattr(entity.dxf, 'text') else ""
                dimensions.append({
                    "type": dim_type,
                    "measurement": measurement,
                    "text": text
                })
            except Exception as e:
                print(f"[WARNING] Failed to extract dimension: {e}")
        return dimensions

    def generate_report(self, output_path: Optional[str] = None) -> str:
        """
        解析結果レポートを生成

        Args:
            output_path: レポート出力先パス（Noneの場合は標準出力のみ）

        Returns:
            str: レポートテキスト
        """
        lines = []
        lines.append("=" * 80)
        lines.append(f"DXF解析レポート: {self.dxf_path.name}")
        lines.append("=" * 80)
        lines.append("")

        # ファイル情報
        lines.append("## ファイル情報")
        file_size = self.dxf_path.stat().st_size / 1024
        lines.append(f"- ファイルパス: {self.dxf_path}")
        lines.append(f"- ファイルサイズ: {file_size:.1f} KB")
        lines.append(f"- DXFバージョン: {self.doc.dxfversion}")
        lines.append("")

        # エンティティ統計
        lines.append("## エンティティ統計")
        lines.append(f"- 総エンティティ数: {len(self.entities)}")
        for entity_type, count in sorted(self.entity_types.items()):
            lines.append(f"  - {entity_type}: {count}")
        lines.append("")

        # バウンディングボックス
        if self.bbox:
            lines.append("## バウンディングボックス")
            lines.append(f"- 最小座標 (X, Y): ({self.bbox['min'][0]:.2f}, {self.bbox['min'][1]:.2f})")
            lines.append(f"- 最大座標 (X, Y): ({self.bbox['max'][0]:.2f}, {self.bbox['max'][1]:.2f})")
            lines.append(f"- 幅 x 高さ: {self.bbox['width']:.2f} x {self.bbox['height']:.2f}")
            lines.append("")

        # 詳細エンティティ情報
        lines.append("## 詳細エンティティ情報")

        # 線分
        line_entities = self.get_lines()
        if line_entities:
            lines.append(f"\n### 線分（LINE）: {len(line_entities)} 個")
            for i, line in enumerate(line_entities[:5], 1):  # 最初の5つのみ表示
                lines.append(f"  {i}. 始点 {line['start']}, 終点 {line['end']}, 長さ {line['length']:.2f}")
            if len(line_entities) > 5:
                lines.append(f"  ... 他 {len(line_entities) - 5} 個")

        # 円
        circle_entities = self.get_circles()
        if circle_entities:
            lines.append(f"\n### 円（CIRCLE）: {len(circle_entities)} 個")
            for i, circle in enumerate(circle_entities[:5], 1):
                lines.append(f"  {i}. 中心 {circle['center']}, 半径 {circle['radius']:.2f}, 直径 {circle['diameter']:.2f}")
            if len(circle_entities) > 5:
                lines.append(f"  ... 他 {len(circle_entities) - 5} 個")

        # 円弧
        arc_entities = self.get_arcs()
        if arc_entities:
            lines.append(f"\n### 円弧（ARC）: {len(arc_entities)} 個")
            for i, arc in enumerate(arc_entities[:5], 1):
                lines.append(f"  {i}. 中心 {arc['center']}, 半径 {arc['radius']:.2f}, 角度 {arc['start_angle']:.1f}°-{arc['end_angle']:.1f}°")
            if len(arc_entities) > 5:
                lines.append(f"  ... 他 {len(arc_entities) - 5} 個")

        # ポリライン
        polyline_entities = self.get_polylines()
        if polyline_entities:
            lines.append(f"\n### ポリライン（LWPOLYLINE）: {len(polyline_entities)} 個")
            for i, pl in enumerate(polyline_entities[:5], 1):
                closed_str = "閉" if pl['is_closed'] else "開"
                lines.append(f"  {i}. 頂点数 {pl['vertex_count']}, 状態 {closed_str}")
            if len(polyline_entities) > 5:
                lines.append(f"  ... 他 {len(polyline_entities) - 5} 個")

        # 寸法
        dimension_entities = self.get_dimensions()
        if dimension_entities:
            lines.append(f"\n### 寸法（DIMENSION）: {len(dimension_entities)} 個")
            for i, dim in enumerate(dimension_entities[:5], 1):
                lines.append(f"  {i}. タイプ {dim['type']}, 測定値 {dim['measurement']:.2f}, テキスト '{dim['text']}'")
            if len(dimension_entities) > 5:
                lines.append(f"  ... 他 {len(dimension_entities) - 5} 個")

        lines.append("")
        lines.append("=" * 80)
        lines.append("[完了] DXF解析完了")
        lines.append("=" * 80)

        report = "\n".join(lines)

        # ファイルに保存
        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(report)
            print(f"[SUCCESS] レポート保存: {output_path}")

        return report


def parse_dxf(dxf_path: str, report_path: Optional[str] = None) -> DXFParser:
    """
    DXFファイルを解析してレポートを生成

    Args:
        dxf_path: DXFファイルのパス
        report_path: レポート出力先パス（Noneの場合は保存しない）

    Returns:
        DXFParser: 解析済みパーサーインスタンス
    """
    parser = DXFParser(dxf_path)

    if not parser.load():
        return None

    parser.analyze()
    report = parser.generate_report(report_path)
    print(report)

    return parser


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python3 dxf_parser.py <dxf_file> [output_report.txt]")
        sys.exit(1)

    dxf_file = sys.argv[1]
    report_file = sys.argv[2] if len(sys.argv) > 2 else None

    parse_dxf(dxf_file, report_file)
