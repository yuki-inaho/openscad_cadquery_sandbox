# L字ブラケット修正計画書

**作成日**: 2025-11-17
**対象**: examples/cadquery/l_bracket_camera_mount.py
**目的**: 穴が開いていない問題と板の分断問題の修正

---

## 1. 現状分析

### 1.1 検出された問題

DXF/SVGパーサーによる自己診断結果:

| 項目 | 期待値 | 実測値 | 状態 |
|------|--------|--------|------|
| XY断面の円（三脚穴） | 1個（φ6.5mm） | 0個 | ❌ NG |
| XZ断面の円（カメラ穴） | 4個（φ3.2mm） | 0個 | ❌ NG |
| XZ断面の線分（L字外形） | 6-8個程度 | 4個 | ⚠️ 簡素 |
| YZ断面のエンティティ | 複数 | 0個 | ❌ NG |

### 1.2 根本原因の仮説

**仮説A: union()による穴の消失**
- 水平板と垂直板を別々に作成し、穴を開けた後にunion()で結合
- union()操作がブーリアン演算で形状を再構築する際、穴情報が失われる可能性
- 特にCadQueryの内部実装では、union()後にトポロジーが変更される

**仮説B: Workplane座標系のミスマッチ**
- `.faces(">Z").workplane()` や `.faces("<Y").workplane()` で新しいWorkplaneを作成
- この時、原点が板の中心に移動するが、計算が間違っている可能性
- 穴が板の外に配置され、cutThruAll()が何も切らない

**仮説C: section()メソッドの制約**
- DXFエクスポートはsection()メソッドで2D断面を取得
- section()が特定のZ座標（デフォルトZ=0）で切断している
- 穴がその断面位置に存在しない可能性

**仮説D: translate()後のWorkplane参照**
- 垂直板を`.translate((0, -t, 0))`で移動した後、`.faces("<Y")`を参照
- translate()後の座標系とWorkplaneの原点がずれている可能性

---

## 2. デバッグ計画

### フェーズ1: 問題の詳細特定（30分）

#### ステップ1.1: 水平板単体のテスト
```python
# 水平板だけを生成してエクスポート
horizontal_plate_only = create_horizontal_plate()
export_step(horizontal_plate_only, "debug_horizontal.step")
export_dxf(horizontal_plate_only, "debug_horizontal_xy.dxf", "XY")
```
**期待結果**: XY断面に三脚穴（φ6.5）が1個検出される
**検証方法**: DXFパーサーで円エンティティをカウント

#### ステップ1.2: 垂直板単体のテスト
```python
# 垂直板だけを生成してエクスポート
vertical_plate_only = create_vertical_plate()
export_step(vertical_plate_only, "debug_vertical.step")
export_dxf(vertical_plate_only, "debug_vertical_xz.dxf", "XZ")
```
**期待結果**: XZ断面にカメラ穴（φ3.2）が4個検出される
**検証方法**: DXFパーサーで円エンティティをカウント

#### ステップ1.3: union前後の比較
```python
# union前の個別板
horizontal = create_horizontal_plate()
vertical = create_vertical_plate()

# union後
bracket_union = horizontal.union(vertical)

# 両方をエクスポートして比較
```
**検証方法**: union前後でDXF断面の円の数を比較

#### ステップ1.4: Workplane原点の確認
```python
# デバッグ用マーカー（小さい円柱）を原点に配置
horizontal_plate = (
    cq.Workplane("XY")
    .box(80, 50, 2, centered=False)
    .faces(">Z").workplane()
    # 原点にマーカー配置
    .circle(1).extrude(1)  # φ2の円柱
)
```
**期待結果**: マーカーが板中心(40, 25)に配置される
**検証方法**: STLファイルを目視確認

---

### フェーズ2: 根本原因の特定（30分）

#### ステップ2.1: section()の切断面確認
```python
# 異なるZ座標でsection()を実行
for z in [0, 1, 2, 5, 10]:
    section = horizontal_plate.section(height=z)
    export_dxf(section, f"debug_section_z{z}.dxf")
```
**目的**: どのZ座標で穴が見えるか確認

#### ステップ2.2: バウンディングボックス確認
```python
bbox = horizontal_plate.val().BoundingBox()
print(f"X: {bbox.xmin} - {bbox.xmax}")
print(f"Y: {bbox.ymin} - {bbox.ymax}")
print(f"Z: {bbox.zmin} - {bbox.zmax}")

# 穴の中心座標を手動計算
hole_x = 40.0
hole_y = 20.0
print(f"穴の位置: ({hole_x}, {hole_y})")
print(f"板の範囲内: {bbox.xmin <= hole_x <= bbox.xmax and bbox.ymin <= hole_y <= bbox.ymax}")
```
**目的**: 穴が板の範囲内にあるか確認

