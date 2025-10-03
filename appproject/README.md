# Codemon - AIプログラミング学習支援システム

## 概要
CodemonはAIを活用したプログラミング学習支援システムです。学生のグループ管理、チャット機能、学習進捗管理などの機能を提供します。

## セットアップ手順

### 1. リポジトリのクローン
```bash
git clone https://github.com/oky-ogura/codemon.git
cd codemon/appproject
```

### 2. 仮想環境の作成と有効化
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

### 3. 依存関係のインストール
```bash
pip install -r requirements.txt
```

### 4. 環境変数の設定
```bash
cp .env.example .env
```
`.env`ファイルを編集して、データベース接続情報を設定してください。

### 5. PostgreSQLデータベースの準備

#### PostgreSQLのインストール
- [PostgreSQL公式サイト](https://www.postgresql.org/download/)からダウンロード・インストール

#### データベースの作成
```sql
-- PostgreSQLに接続
psql -U postgres

-- データベース作成
CREATE DATABASE codemon;

-- ユーザー作成（オプション）
CREATE USER codemon_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE codemon TO codemon_user;
```

#### テーブルの作成
```powershell
# PostgreSQLのパスワード設定（例）
$env:PGPASSWORD = 'your_password'

# 各テーブルのSQLファイルを実行
& 'C:\Program Files\PostgreSQL\17\bin\psql.exe' -h localhost -U postgres -d codemon -f 'sql\create_account.sql'
& 'C:\Program Files\PostgreSQL\17\bin\psql.exe' -h localhost -U postgres -d codemon -f 'sql\create_ai_config.sql'
& 'C:\Program Files\PostgreSQL\17\bin\psql.exe' -h localhost -U postgres -d codemon -f 'sql\create_system.sql'
& 'C:\Program Files\PostgreSQL\17\bin\psql.exe' -h localhost -U postgres -d codemon -f 'sql\create_algorithm.sql'
& 'C:\Program Files\PostgreSQL\17\bin\psql.exe' -h localhost -U postgres -d codemon -f 'sql\create_checklist.sql'
& 'C:\Program Files\PostgreSQL\17\bin\psql.exe' -h localhost -U postgres -d codemon -f 'sql\create_group.sql'
& 'C:\Program Files\PostgreSQL\17\bin\psql.exe' -h localhost -U postgres -d codemon -f 'sql\create_group_member.sql'
& 'C:\Program Files\PostgreSQL\17\bin\psql.exe' -h localhost -U postgres -d codemon -f 'sql\create_chat_history.sql'
& 'C:\Program Files\PostgreSQL\17\bin\psql.exe' -h localhost -U postgres -d codemon -f 'sql\create_ai_learning.sql'
& 'C:\Program Files\PostgreSQL\17\bin\psql.exe' -h localhost -U postgres -d codemon -f 'sql\create_ai_detail.sql'

# 環境変数を削除
Remove-Item Env:PGPASSWORD
```

### 6. Djangoマイグレーション
```bash
python manage.py makemigrations
python manage.py migrate
```

### 7. スーパーユーザーの作成
```bash
python manage.py createsuperuser
```

### 8. サーバーの起動
```bash
python manage.py runserver
```

## データベース構造

### 主要テーブル
- `account` - ユーザーアカウント管理
- `ai_config` - AI設定管理
- `ai_detail` - AI詳細設定（外見、性格など）
- `group` - グループ管理
- `group_member` - グループメンバー管理
- `chat_history` - チャット履歴
- `ai_learning` - AI学習データ
- `system` - システム設定
- `algorithm` - アルゴリズム管理
- `checklist` - チェックリスト管理

## 環境変数

### 必須設定
- `DB_NAME` - データベース名
- `DB_USER` - データベースユーザー名
- `DB_PASSWORD` - データベースパスワード
- `DB_HOST` - データベースホスト（通常はlocalhost）
- `DB_PORT` - データベースポート（通常は5432）
- `SECRET_KEY` - Django秘密鍵

## 開発ガイドライン

### PostgreSQL接続設定の統一
チーム開発時は以下の点を統一してください：

1. **データベース名**: `codemon`
2. **ポート番号**: `5432`（PostgreSQLデフォルト）
3. **文字エンコーディング**: `UTF-8`
4. **タイムゾーン**: `Asia/Tokyo`

### 個人設定が異なる項目
以下は各開発者の環境に応じて`.env`ファイルで設定：

- データベースパスワード
- ホスト名（ローカル開発では通常localhost）
- ユーザー名（postgres または個別ユーザー）

## トラブルシューティング

### PostgreSQL接続エラー
1. PostgreSQLサービスが起動しているか確認
2. `.env`ファイルの接続情報が正しいか確認
3. データベースが作成されているか確認

### マイグレーションエラー
```bash
# マイグレーションファイルの削除（必要に応じて）
find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
find . -path "*/migrations/*.pyc" -delete

# 新しいマイグレーション作成
python manage.py makemigrations
python manage.py migrate
```

## ライセンス
このプロジェクトはMITライセンスの下で公開されています。