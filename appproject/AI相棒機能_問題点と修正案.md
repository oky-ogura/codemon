# 相棒AI機能 問題点と修正案

## ✅ 修正完了（2026年2月9日）

### 実施した修正内容

**採用した案: 案1（統合）**

1. **ai_chat_base.htmlの削除**
   - 以下の7つの画面から`{% include 'includes/ai_chat_base.html' %}`を削除:
     - ✅ system_choice.html
     - ✅ system_create.html
     - ✅ block_choice.html
     - ✅ block_create.html
     - ✅ checklist_selection.html
     - ✅ s_account.html
     - ✅ t_account.html
   
2. **karihome.htmlの修正**
   - 独自のキャラクター表示ロジックを削除
   - `character_widget.html`をkarihomeモードでインクルード
   - 不要なJavaScriptとCSSを削除

3. **重複ファイルの削除**
   - ✅ `codemon/templates/includes/ai_chat_base.html` - 削除
   - ✅ `accounts/templates/includes/character_widget.html` - 削除（codemon版を使用）
   - ✅ `accounts/templates/includes/character_widget_old.html` - 削除

### 修正後の構成

**統一されたシステム: `character_widget.html`のみ**

- **karihome画面**: `character_widget.html` (karihomeモード)
  - 中央に大きく表示
  - 吹き出し付き
  - 「話しかける」ボタン
  
- **その他の画面**: `character_widget.html` (sidebarモード)
  - base.htmlから自動的に表示
  - 右下に小さく表示
  - 最小化機能付き

### メリット

✅ システムが1つに統一され、保守が容易
✅ 重複表示の問題が解消
✅ 全画面で統一されたUI/UX
✅ コードの複雑さが減少

---

## 📋 元の問題点（参考）

### 1. システムの重複
現在、2つの異なる相棒AIシステムが存在し、混乱を引き起こしています：

#### システムA: `character_widget.html` 
- **場所**: `codemon/templates/includes/character_widget.html`
- **呼び出し元**: `base.html` の `global_character_widget` ブロック
- **表示形式**: 
  - karihomeモード: 中央に大きく表示、吹き出し付き
  - sidebarモード: 右下に小さく表示、チャットモーダル形式
- **対象画面**: ほとんどの画面（base.htmlを継承する全画面）

#### システムB: `ai_chat_base.html`
- **場所**: `codemon/templates/includes/ai_chat_base.html`
- **呼び出し元**: 各画面で個別に `{% include 'includes/ai_chat_base.html' %}`
- **表示形式**: 右下固定、独自の吹き出しUIとチャット
- **対象画面**: 
  - karihome.html
  - system_choice.html
  - system_create.html
  - block_choice.html
  - block_create.html
  - checklist_selection.html
  - s_account.html
  - t_account.html

### 2. 重複インクルードの問題

以下の画面では**両方のシステムが同時に表示**されています：

```
✗ system_choice.html
  - base.html → character_widget.html (sidebar)
  - 自身 → ai_chat_base.html
  → 結果: 2つの相棒AIが表示される

✗ system_create.html
  - base.html → character_widget.html (sidebar)
  - 自身 → ai_chat_base.html
  → 結果: 2つの相棒AIが表示される

✗ block_choice.html, block_create.html
✗ checklist_selection.html
✗ s_account.html, t_account.html
  （同様の重複）
```

### 3. レイアウトの不一致

#### karihome
- `character_widget.html` を karihomeモードで使用
- 中央に大きく配置
- 吹き出し表示
- 「話しかける」ボタン → `ai_chat_base.html` のチャットを開く

#### 他の画面
- `character_widget.html` (sidebar) + `ai_chat_base.html`
- 両方が右下に表示されて衝突
- レイアウトが異なる

## 🎯 修正案

### 案1: `ai_chat_base.html` を統合・廃止（推奨）

**方針**: `character_widget.html` に一本化

**変更内容**:
1. `ai_chat_base.html` を使用している全画面から削除
2. `character_widget.html` のチャット機能を強化
3. karihomeは引き続き `character_widget.html` (karihomeモード) を使用
4. 他画面は `base.html` の `character_widget.html` (sidebarモード) のみ

**メリット**:
- システムが1つになり管理が楽
- 重複がなくなる
- 統一されたUI/UX

**デメリット**:
- `ai_chat_base.html` の独自機能があれば移植が必要

---

### 案2: `character_widget.html` を特定画面で非表示

**方針**: 画面ごとに使い分け

**変更内容**:
1. `ai_chat_base.html` を使う画面では `base.html` の `character_widget.html` を非表示
2. `base.html` の除外リストに追加:
   ```django
   {% elif '/accounts/system/' in current_path %}
     {# ai_chat_base.htmlを使うので非表示 #}
   {% elif '/accounts/block/' in current_path %}
     {# ai_chat_base.htmlを使うので非表示 #}
   ```

**メリット**:
- 既存コードの変更が少ない
- すぐに重複を解消できる

**デメリット**:
- 2つのシステムが並存し続ける
- 保守が複雑

---

### 案3: 機能別に完全分離

**方針**: karihomeは独自、他は統一

**変更内容**:
1. karihome専用の表示システム（現状維持）
2. 他画面は全て `character_widget.html` (sidebar) のみ
3. `ai_chat_base.html` を削除

**メリット**:
- karihomeの特別感を維持
- 他画面は統一

**デメリット**:
- やはり2種類のシステムが残る

## 📌 推奨: 案1（統合）

**理由**:
- 長期的な保守性が最も高い
- ユーザー体験が統一される
- コードの複雑さが減る

**実装ステップ**:
1. `ai_chat_base.html` の機能を `character_widget.html` に移植（必要なら）
2. 各画面から `{% include 'includes/ai_chat_base.html' %}` を削除
3. テスト・動作確認

---

## 📝 修正が必要なファイル一覧

### 削除が必要な行:
1. `accounts/templates/system/system_choice.html` - 450行目
2. `accounts/templates/system/system_create.html` - 505行目
3. `accounts/templates/block/block_choice.html` - 409行目
4. `accounts/templates/block/block_create.html` - 526行目
5. `codemon/templates/codemon/checklist_selection.html` - 374行目
6. `accounts/templates/accounts/s_account.html` - 489行目
7. `accounts/templates/accounts/t_account.html` - 659行目

### karihomeは維持:
- `accounts/templates/accounts/karihome.html` - 521行目（維持）

---

## 🔧 次のアクション

どの修正案を採用しますか？
- 案1: 統合（推奨）
- 案2: 除外リスト追加
- 案3: 機能別分離
- その他: カスタム案

選択後、具体的な修正作業を開始します。
