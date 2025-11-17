# OpenSCAD Headless Renderer with SolidPython & CadQuery

パラメトリック3Dモデリングとheadlessレンダリングのための統合環境。OpenSCAD、SolidPython、CadQueryをサポート。

## ディレクトリ構造

```
.
├── scripts/                    # 再利用可能な共通モジュール
│   ├── renderer.py            # OpenSCADレンダリング機能
│   ├── cadquery_utils.py      # CadQuery共通ユーティリティ
│   └── solidpython_utils.py   # SolidPython共通ユーティリティ
├── examples/                   # サンプルスクリプト
│   ├── openscad/              # OpenSCAD例
│   │   ├── test.scad
│   │   └── example_advanced.py
│   ├── solidpython/           # SolidPython例
│   │   ├── solidpython_simple.py
│   │   └── solidpython_example.py
│   └── cadquery/              # CadQuery例
│       ├── cadquery_examples.py
│       └── l_bracket_camera_mount.py
├── outputs/                    # 生成ファイル出力先
│   ├── openscad/
│   ├── solidpython/
│   ├── cadquery/
│   └── l_bracket/
├── tools/                      # ツールスクリプト
│   └── render_headless.sh
└── docs/                       # ドキュメント
    └── workdoc_nov17_2025_openscad_setup.md
```

## インストール済みパッケージ

- `openscad` (2021.01): 3Dモデリングソフトウェア
- `xvfb`: 仮想フレームバッファ（headless実行に必要）
- `xauth`: X認証ユーティリティ
- `mesa-utils`: OpenGLユーティリティ
- `libgl1-mesa-dri`: Mesa DRIドライバ
- `solidpython2`: OpenSCAD用Pythonライブラリ
- `cadquery`: OCCT使用のパラメトリックCADライブラリ

## クイックスタート

### 1. OpenSCADレンダリング

```bash
# Pythonレンダラーを使用
python3 scripts/renderer.py examples/openscad/test.scad output.png

# オプション指定
python3 scripts/renderer.py examples/openscad/test.scad output.png \
    --imgsize 1920 1080 \
    --colorscheme Tomorrow \
    --projection p

# Bashスクリプトを使用
tools/render_headless.sh examples/openscad/test.scad output.png
```

### 2. CadQueryで3Dモデル生成

```bash
# サンプルモデル生成（STEP/STL/SCAD形式）
python3 examples/cadquery/cadquery_examples.py

# L字ブラケット生成
python3 examples/cadquery/l_bracket_camera_mount.py

# レンダリング
python3 scripts/renderer.py outputs/cadquery/cq_bracket.scad bracket.png
```

### 3. SolidPythonで3Dモデル生成

```bash
# サンプルモデル生成（3D/2D版のSCADファイル）
python3 examples/solidpython/solidpython_simple.py

# 3Dレンダリング
python3 scripts/renderer.py outputs/solidpython/mech_part_3d.scad mech_3d.png

# 2D図面
python3 scripts/renderer.py outputs/solidpython/mech_part_2d.scad mech_2d.png --projection o
```

## 共通モジュールの使用方法

### scripts/renderer.py

OpenSCADのheadlessレンダリング機能を提供:

```python
from scripts.renderer import OpenSCADRenderer

with OpenSCADRenderer(display=99) as renderer:
    renderer.render(
        scad_file="model.scad",
        output_file="output.png",
        imgsize=(1920, 1080),
        colorscheme="Tomorrow",
        projection="p"  # "p"=透視投影, "o"=平行投影
    )
```

### scripts/cadquery_utils.py

CadQuery モデルの保存と変換:

```python
from scripts.cadquery_utils import save_model_with_openscad_support
import cadquery as cq

# モデル作成
model = cq.Workplane("XY").box(10, 10, 10)

# STEP/STL/SCAD形式で保存 + 2D投影ファイル生成
save_model_with_openscad_support(
    model,
    "my_model",
    output_dir="outputs/cadquery",
    create_projections=True
)
```

### scripts/solidpython_utils.py

SolidPythonモデルの保存と2D投影:

```python
from scripts.solidpython_utils import batch_save_models
from solid2 import cube

models = {
    "box": cube([10, 10, 10]),
    "sphere": sphere(r=5)
}

# 一括保存（3D/2D版のSCADファイル）
batch_save_models(models, output_dir="outputs/solidpython")
```

### scripts/dxf_parser.py / svg_parser.py

DXF/SVGファイルをパースして設計情報を抽出:

```python
from scripts.dxf_parser import parse_dxf
from scripts.svg_parser import parse_svg

# DXFファイル解析
dxf_parser = parse_dxf("outputs/model_xy.dxf", "dxf_report.txt")
# エンティティ情報（LINE, CIRCLE, ARC等）を抽出
circles = dxf_parser.get_circles()
lines = dxf_parser.get_lines()

# SVGファイル解析
svg_parser = parse_svg("outputs/model_top.svg", "svg_report.txt")
# 要素情報（path, circle, rect等）を抽出
paths = svg_parser.get_paths()
```

## 設計フィードバックループワークフロー

