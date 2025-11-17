# TDD作業計画: L字ブラケット穴問題の解決

## 目的
L字ブラケットの穴がDXFで検出できない問題を、TDD方式で段階的に解決する。
t-wadaスタイルのTDDに従い、トイプロブレムを作成して1つずつ検証する。

## 現状の問題
- union後に穴を開けるコードは実装済み
- しかし、DXFエクスポートで穴が検出できない（CIRCLE: 0個）
- section()の高さ指定が適切でない可能性

## TDDサイクル: Red → Green → Refactor

### トイプロブレム1: 単純な箱に穴を開けてDXFで検出
**目的**: 基本的な穴開け→DXFエクスポート→検出が動作するか確認

**テストコード**: `tests/toy_01_simple_box_with_hole.py`

**期待結果**:
- XY断面（Z=5mm）: CIRCLE 1個、φ6mm
- 中心: (0, 0)

**実装内容**:
```python
def create_simple_box():
    """10x10x10mmの箱の中央に直径6mmの穴"""
    box = (
        cq.Workplane("XY")
        .box(10, 10, 10, centered=(True, True, False))
        .faces(">Z")
        .workplane()
        .circle(3)  # 半径3mm = 直径6mm
        .cutThruAll()
    )
    return box
```

**検証ポイント**:
- [ ] DXFエクスポートが成功するか
- [ ] section(height=5)で穴が見えるか
- [ ] DXFパーサーでCIRCLE 1個検出できるか

**実行コマンド**: `uv run python tests/toy_01_simple_box_with_hole.py`

---

### トイプロブレム2: 2つの箱をunionしてDXF出力確認
**目的**: union操作がDXF出力に影響するか確認

**テストコード**: `tests/toy_02_union_two_boxes.py`

**期待結果**:
- XY断面（Z=5mm）: 2つの箱の断面が見える
- L字形状のアウトラインが検出される

**実装内容**:
```python
def create_two_boxes():
    """2つの箱をunion（穴なし）"""
    box1 = cq.Workplane("XY").box(10, 10, 10, centered=(True, True, False))
    box2 = (
        cq.Workplane("XY")
        .box(10, 10, 10, centered=(True, True, False))
        .translate((10, 0, 0))
    )
    combined = box1.union(box2)
    return combined
```

**検証ポイント**:
- [ ] union後のDXFエクスポートが成功するか
- [ ] section(height=5)でアウトラインが正しく出力されるか
- [ ] LINE数が期待通りか

**実行コマンド**: `uv run python tests/toy_02_union_two_boxes.py`

---

### トイプロブレム3: union後に穴を開けてDXFで検出
**目的**: union後の穴開けがDXFで検出できるか確認（最重要）

**テストコード**: `tests/toy_03_union_then_hole.py`

**期待結果**:
- XY断面（Z=5mm）: CIRCLE 1個、φ6mm
- 中心: (0, 0)

**実装内容**:
```python
def create_union_then_hole():
    """2つの箱をunion後、中央に穴を開ける"""
    box1 = cq.Workplane("XY").box(10, 10, 10, centered=(True, True, False))
    box2 = (
        cq.Workplane("XY")
        .box(10, 10, 10, centered=(True, True, False))
        .translate((10, 0, 0))
    )
    # union
    combined = box1.union(box2)

    # union後に穴を開ける
    result = (
        combined
        .faces(">Z")
        .workplane()
        .circle(3)  # 半径3mm = 直径6mm
        .cutThruAll()
    )
    return result
```

**検証ポイント**:
- [ ] union後に穴を開けられるか
- [ ] section(height=5)で穴が見えるか
- [ ] DXFパーサーでCIRCLE 1個検出できるか

**実行コマンド**: `uv run python tests/toy_03_union_then_hole.py`

---

### トイプロブレム4: L字（フィレットなし）でDXF穴検出
**目的**: 実際のL字形状で穴が検出できるか確認

**テストコード**: `tests/toy_04_l_shape_no_fillet.py`

**期待結果**:
- XY断面（Z=1mm）: CIRCLE 1個、φ6.5mm（三脚穴）
- XZ断面（適切な高さ）: CIRCLE 4個、φ3.2mm（カメラ穴）