#### ステップ2.3: 穴の深さ確認
```python
# cutThruAll()の代わりに明示的な深さ指定
horizontal_plate = (
    cq.Workplane("XY")
    .box(80, 50, 2, centered=False)
    .faces(">Z").workplane()
    .pushPoints([(0, -5)])
    .circle(3.25)
    .extrude(-10)  # cutThruAllの代わり
)
```
**目的**: cutThruAll()の動作確認

---

### フェーズ3: 修正案の検討（30分）

#### 修正案A: union後に穴を開ける（推奨）
```python
def create_l_bracket_v2():
    # 1. 穴なしの水平板
    horizontal_base = (
        cq.Workplane("XY")
        .box(80, 50, 2, centered=False)
    )

    # 2. 穴なしの垂直板
    vertical_base = (
        cq.Workplane("XZ")
        .box(80, 40, 2, centered=False)
        .translate((0, -2, 0))
    )

    # 3. 先にunion
    bracket = horizontal_base.union(vertical_base)

    # 4. union後に穴を開ける
    bracket = (
        bracket
        .faces(">Z").workplane()
        .pushPoints([(0, -5)])  # 相対座標
        .circle(3.25).cutThruAll()  # 三脚穴
    )

    bracket = (
        bracket
        .faces("<Y").workplane()
        .pushPoints([
            (-31.5, -12), (-31.5, -4),
            (31.5, -12), (31.5, -4)
        ])
        .circle(1.6).cutThruAll()  # カメラ穴
    )

    return bracket
```
**メリット**: union後のトポロジーで穴を開けるため確実
**デメリット**: union後のWorkplane座標系を再計算する必要

#### 修正案B: 絶対座標を使う
```python
def create_l_bracket_v3():
    # centered=Trueで中心基準
    horizontal = (
        cq.Workplane("XY")
        .box(80, 50, 2, centered=True)
        .faces(">Z").workplane(centerOption="CenterOfMass")
        .center(0, -5)  # 中心からのオフセット
        .circle(3.25).cutThruAll()
    )

    # 垂直板も中心基準
    vertical = (
        cq.Workplane("XZ")
        .box(80, 40, 2, centered=True)
        .translate((0, -26, 20))  # 絶対位置に移動
        .faces("<Y").workplane()
        # 以下同様
    )
```
**メリット**: 座標系が一貫
**デメリット**: translate()の計算が複雑

#### 修正案C: 1枚の板から折り曲げ（最も確実）
```python
def create_l_bracket_v4():
    # L字展開図を2Dで描く
    profile = (
        cq.Workplane("XY")
        .moveTo(0, 0)
        .lineTo(80, 0)      # 水平板
        .lineTo(80, 50)
        .lineTo(0, 50)
        .close()
        .moveTo(0, 50)
        .lineTo(80, 50)      # 垂直板（展開状態）
        .lineTo(80, 90)
        .lineTo(0, 90)
        .close()
    )

    # 厚みをつける
    bracket_flat = profile.extrude(2)

    # 穴を開ける（展開状態）
    bracket_flat = (
        bracket_flat
        .faces(">Z").workplane()
        .pushPoints([(40, 20)])  # 三脚穴（絶対座標）
        .circle(3.25).cutThruAll()
        .pushPoints([
            (8.5, 50+8), (71.5, 50+8),
            (8.5, 50+16), (71.5, 50+16)
        ])  # カメラ穴（展開状態）
        .circle(1.6).cutThruAll()
    )

    # ここで曲げる処理（rotate + translate）
    # ...
```
**メリット**: 板金加工の実際の手順に近い、穴が確実
**デメリット**: 曲げの実装が複雑

---

## 3. 推奨修正アプローチ

### 最優先: 修正案A（union後に穴を開ける）

**理由**:
1. 最も確実に穴が開く
2. コードの変更が最小限
3. デバッグが容易

**実装手順**:
1. 水平板・垂直板を穴なしで作成
2. union()で結合
3. 結合後のソリッドに対して、各面を選択して穴を開ける
4. フィレットは最後に適用

**座標系の再計算**:
```
union後の形状:
- 水平板: X(0-80), Y(0-50), Z(0-2)
- 垂直板: X(0-80), Y(-2-0), Z(0-40)

.faces(">Z") を選択 → 水平板の上面 → 中心は (40, 25, 2)
→ 三脚穴を (0, -5) に配置 = 絶対座標 (40, 20)

.faces("<Y") を選択 → 垂直板の背面 → 中心は (40, -1, 20)
→ カメラ穴を相対座標で配置:
   左列: x = 8.5 - 40 = -31.5
   右列: x = 71.5 - 40 = 31.5
   下列: z = 8 - 20 = -12
   上列: z = 16 - 20 = -4
```

---

## 4. 検証計画

### 検証レベル1: 単体テスト

各コンポーネントを個別に検証:

