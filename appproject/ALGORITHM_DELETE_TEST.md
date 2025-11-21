# アルゴリズム削除機能のテスト手順

## 実装された機能

✅ アルゴリズム削除確認画面 (`block_delete.html`)
✅ アルゴリズム削除完了画面 (`block_delete_success.html`)
✅ 削除ビュー (`block_delete`, `block_delete_success`)
✅ URLパターン (`/accounts/block/delete/`, `/accounts/block/delete/success/`)
✅ 詳細画面の削除ボタン

## テスト手順

### 1. 開発サーバーの起動

```powershell
# 仮想環境を有効化（必要な場合）
# .\venv\Scripts\Activate.ps1

# プロジェクトディレクトリに移動
cd "c:\Users\y_ogura\Desktop\卒業制作\codemon\appproject"

# 開発サーバーを起動
python manage.py runserver
```

### 2. ブラウザでアクセス

1. ブラウザで `http://127.0.0.1:8000/` にアクセス
2. ログイン画面でログイン
3. アルゴリズム一覧画面に移動: `http://127.0.0.1:8000/accounts/block/list/`

### 3. 削除機能のテスト

#### パターン1: 詳細画面から削除
```
1. アルゴリズム一覧で「詳細」ボタンをクリック
   → URL: /accounts/block/details/?id=5000001
   
2. 詳細画面で「削除」ボタンをクリック
   → URL: /accounts/block/delete/?id=5000001
   → 削除確認画面が表示される
   
3. 削除確認画面の内容を確認:
   - アルゴリズム名
   - アルゴリズム概要
   - 作成日時
   - 警告メッセージ
   
4. 「削除する」ボタンをクリック
   → URL: /accounts/block/delete/success/
   → 削除完了画面が表示される
   
5. 「アルゴリズム一覧に戻る」ボタンをクリック
   → 削除されたアルゴリズムが一覧から消えている
```

#### パターン2: 直接URLアクセス
```
1. ブラウザのアドレスバーに直接入力:
   http://127.0.0.1:8000/accounts/block/delete/?id=5000001
   
2. 削除確認画面が表示される
```

#### パターン3: キャンセル
```
1. 削除確認画面で「キャンセル」ボタンをクリック
   → 詳細画面に戻る
   → アルゴリズムは削除されていない
```

## トラブルシューティング

### 問題1: 画面が表示されない

**確認事項:**
1. URLが正しいか確認
   - 正: `/accounts/block/delete/?id=5000001`
   - 誤: `/accounts/block/delete/` (IDなし)

2. アルゴリズムIDが存在するか確認
   ```python
   # Djangoシェルで確認
   python manage.py shell
   >>> from codemon.models import Algorithm
   >>> Algorithm.objects.all()
   ```

3. ビューが正しくインポートされているか確認
   ```python
   # accounts/urls.py
   from . import views
   path('block/delete/', views.block_delete, name='block_delete'),
   ```

### 問題2: 404エラーが出る

**原因:** URLパターンが登録されていない

**解決策:**
1. `accounts/urls.py` を確認
2. 以下の行があることを確認:
   ```python
   path('block/delete/', views.block_delete, name='block_delete'),
   path('block/delete/success/', views.block_delete_success, name='block_delete_success'),
   ```

### 問題3: テンプレートが見つからない

**原因:** テンプレートファイルのパスが間違っている

**解決策:**
1. ファイルが存在することを確認:
   - `accounts/templates/block/block_delete.html`
   - `accounts/templates/block/block_delete_success.html`

2. settings.pyのTEMPLATES設定を確認

### 問題4: 「アルゴリズムが見つかりません」エラー

**原因:** 
- 指定されたIDのアルゴリズムが存在しない
- 他のユーザーのアルゴリズムを削除しようとしている

**解決策:**
1. 正しいアルゴリズムIDを使用
2. 自分が作成したアルゴリズムのみ削除可能

## デバッグ方法

### ビューでprint文を使う

```python
# accounts/views.py の block_delete ビュー内
def block_delete(request):
    algorithm_id = request.GET.get('id')
    print(f"DEBUG: algorithm_id = {algorithm_id}")  # デバッグ
    
    if not algorithm_id:
        print("DEBUG: IDが指定されていません")  # デバッグ
        messages.error(request, 'アルゴリズムIDが指定されていません。')
        return redirect('accounts:block_list')
    
    try:
        algorithm = Algorithm.objects.get(algorithm_id=algorithm_id)
        print(f"DEBUG: algorithm found = {algorithm.algorithm_name}")  # デバッグ
        # ...
```

### ブラウザの開発者ツールを使う

1. F12キーで開発者ツールを開く
2. Consoleタブでエラーメッセージを確認
3. Networkタブでリクエスト/レスポンスを確認

## 期待される動作

✅ 削除確認画面が正しく表示される
✅ アルゴリズム情報（名前、概要、作成日）が表示される
✅ 削除ボタンで削除が実行される
✅ 削除完了画面が表示される
✅ 削除後、一覧から消える
✅ キャンセルボタンで詳細画面に戻る
✅ 他のユーザーのアルゴリズムは削除できない

## 実装済みのセキュリティ機能

🔒 所有者チェック（自分のアルゴリズムのみ削除可能）
🔒 CSRFトークン保護
🔒 2段階削除（確認→実行）