**実装内容**:
```python
def create_l_shape_no_fillet():
    """L字ブラケット（フィレットなし）"""
    # 水平板（穴なし）
    h_plate = cq.Workplane("XY").box(80, 50, 2, centered=(True, True, False))

    # 垂直板（穴なし）
    v_plate = (
        cq.Workplane("XY")
        .box(80, 40, 2, centered=(True, True, False))
        .rotate((0, 0, 0), (1, 0, 0), -90)
        .translate((0, -25, 0))
    )

    # union
    bracket = h_plate.union(v_plate)

    # 三脚穴（union後）
    bracket = (
        bracket
        .faces(">Z")
        .workplane()
        .center(0, -5)
        .circle(3.25)
        .cutThruAll()
    )

    # カメラ穴（union後）
    bracket = (
        bracket
        .faces("<Y")
        .workplane()
        .pushPoints([(-31.5, 10), (-31.5, 18), (31.5, 10), (31.5, 18)])
        .circle(1.6)
        .cutThruAll()
    )

    return bracket
```

**検証ポイント**:
- [ ] XY断面で三脚穴が検出できるか
- [ ] XZ断面でカメラ穴4個が検出できるか
- [ ] 穴の位置・サイズが正しいか

**実行コマンド**: `uv run python tests/toy_04_l_shape_no_fillet.py`

---

### トイプロブレム5: L字（フィレットあり）でDXF穴検出
**目的**: フィレットが穴の検出に影響するか確認

**テストコード**: `tests/toy_05_l_shape_with_fillet.py`

**期待結果**:
- トイプロブレム4と同じ結果（フィレットは穴に影響しないはず）

**実装内容**:
```python
def create_l_shape_with_fillet():
    """L字ブラケット（フィレットあり）"""
    bracket = create_l_shape_no_fillet()

    # 内側フィレット
    try:
        bracket = bracket.edges("|X and >Z and <Y").fillet(3.0)
    except:
        pass

    # 外側フィレット
    try:
        bracket = bracket.edges("|Z and >Y").fillet(1.5)
    except:
        pass

    return bracket
```

**検証ポイント**:
- [ ] フィレット適用後も穴が検出できるか
- [ ] 穴の数・位置・サイズが変わらないか

**実行コマンド**: `uv run python tests/toy_05_l_shape_with_fillet.py`

---

## テストフレームワーク構造

### ディレクトリ構成
```
tests/
├── toy_01_simple_box_with_hole.py
├── toy_02_union_two_boxes.py
├── toy_03_union_then_hole.py
├── toy_04_l_shape_no_fillet.py
├── toy_05_l_shape_with_fillet.py
└── test_utils.py  # 共通テストユーティリティ
```

### 共通テストユーティリティ (`test_utils.py`)
```python
def export_and_verify_dxf(
    model,
    section_plane: str,
    section_height: float,
    expected_circles: int,
    expected_diameter: float = None,
    tolerance: float = 0.1
) -> bool:
    """
    DXFエクスポートして穴を検証

    Args:
        model: CadQueryモデル
        section_plane: "XY" or "XZ"
        section_height: 断面の高さ
        expected_circles: 期待される円の数
        expected_diameter: 期待される直径（Noneなら検証しない）
        tolerance: 許容誤差

    Returns:
        bool: テストが成功したか
    """
    ...
```

## TDDサイクルの実行手順

### 各トイプロブレムごと:
1. **Red**: テストを書いて実行（失敗することを確認）
2. **Green**: 最小限の実装でテストを通す
3. **Refactor**: コードをきれいにする
4. **記録**: 作業記録に詳細を記録

### 実行順序
1. トイプロブレム1 → Green確認
2. トイプロブレム2 → Green確認
3. トイプロブレム3 → Green確認（ここで根本原因が明確になる）
4. トイプロブレム4 → Green確認（ここでsection高さが分かる）
5. トイプロブレム5 → Green確認
6. 本番コード修正
7. 最終テスト

## 成功基準
- 全トイプロブレムのテストがPass（Green）
- 本番コード（`l_bracket_camera_mount.py`）のテストがPass
- DXFパーサーで期待通りの穴が検出できる

## 作業時間見積もり
- トイプロブレム1-3: 各15分 = 45分
- トイプロブレム4-5: 各20分 = 40分
- 本番コード修正: 30分
- ドキュメント更新: 15分
- **合計: 約2時間**

## 参考: section()の高さ指定について
```python
# XY断面（Z=h平面で切断）
model.section(height=h)

# XZ断面（rotate後にZ=h平面で切断、元の座標系ではY=h?）
model.rotate((0,0,0), (1,0,0), 90).section(height=h)
```

**重要**: rotate()後の座標系とsection(height)の関係を理解する必要がある
→ トイプロブレム1-3で明確化
