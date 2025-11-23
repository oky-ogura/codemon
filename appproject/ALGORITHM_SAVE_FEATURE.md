# アルゴリズム保存機能の実装

## 実装内容

### 1. 機能概要
- **index.html**で作成したアルゴリズム(Blockly)の情報をDBに保存
- **/accounts/block/choice/**でアルゴリズム一覧から内容の確認や編集、削除ができる

### 2. 実装したファイル

#### モデル変更
- **codemon/models.py**: `Algorithm`モデルに`blockly_xml`フィールドを追加
  - Blocklyのワークスペース情報をXML形式で保存

#### ビュー変更
- **accounts/views.py**:
  - `block_index`: 編集モードで既存アルゴリズムのBlocklyデータを読み込み
  - `block_create`: アルゴリズム名、詳細、BlocklyデータをDBに保存
  - `block_list`: アルゴリズム一覧を表示
  - `block_details`: アルゴリズム詳細を表示・編集
  - `block_delete`: アルゴリズムを削除

#### テンプレート変更
- **accounts/templates/block/index.html**:
  - 保存ボタンでBlocklyワークスペースをXMLに変換してセッションストレージに保存
  - `/accounts/block/create/`へ遷移
  - 編集モードで既存のBlocklyデータを読み込んでワークスペースに復元

- **accounts/templates/block/block_create.html**:
  - セッションストレージからBlocklyデータを取得
  - アルゴリズム名、詳細、BlocklyデータをPOSTで送信
  - 保存後は`save.html`を表示

- **accounts/templates/block/save.html**:
  - 保存完了メッセージを表示
  - アルゴリズム一覧へのリンクボタン

- **accounts/templates/block/block_choice.html**:
  - 「作成したアルゴリズム一覧を開く」ボタンで`/accounts/block/list/`へ遷移
  - 「新しいアルゴリズムを作成」ボタンで`/accounts/block/`へ遷移

- **accounts/templates/block/block_list.html**:
  - アルゴリズム一覧を表示
  - 各アルゴリズムの「詳細」ボタンで`/accounts/block/details/`へ遷移

- **accounts/templates/block/block_details.html**:
  - アルゴリズム詳細を表示
  - 「編集」ボタンで`/accounts/block/?id=xxx`へ遷移（Blockly編集画面）
  - 「削除」ボタンで`/accounts/block/delete/?id=xxx`へ遷移

### 3. データフロー

#### 新規作成フロー
1. `/accounts/block/` でBlocklyを使ってアルゴリズムを作成
2. 「保存」ボタンをクリック
   - BlocklyワークスペースをXMLに変換
   - セッションストレージに保存
3. `/accounts/block/create/` に自動遷移
   - セッションストレージからBlocklyデータを読み込み
   - アルゴリズム名と詳細を入力
4. 「保存」ボタンをクリック
   - DBにアルゴリズム情報を登録（algorithm_name, algorithm_description, blockly_xml）
5. `/accounts/block/save.html` を表示
   - 保存完了メッセージ
   - アルゴリズム一覧へのリンク

#### 編集フロー
1. `/accounts/block/list/` でアルゴリズム一覧を表示
2. 「詳細」ボタンをクリック
3. `/accounts/block/details/?id=xxx` で詳細を表示
4. 「編集」ボタンをクリック
5. `/accounts/block/?id=xxx` でBlockly編集画面を表示
   - 既存のBlocklyデータ（blockly_xml）を読み込んでワークスペースに復元
6. 編集後、「保存」ボタンをクリック
   - 新規作成と同じフロー（ただしalgorithm_idがあるので更新処理）

#### 削除フロー
1. `/accounts/block/details/?id=xxx` で詳細を表示
2. 「削除」ボタンをクリック
3. `/accounts/block/delete/?id=xxx` で削除確認画面を表示
4. 削除確認後、DBから削除
5. `/accounts/block/delete/success/` で削除完了メッセージを表示

### 4. マイグレーション
```bash
# マイグレーションファイルを作成
python manage.py makemigrations codemon

# マイグレーションを適用
python manage.py migrate codemon
```

生成されたマイグレーションファイル: `codemon/migrations/0007_algorithm_blockly_xml.py`

### 5. 使用方法

#### 新規作成
1. ログイン後、`/accounts/block/choice/` にアクセス
2. 「新しいアルゴリズムを作成」をクリック
3. Blocklyでアルゴリズムを作成
4. 「保存」ボタンをクリック
5. アルゴリズム名と詳細を入力して「保存」

#### 一覧確認
1. `/accounts/block/choice/` にアクセス
2. 「作成したアルゴリズム一覧を開く」をクリック
3. アルゴリズム一覧が表示される

#### 編集
1. アルゴリズム一覧から編集したいアルゴリズムの「詳細」をクリック
2. 「編集」ボタンをクリック
3. Blocklyでアルゴリズムを編集
4. 「保存」ボタンをクリック
5. アルゴリズム名と詳細を編集して「保存」

#### 削除
1. アルゴリズム一覧から削除したいアルゴリズムの「詳細」をクリック
2. 「削除」ボタンをクリック
3. 削除確認画面で「削除」をクリック

### 6. 注意事項
- Blocklyデータは`blockly_xml`フィールドにXML形式で保存されます
- セッションストレージは一時的な保存に使用され、`/accounts/block/create/`でデータを読み込んだ後は削除されます
- アルゴリズムの所有者のみが編集・削除できます（`user`フィールドでチェック）

### 7. 今後の改善案
- Blocklyプレビュー機能の追加（詳細画面でBlocklyの視覚的プレビュー）
- アルゴリズムの複製機能
- アルゴリズムの検索・フィルタ機能
- アルゴリズムのカテゴリ分類
