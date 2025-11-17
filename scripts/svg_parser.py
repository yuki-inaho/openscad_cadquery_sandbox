#!/usr/bin/env python3
"""
SVGファイルパーサー

xml.etree.ElementTreeを使用してSVGファイルから形状情報、投影データ、統計を抽出し、
Claude Codeにフィードバック可能なテキストレポートを生成します。
"""

import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from collections import Counter
import re


class SVGParser:
    """SVGファイル解析クラス"""

    # SVG名前空間
    NS = {'svg': 'http://www.w3.org/2000/svg'}

    def __init__(self, svg_path: str):
        """
        Args:
            svg_path: SVGファイルのパス
        """
        self.svg_path = Path(svg_path)
        self.tree = None
        self.root = None
        self.element_types = Counter()
        self.viewbox = None
        self.width = None
        self.height = None

    def load(self) -> bool:
        """
        SVGファイルを読み込み

        Returns:
            bool: 成功時True
        """
        try:
            self.tree = ET.parse(str(self.svg_path))
            self.root = self.tree.getroot()
            print(f"[SUCCESS] SVG loaded: {self.svg_path}")
            return True
        except Exception as e:
            print(f"[FAILED] SVG load failed: {e}")
            return False

    def analyze(self):
        """SVGファイルを解析して要素情報を抽出"""
        if self.root is None:
            print("[ERROR] SVG not loaded. Call load() first.")
            return

        # viewBox属性を取得
        self._parse_viewbox()

        # 幅と高さを取得
        self._parse_dimensions()

        # 全要素をカウント
        self._count_elements()

    def _parse_viewbox(self):
        """viewBox属性を解析"""
        viewbox_str = self.root.get('viewBox')
        if viewbox_str:
            try:
                values = [float(v) for v in viewbox_str.split()]
                if len(values) == 4:
                    self.viewbox = {
                        "min_x": values[0],
                        "min_y": values[1],
                        "width": values[2],
                        "height": values[3]
                    }
            except Exception as e:
                print(f"[WARNING] Failed to parse viewBox: {e}")

    def _parse_dimensions(self):
        """幅と高さ属性を解析"""
        width_str = self.root.get('width', '')
        height_str = self.root.get('height', '')

        # 数値のみを抽出（単位を除去）
        width_match = re.match(r'([\d.]+)', width_str)
        height_match = re.match(r'([\d.]+)', height_str)

        if width_match:
            self.width = float(width_match.group(1))
        if height_match:
            self.height = float(height_match.group(1))

    def _count_elements(self):
        """全要素をタイプ別にカウント"""
        for elem in self.root.iter():
            # 名前空間を除去してタグ名を取得
            tag = elem.tag.split('}')[-1] if '}' in elem.tag else elem.tag
            self.element_types[tag] += 1

    def get_paths(self) -> List[Dict]:
        """
        path要素を抽出

        Returns:
            List[Dict]: path情報のリスト [{d, id, class}, ...]
        """
        paths = []
        for path in self.root.findall('.//svg:path', self.NS):
            d = path.get('d', '')
            path_id = path.get('id', '')
            path_class = path.get('class', '')
            paths.append({
                "d": d,
                "id": path_id,
                "class": path_class,
                "command_count": len(re.findall(r'[MLHVCSQTAZ]', d, re.IGNORECASE))
            })

        # 名前空間なしでも検索（互換性のため）
        if not paths:
            for path in self.root.findall('.//path'):
                d = path.get('d', '')
                path_id = path.get('id', '')
                path_class = path.get('class', '')
                paths.append({
                    "d": d,
                    "id": path_id,
                    "class": path_class,
                    "command_count": len(re.findall(r'[MLHVCSQTAZ]', d, re.IGNORECASE))
                })

        return paths

    def get_circles(self) -> List[Dict]:
        """
        circle要素を抽出

        Returns:
            List[Dict]: 円情報のリスト [{cx, cy, r}, ...]
        """
        circles = []
        for circle in self.root.findall('.//svg:circle', self.NS):
            cx = float(circle.get('cx', 0))
            cy = float(circle.get('cy', 0))
            r = float(circle.get('r', 0))
            circles.append({"cx": cx, "cy": cy, "r": r, "diameter": r * 2})

        # 名前空間なしでも検索
        if not circles:
            for circle in self.root.findall('.//circle'):
                cx = float(circle.get('cx', 0))
                cy = float(circle.get('cy', 0))
                r = float(circle.get('r', 0))
                circles.append({"cx": cx, "cy": cy, "r": r, "diameter": r * 2})

        return circles

    def get_rects(self) -> List[Dict]:
        """
        rect要素を抽出

        Returns:
            List[Dict]: 矩形情報のリスト [{x, y, width, height}, ...]
        """
        rects = []
        for rect in self.root.findall('.//svg:rect', self.NS):
            x = float(rect.get('x', 0))
            y = float(rect.get('y', 0))
            width = float(rect.get('width', 0))
            height = float(rect.get('height', 0))
            rects.append({"x": x, "y": y, "width": width, "height": height})

        # 名前空間なしでも検索
        if not rects:
            for rect in self.root.findall('.//rect'):
                x = float(rect.get('x', 0))
                y = float(rect.get('y', 0))
                width = float(rect.get('width', 0))
                height = float(rect.get('height', 0))
                rects.append({"x": x, "y": y, "width": width, "height": height})

        return rects

    def get_lines(self) -> List[Dict]:
        """
        line要素を抽出

        Returns:
            List[Dict]: 線分情報のリスト [{x1, y1, x2, y2, length}, ...]
        """
        lines = []
        for line in self.root.findall('.//svg:line', self.NS):
            x1 = float(line.get('x1', 0))
            y1 = float(line.get('y1', 0))
            x2 = float(line.get('x2', 0))
            y2 = float(line.get('y2', 0))
            length = ((x2 - x1)**2 + (y2 - y1)**2)**0.5
            lines.append({
                "x1": x1, "y1": y1, "x2": x2, "y2": y2, "length": length
            })

        # 名前空間なしでも検索
        if not lines:
            for line in self.root.findall('.//line'):
                x1 = float(line.get('x1', 0))
                y1 = float(line.get('y1', 0))
                x2 = float(line.get('x2', 0))
                y2 = float(line.get('y2', 0))
                length = ((x2 - x1)**2 + (y2 - y1)**2)**0.5
                lines.append({
                    "x1": x1, "y1": y1, "x2": x2, "y2": y2, "length": length
                })

        return lines

    def get_texts(self) -> List[Dict]:
        """
        text要素を抽出

        Returns:
            List[Dict]: テキスト情報のリスト [{text, x, y}, ...]
        """
        texts = []
        for text in self.root.findall('.//svg:text', self.NS):
            x = float(text.get('x', 0))
            y = float(text.get('y', 0))
            content = text.text or ''
            texts.append({"text": content, "x": x, "y": y})

        # 名前空間なしでも検索
        if not texts:
            for text in self.root.findall('.//text'):
                x = float(text.get('x', 0))
                y = float(text.get('y', 0))
                content = text.text or ''
                texts.append({"text": content, "x": x, "y": y})

        return texts

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
        lines.append(f"SVG解析レポート: {self.svg_path.name}")
        lines.append("=" * 80)
        lines.append("")

        # ファイル情報
        lines.append("## ファイル情報")
        file_size = self.svg_path.stat().st_size / 1024
        lines.append(f"- ファイルパス: {self.svg_path}")
        lines.append(f"- ファイルサイズ: {file_size:.1f} KB")
        if self.width and self.height:
            lines.append(f"- 幅 x 高さ: {self.width} x {self.height}")
        lines.append("")

        # viewBox情報
        if self.viewbox:
            lines.append("## viewBox情報")
            lines.append(f"- 最小座標 (X, Y): ({self.viewbox['min_x']:.2f}, {self.viewbox['min_y']:.2f})")
            lines.append(f"- 幅 x 高さ: {self.viewbox['width']:.2f} x {self.viewbox['height']:.2f}")
            lines.append("")

        # 要素統計
        lines.append("## 要素統計")
        lines.append(f"- 総要素数: {sum(self.element_types.values())}")
        for elem_type, count in sorted(self.element_types.items()):
            if count > 0:
                lines.append(f"  - {elem_type}: {count}")
        lines.append("")

        # 詳細要素情報
        lines.append("## 詳細要素情報")

        # path要素
        path_elements = self.get_paths()
        if path_elements:
            lines.append(f"\n### path要素: {len(path_elements)} 個")
            for i, path in enumerate(path_elements[:5], 1):
                id_str = f", id='{path['id']}'" if path['id'] else ""
                lines.append(f"  {i}. コマンド数 {path['command_count']}{id_str}")
            if len(path_elements) > 5:
                lines.append(f"  ... 他 {len(path_elements) - 5} 個")

        # circle要素
        circle_elements = self.get_circles()
        if circle_elements:
            lines.append(f"\n### circle要素: {len(circle_elements)} 個")
            for i, circle in enumerate(circle_elements[:5], 1):
                lines.append(f"  {i}. 中心 ({circle['cx']:.2f}, {circle['cy']:.2f}), 半径 {circle['r']:.2f}, 直径 {circle['diameter']:.2f}")
            if len(circle_elements) > 5:
                lines.append(f"  ... 他 {len(circle_elements) - 5} 個")

        # rect要素
        rect_elements = self.get_rects()
        if rect_elements:
            lines.append(f"\n### rect要素: {len(rect_elements)} 個")
            for i, rect in enumerate(rect_elements[:5], 1):
                lines.append(f"  {i}. 位置 ({rect['x']:.2f}, {rect['y']:.2f}), サイズ {rect['width']:.2f} x {rect['height']:.2f}")
            if len(rect_elements) > 5:
                lines.append(f"  ... 他 {len(rect_elements) - 5} 個")

        # line要素
        line_elements = self.get_lines()
        if line_elements:
            lines.append(f"\n### line要素: {len(line_elements)} 個")
            for i, line in enumerate(line_elements[:5], 1):
                lines.append(f"  {i}. ({line['x1']:.2f}, {line['y1']:.2f}) → ({line['x2']:.2f}, {line['y2']:.2f}), 長さ {line['length']:.2f}")
            if len(line_elements) > 5:
                lines.append(f"  ... 他 {len(line_elements) - 5} 個")

        # text要素
        text_elements = self.get_texts()
        if text_elements:
            lines.append(f"\n### text要素: {len(text_elements)} 個")
            for i, text in enumerate(text_elements[:5], 1):
                lines.append(f"  {i}. 位置 ({text['x']:.2f}, {text['y']:.2f}), テキスト '{text['text']}'")
            if len(text_elements) > 5:
                lines.append(f"  ... 他 {len(text_elements) - 5} 個")

        lines.append("")
        lines.append("=" * 80)
        lines.append("[完了] SVG解析完了")
        lines.append("=" * 80)

        report = "\n".join(lines)

        # ファイルに保存
        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(report)
            print(f"[SUCCESS] レポート保存: {output_path}")

        return report


def parse_svg(svg_path: str, report_path: Optional[str] = None) -> SVGParser:
    """
    SVGファイルを解析してレポートを生成

    Args:
        svg_path: SVGファイルのパス
        report_path: レポート出力先パス（Noneの場合は保存しない）

    Returns:
        SVGParser: 解析済みパーサーインスタンス
    """
    parser = SVGParser(svg_path)

    if not parser.load():
        return None

    parser.analyze()
    report = parser.generate_report(report_path)
    print(report)

    return parser


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python3 svg_parser.py <svg_file> [output_report.txt]")
        sys.exit(1)

    svg_file = sys.argv[1]
    report_file = sys.argv[2] if len(sys.argv) > 2 else None

    parse_svg(svg_file, report_file)
