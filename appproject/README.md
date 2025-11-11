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
# 基本パッケージのインストール
pip install -r requirements.txt

# WebSocket関連パッケージのインストール
pip install channels daphne channels-redis httpx twisted[tls,http2]
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

### 8. Redisサーバーのセットアップ

WebSocketのメッセージブローカーとしてRedisを使用します：

#### Windowsの場合：
1. [Windows Subsystem for Linux (WSL2)](https://docs.microsoft.com/ja-jp/windows/wsl/install)をインストール
2. WSL2でRedisをインストール：
```bash
sudo apt update
sudo apt install redis-server
sudo service redis-server start
```

#### macOS/Linuxの場合：
```bash
# macOS (Homebrew)
brew install redis
brew services start redis

# Ubuntu/Debian
sudo apt update
sudo apt install redis-server
sudo systemctl start redis-server
```

### 9. メディアファイル設定

1. プロジェクトルートに`media`ディレクトリを作成：
```bash
mkdir media
```

2. `.env`ファイルにメディア設定を追加：
```ini
MEDIA_ROOT=media/
MEDIA_URL=/media/
```

### 10. サーバーの起動

#### 開発用サーバー（WebSocket非対応）
```bash
python manage.py runserver
```

#### 本番用サーバー（WebSocket対応）
```bash
# Windows PowerShell
$env:PYTHONPATH = 'path/to/your/project'
$env:DJANGO_LOG_LEVEL = 'DEBUG'
daphne -v 3 -b 127.0.0.1 -p 8001 --access-log - --ping-interval 20 appproject.asgi:application

# macOS/Linux
export PYTHONPATH=/path/to/your/project
export DJANGO_LOG_LEVEL=DEBUG
daphne -v 3 -b 127.0.0.1 -p 8001 --access-log - --ping-interval 20 appproject.asgi:application
```

## データベース構造

### 主要テーブル
- `account` - ユーザーアカウント管理
  - アバター画像保存機能
  - ユーザー種別（教師/学生）
- `ai_config` - AI設定管理
- `ai_detail` - AI詳細設定（外見、性格など）
- `group` - グループ管理
- `group_member` - グループメンバー管理
- `chat_thread` - チャットスレッド（投函ボックス）管理
  - 公開範囲設定（クラス/グループ）
- `chat_message` - チャットメッセージ管理
  - 本文、送信者、タイムスタンプ
  - 削除フラグと削除者情報
- `chat_attachment` - 添付ファイル管理
  - ファイルパス、MIME type
  - アップロード日時
- `read_receipt` - 既読管理
  - メッセージID、読者ID、既読日時
- `chat_score` - メッセージ評価管理
  - 点数、コメント、評価者
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
- `MEDIA_ROOT` - メディアファイルの保存ディレクトリ（例：media/）
- `MEDIA_URL` - メディアファイルのURL（例：/media/）

### チャット機能の設定
- `REDIS_HOST` - Redisホスト（デフォルト：localhost）
- `REDIS_PORT` - Redisポート（デフォルト：6379）
- `REDIS_DB` - Redis DB番号（デフォルト：0）
- `AI_API_KEY` - OpenAI APIキー（AIチャット応答機能を使用する場合）
- `AI_MODEL` - 使用するAIモデル（デフォルト：gpt-3.5-turbo）

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

### WebSocket接続エラー
1. Redisサーバーが起動しているか確認：
```bash
# Windows WSL2
sudo service redis-server status

# macOS
brew services list | grep redis

# Linux
sudo systemctl status redis-server
```

2. Daphneサーバーのログを確認：
```bash
# デバッグモードで起動
daphne -v 3 -b 127.0.0.1 -p 8001 --access-log - appproject.asgi:application
```

3. WebSocket接続設定を確認：
- `ws://`または`wss://`プロトコルを使用しているか
- ポート番号が正しいか
- URLパスが`/ws/chat/<thread_id>/`の形式か

### メディアファイルアクセスエラー
1. `MEDIA_ROOT`ディレクトリが存在し、書き込み権限があるか確認
2. `urls.py`でメディアファイルのURLパターンが正しく設定されているか確認
3. アップロードされたファイルのパーミッションを確認

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