DXF/SVGパーサーを使用して、設計→エクスポート→解析→フィードバックのループを自動化:

```bash
# ワークフロー実行
python3 examples/workflow/design_feedback_loop.py

# 統合レポートが生成される
# outputs/workflow/reports/SUMMARY_REPORT.txt
```

ワークフローの流れ:
1. CadQueryでパラメトリックモデル設計
2. STEP/STL/DXF（3断面）/SVG形式でエクスポート
3. DXF/SVGをパースして詳細情報を抽出
4. テキストレポート生成（Claude Codeで読み取り可能）
5. レポートを基に設計を検証・改善

生成されるレポート内容:
- エンティティ統計（LINE、CIRCLE、ARC等の数）
- 寸法情報（座標、長さ、半径、角度）
- バウンディングボックス
- ファイルサイズとバージョン

## コマンドラインオプション

`scripts/renderer.py`のオプション:

- `--imgsize WIDTH HEIGHT`: 画像サイズ（デフォルト: 1920 1080）
- `--colorscheme SCHEME`: カラースキーム（Tomorrow, Cornfield, Metallic等）
- `--projection {p|o}`: 投影タイプ（p=透視投影, o=平行投影）
- `--preview`: プレビューモード（高速、低品質）
- `--display NUM`: Xvfbディスプレイ番号（デフォルト: 99）

## サンプル

### 簡単なCadQueryモデル

```python
import cadquery as cq
from scripts.cadquery_utils import save_model_with_openscad_support

bracket = (
    cq.Workplane("XY")
    .box(80, 60, 10)
    .faces(">Z").workplane()
    .rect(60, 40, forConstruction=True).vertices()
    .circle(3).cutThruAll()
)

save_model_with_openscad_support(bracket, "bracket", "outputs/cadquery")
```

### 簡単なSolidPythonモデル

```python
from solid2 import cube, cylinder, translate
from scripts.solidpython_utils import save_model_with_2d

base = cube([50, 50, 10], center=True)
hole = translate([0, 0, 0])(cylinder(h=12, r=5, center=True))
part = base - hole

save_model_with_2d(part, "simple_part", "outputs/solidpython")
```

### DXF断面エクスポート

```python
import cadquery as cq
from scripts.cadquery_utils import export_dxf

# 3Dモデル作成
model = cq.Workplane("XY").box(80, 60, 10)

# 各断面をDXFエクスポート
export_dxf(model, "outputs/top_view.dxf", section_plane="XY")    # トップビュー
export_dxf(model, "outputs/front_view.dxf", section_plane="XZ")  # フロントビュー
export_dxf(model, "outputs/side_view.dxf", section_plane="YZ")   # サイドビュー
```

### L字ブラケット完全ワークフロー

L字カメラマウントブラケットの生成から解析までの完全なワークフロー:

```bash
# 1. L字ブラケット生成（STEP/STL/SCAD+2D投影）
uv run python3 examples/cadquery/l_bracket_camera_mount.py

# 2. 3D画像レンダリング
uv run python3 scripts/renderer.py \
  outputs/l_bracket/l_bracket_camera_mount.scad \
  outputs/l_bracket/l_bracket_camera_mount_3d.png \
  --imgsize 1920 1080 --colorscheme Tomorrow

# 3. 2D投影画像レンダリング（トップビュー）
uv run python3 scripts/renderer.py \
  outputs/l_bracket/l_bracket_camera_mount_2d_top.scad \
  outputs/l_bracket/l_bracket_camera_mount_2d_top.png \
  --imgsize 1920 1080 --colorscheme Tomorrow

# 4. 2D投影画像レンダリング（フロントビュー）
uv run python3 scripts/renderer.py \
  outputs/l_bracket/l_bracket_camera_mount_2d_front.scad \
  outputs/l_bracket/l_bracket_camera_mount_2d_front.png \
  --imgsize 1920 1080 --colorscheme Tomorrow

# 5. 2D投影画像レンダリング（サイドビュー）
uv run python3 scripts/renderer.py \
  outputs/l_bracket/l_bracket_camera_mount_2d_side.scad \
  outputs/l_bracket/l_bracket_camera_mount_2d_side.png \
  --imgsize 1920 1080 --colorscheme Tomorrow
```

生成されるファイル:
- `l_bracket_camera_mount.step` (40KB) - STEP形式（CAD編集可能）
- `l_bracket_camera_mount.stl` (14KB) - STL形式（3Dプリント用）
- `l_bracket_camera_mount.scad` - OpenSCADファイル
- `l_bracket_camera_mount_2d_*.scad` - 2D投影用SCADファイル（3種）
- `l_bracket_camera_mount_*.png` - レンダリング画像（4種）

## 参考リンク

- [OpenSCAD公式サイト](https://openscad.org/)
- [OpenSCADチートシート](https://openscad.org/cheatsheet/)
- [SolidPython2 GitHub](https://github.com/jeff-dh/SolidPython)
- [CadQueryドキュメント](https://cadquery.readthedocs.io/)
- [CadQuery GitHub](https://github.com/CadQuery/cadquery)