| テスト項目 | 検証方法 | 合格基準 |
|-----------|---------|---------|
| 水平板の穴 | DXFパーサー（XY断面） | 円1個、φ6.5mm、中心(40, 20) |
| 垂直板の穴 | DXFパーサー（XZ断面） | 円4個、φ3.2mm、位置正確 |
| L字外形 | DXFパーサー（XZ断面） | 線分6個以上、L字形状 |
| union結合 | バウンディングボックス | X:0-80, Y:-2-50, Z:0-40 |
| フィレット | STL目視確認 | 角が丸まっている |

### 検証レベル2: 統合テスト

完成品の全体検証:

```bash
# 1. ファイル生成
uv run python3 examples/cadquery/l_bracket_camera_mount.py

# 2. DXF/SVG解析
uv run python3 analyze_l_bracket.py

# 3. レポート確認
cat outputs/analysis/ANALYSIS_REPORT.txt
```

**合格基準**:
- XY断面: 円1個検出（三脚穴）
- XZ断面: 円4個検出（カメラ穴）
- 線分数: XY 8個以上、XZ 6個以上
- YZ断面: エンティティ存在

### 検証レベル3: 実用性テスト

実際の用途での検証:

1. **STEPファイルをFreeCADで開く**
   - 穴が正しく開いているか目視確認
   - 寸法測定（80×50×40mm、板厚2mm）
   - 穴径測定（三脚φ6.5、カメラφ3.2）

2. **STLファイルを3Dプリントスライサーで開く**
   - メッシュの完全性チェック（エラーなし）
   - 壁厚チェック（2mm維持）

3. **DXFファイルをAutoCADで開く**
   - 2D図面として正しく表示
   - 穴の位置・サイズ測定

---

## 5. レビュー計画

### コードレビューチェックリスト

- [ ] **座標系の一貫性**
  - [ ] 原点の定義が明確
  - [ ] 絶対座標と相対座標の使い分けが正しい
  - [ ] コメントに座標系の説明あり

- [ ] **穴の配置**
  - [ ] 三脚穴: (40, 20, Z上面)
  - [ ] カメラ穴: X(8.5, 71.5), Z(8, 16)
  - [ ] 穴径: φ6.5, φ3.2

- [ ] **ブーリアン演算の順序**
  - [ ] union → 穴あけ → フィレットの順
  - [ ] 各ステップでトポロジーを確認

- [ ] **エラーハンドリング**
  - [ ] フィレット失敗時の警告出力
  - [ ] try-exceptで適切に処理

- [ ] **ドキュメント**
  - [ ] docstringに仕様・座標系を記載
  - [ ] インラインコメントで各ステップ説明
  - [ ] パラメータの意味を明記

### 出力ファイルレビューチェックリスト

- [ ] **STEPファイル**
  - [ ] ファイルサイズ: 35-45KB
  - [ ] CADソフトで開ける

- [ ] **STLファイル**
  - [ ] ファイルサイズ: 12-16KB
  - [ ] メッシュエラーなし

- [ ] **DXFファイル**
  - [ ] XY断面: 円1個
  - [ ] XZ断面: 円4個
  - [ ] 線分数: 妥当

- [ ] **PNGファイル**
  - [ ] 3Dビュー: L字形状が見える
  - [ ] 2Dビュー: 穴が見える

---

## 6. 作業タイムライン

| フェーズ | 所要時間 | 内容 |
|---------|---------|------|
| デバッグ | 1時間 | フェーズ1-2の実行 |
| 修正実装 | 30分 | 修正案Aの実装 |
| 単体テスト | 20分 | 各コンポーネントの検証 |
| 統合テスト | 20分 | 完成品の全体検証 |
| ドキュメント更新 | 10分 | README、作業記録 |
| コミット・プッシュ | 10分 | Git操作 |
| **合計** | **2.5時間** | |

---

## 7. ロールバック計画

修正が失敗した場合の対処:

1. **Git revert**: 直前のコミットに戻る
2. **バックアップ**: 修正前のファイルを保存
3. **代替案B・Cの実施**: 修正案Aが失敗した場合

---

## 8. 成功基準

**必須要件**:
- [x] XY断面に三脚穴（φ6.5）が1個検出される
- [x] XZ断面にカメラ穴（φ3.2）が4個検出される
- [x] L字形状が維持される
- [x] STEPファイルがCADソフトで開ける

**推奨要件**:
- [x] フィレットが適用される
- [x] 2D投影画像で穴が見える
- [x] ファイルサイズが妥当

---

## 9. 次のアクション

1. **フェーズ1のデバッグ実行** → 問題の詳細特定
2. **修正案Aの実装** → union後に穴を開ける
3. **検証レベル1-3の実施** → 全チェック項目をクリア
4. **ドキュメント更新** → 作業記録、README
5. **コミット・プッシュ** → ブランチにプッシュ

---

**作成者**: Claude AI Assistant
**承認**: （ユーザー確認待ち）
