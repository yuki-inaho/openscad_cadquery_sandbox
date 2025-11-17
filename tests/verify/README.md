# L字ブラケット 検証スクリプト

このディレクトリには、L字ブラケットの開発・デバッグ過程で作成された検証スクリプトが格納されています。

## スクリプト一覧

### アクティブな検証スクリプト

#### `verify_camera_hole_position_v2.py`
**最新版のカメラ穴位置検証スクリプト**

- 目的: カメラ穴の位置を検証し、複数の候補を比較
- 機能:
  - 5つの穴位置候補を生成
  - 各候補の相対位置とフィレットクリアランスを解析
  - DXF断面で視覚的に比較
  - フィレット適用テスト
- 使用法:
  ```bash
  uv run python tests/verify/verify_camera_hole_position_v2.py
  ```
- 出力: `outputs/verify_camera_position/`

#### `verify_fillet_status.py`
**フィレット状態検証スクリプト**

- 目的: フィレットが正しく適用されているかを確認
- 機能:
  - フィレットなし/ありのモデルを生成
  - エッジ数・タイプの変化を解析
  - DXF断面でフィレット形状を確認
- 使用法:
  ```bash
  uv run python tests/verify/verify_fillet_status.py
  ```
- 出力: `outputs/verify_fillet/`

#### `debug_edges.py`
**エッジ解析・デバッグスクリプト**

- 目的: L字ブラケットの全エッジを解析し、フィレット適用の問題を診断
- 機能:
  - 全エッジの位置・方向・タイプを列挙
  - L字内側角エッジの候補を自動検出
  - 各セレクタの動作確認
  - フィレット適用テスト
- 使用法:
  ```bash
  uv run python tests/verify/debug_edges.py
  ```
- 重要な発見:
  - union後、L字内側角（Z=2, Y=-25）にエッジが存在しない
  - 代替エッジ（Z=2, Y=-23）を使用する必要がある

### 開発履歴スクリプト（アーカイブ）

以下のスクリプトは、開発過程で作成されたもので、現在は参考用に保管されています。

#### `verify_camera_holes_position.py`
初期版のカメラ穴位置検証スクリプト（v2で置き換え）

#### `verify_current_shape.py`
形状の現状確認スクリプト（開発初期）

#### `verify_final_fix.py`
最終修正の検証スクリプト

#### `verify_plate_positions.py`
水平板・垂直板の位置検証スクリプト

#### `verify_rotation_fix.py`
回転修正の検証スクリプト

## 使用ガイドライン

### 新しい検証スクリプトの追加

1. スクリプト名: `verify_<feature>_<date>.py` または `debug_<feature>.py`
2. 出力ディレクトリ: `outputs/verify_<feature>/`
3. `.gitignore`に出力ディレクトリを追加
4. このREADMEに説明を追加

### 検証スクリプトのベストプラクティス

1. **明確な目的**: スクリプトの目的を冒頭に記載
2. **独立性**: 他のスクリプトに依存しない
3. **出力**: DXFやレポートを生成して視覚的に確認可能にする
4. **エラーハンドリング**: 適切なtry-exceptで失敗を報告
5. **ドキュメント**: 使用方法と期待される結果を記載

## 主要な検証ポイント

### 穴位置検証
- グローバル座標での位置
- DXF断面での確認
- 仕様要件との照合

### フィレット検証
- エッジセレクタの正確性
- フィレット半径の適用
- トポロジーの変化（エッジ数、タイプ）
- DXF断面での形状確認

### 形状検証
- バウンディングボックス
- L字形状（T字ではない）
- 一体構造（union成功）

## トラブルシューティング

### エッジが見つからない
- `debug_edges.py`で全エッジを列挙
- union前後のトポロジー変化を確認
- セレクタの構文を確認

### フィレット失敗
- エッジセレクタが正しいか確認
- フィレット半径が大きすぎないか確認
- 穴との干渉をチェック
- エッジのトポロジーを確認

### DXF解析エラー
- section_plane引数を確認（"XY", "XZ", "YZ"）
- section_height引数を確認
- DXFパーサーのエラーメッセージを確認

## 関連ファイル

- 仕様テスト: `tests/test_l_bracket_requirements.py`
- メイン実装: `examples/cadquery/l_bracket_camera_mount.py`
- 作業計画: `docs/work_plan_fillet_and_holes.md`
- 作業記録: `docs/workdoc_nov17_2025_openscad_setup.md`

---

**最終更新**: 2025-11-17
