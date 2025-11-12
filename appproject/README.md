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

## データベーススキーマ

### テーブル一覧
Codemonシステムは18個のPostgreSQLテーブルで構成されています。以下、カテゴリ別に説明します。

---

### 1. アカウント管理

#### `account` テーブル
ユーザー（教師・学生）の基本情報を管理。

| カラム名 | 型 | NULL | デフォルト | 説明 |
|---------|---|------|----------|------|
| user_id | INTEGER | NO | - | 主キー（20000001〜） |
| user_name | VARCHAR(100) | NO | - | ユーザー名 |
| user_mail | VARCHAR(150) | NO | - | メールアドレス（ログインID） |
| password | VARCHAR(128) | NO | - | ハッシュ化パスワード |
| account_type | VARCHAR(10) | NO | - | 'teacher'または'student' |
| type | VARCHAR(10) | YES | NULL | account_typeのコピー（views互換用） |
| avatar | VARCHAR(100) | YES | NULL | アバター画像パス |

**サンプルデータ**
```sql
INSERT INTO account (user_id, user_name, user_mail, password, account_type, type) VALUES
(20000001, '山田太郎', 'teacher@example.com', 'pbkdf2_...', 'teacher', 'teacher'),
(20000002, '佐藤花子', 'student1@example.com', 'pbkdf2_...', 'student', 'student');
```

---

### 2. グループ管理

#### `group` テーブル
クラスやプロジェクトグループの情報を管理。

| カラム名 | 型 | NULL | デフォルト | 説明 |
|---------|---|------|----------|------|
| group_id | INTEGER | NO | - | 主キー（7000001〜） |
| group_name | VARCHAR(100) | NO | - | グループ名 |
| user_id | INTEGER | YES | NULL | 作成者ID（歴史的理由で保持） |
| password | VARCHAR(100) | YES | NULL | 参加パスワード（任意） |
| description | TEXT | YES | NULL | グループ説明 |
| owner_id | INTEGER | YES | NULL | 所有者ID（FK: account.user_id） |
| is_active | BOOLEAN | NO | TRUE | アクティブフラグ |

**外部キー**
- `owner_id` → `account(user_id)` ON DELETE SET NULL

**サンプルデータ**
```sql
INSERT INTO "group" (group_id, group_name, user_id, password, description, owner_id, is_active) VALUES
(7000001, 'プログラミング基礎クラスA', 20000001, 'class2024', 'プログラミング基礎クラスA - 2024年度', 20000001, TRUE);
```

#### `group_member` テーブル
グループメンバーシップを管理（多対多関係）。

| カラム名 | 型 | NULL | デフォルト | 説明 |
|---------|---|------|----------|------|
| group_member_id | INTEGER | NO | - | 主キー |
| group_id | INTEGER | NO | - | グループID（FK: group.group_id） |
| member_user_id | INTEGER | NO | - | メンバーユーザーID（歴史的理由で保持） |
| member_id | INTEGER | NO | - | メンバーID（FK: account.user_id） |
| joined_at | TIMESTAMP | NO | CURRENT_TIMESTAMP | 参加日時 |
| is_active | BOOLEAN | NO | TRUE | アクティブフラグ |

**外部キー**
- `group_id` → `group(group_id)` ON DELETE CASCADE
- `member_id` → `account(user_id)` ON DELETE CASCADE

**制約**
- UNIQUE(group_id, member_id) - 重複登録防止

---

### 3. チャット機能

#### `chat_thread` テーブル
チャットスレッド（投函ボックス）を管理。課題提出や質問用。

| カラム名 | 型 | NULL | デフォルト | 説明 |
|---------|---|------|----------|------|
| thread_id | BIGSERIAL | NO | - | 主キー |
| title | VARCHAR(200) | NO | - | スレッドタイトル |
| description | TEXT | YES | NULL | スレッド説明 |
| created_by_id | INTEGER | NO | - | 作成者ID（FK: account.user_id） |
| group_id | INTEGER | YES | NULL | 対象グループID（FK: group.group_id） |
| is_active | BOOLEAN | NO | TRUE | アクティブフラグ |
| created_at | TIMESTAMP | NO | CURRENT_TIMESTAMP | 作成日時 |

**外部キー**
- `created_by_id` → `account(user_id)` ON DELETE CASCADE
- `group_id` → `group(group_id)` ON DELETE SET NULL

**サンプルデータ**
```sql
INSERT INTO chat_thread (title, description, created_by_id, group_id, is_active) VALUES
('第1回課題提出スレッド', '第1回プログラミング課題をこちらに提出してください', 20000001, 7000001, TRUE);
```

#### `chat_message` テーブル
チャットメッセージ本体を管理。

| カラム名 | 型 | NULL | デフォルト | 説明 |
|---------|---|------|----------|------|
| message_id | BIGSERIAL | NO | - | 主キー |
| thread_id | BIGINT | NO | - | スレッドID（FK: chat_thread.thread_id） |
| sender_id | INTEGER | NO | - | 送信者ID（FK: account.user_id） |
| content | TEXT | NO | - | メッセージ本文 |
| created_at | TIMESTAMP | NO | CURRENT_TIMESTAMP | 送信日時 |
| is_deleted | BOOLEAN | NO | FALSE | 削除フラグ |

**外部キー**
- `thread_id` → `chat_thread(thread_id)` ON DELETE CASCADE
- `sender_id` → `account(user_id)` ON DELETE CASCADE

**インデックス**
- `idx_chat_message_thread_id` ON thread_id
- `idx_chat_message_sender_id` ON sender_id
- `idx_chat_message_created_at` ON created_at

#### `chat_attachment` テーブル
メッセージ添付ファイルを管理。

| カラム名 | 型 | NULL | デフォルト | 説明 |
|---------|---|------|----------|------|
| attachment_id | BIGSERIAL | NO | - | 主キー |
| message_id | BIGINT | NO | - | メッセージID（FK: chat_message.message_id） |
| file | VARCHAR(100) | NO | - | ファイルパス |
| uploaded_at | TIMESTAMP | NO | CURRENT_TIMESTAMP | アップロード日時 |

**外部キー**
- `message_id` → `chat_message(message_id)` ON DELETE CASCADE

#### `chat_read_receipt` テーブル
メッセージ既読状態を管理。

| カラム名 | 型 | NULL | デフォルト | 説明 |
|---------|---|------|----------|------|
| id | BIGSERIAL | NO | - | 主キー |
| message_id | BIGINT | NO | - | メッセージID（FK: chat_message.message_id） |
| reader_id | INTEGER | NO | - | 既読者ID（FK: account.user_id） |
| read_at | TIMESTAMP | NO | CURRENT_TIMESTAMP | 既読日時 |

**外部キー**
- `message_id` → `chat_message(message_id)` ON DELETE CASCADE
- `reader_id` → `account(user_id)` ON DELETE CASCADE

**制約**
- UNIQUE(message_id, reader_id) - 重複既読防止

#### `chat_score` テーブル
メッセージまたはスレッドへの評価を管理。教師が課題採点に使用。

| カラム名 | 型 | NULL | デフォルト | 説明 |
|---------|---|------|----------|------|
| id | BIGSERIAL | NO | - | 主キー |
| message_id | BIGINT | YES | NULL | 評価対象メッセージID（FK: chat_message.message_id） |
| thread_id | BIGINT | YES | NULL | 評価対象スレッドID（FK: chat_thread.thread_id） |
| scorer_id | INTEGER | NO | - | 評価者ID（FK: account.user_id） |
| score | INTEGER | NO | - | 点数 |
| comment | TEXT | YES | NULL | コメント |
| scored_at | TIMESTAMP | NO | CURRENT_TIMESTAMP | 評価日時 |

**外部キー**
- `message_id` → `chat_message(message_id)` ON DELETE CASCADE
- `thread_id` → `chat_thread(thread_id)` ON DELETE CASCADE
- `scorer_id` → `account(user_id)` ON DELETE CASCADE

**制約**
- CHECK ((message_id IS NOT NULL AND thread_id IS NULL) OR (message_id IS NULL AND thread_id IS NOT NULL)) - XOR制約

**サンプルデータ**
```sql
INSERT INTO chat_score (message_id, scorer_id, score, comment) VALUES
(1, 20000001, 85, 'よくできています。関数の使い方が適切です。');
```

---

### 4. AI設定・学習

#### `ai_config` テーブル
AIキャラクター（codemon, usagi, nekoなど）の基本設定。

| カラム名 | 型 | NULL | デフォルト | 説明 |
|---------|---|------|----------|------|
| ai_id | INTEGER | NO | - | 主キー（3000001〜） |
| ai_name | VARCHAR(100) | NO | - | AI名（表示名） |
| character_id | VARCHAR(32) | NO | - | キャラクターID（'usagi', 'neko'等） |

**サンプルデータ**
```sql
INSERT INTO ai_config (ai_id, ai_name, character_id) VALUES
(3000001, 'コードもん', 'codemon'),
(3000002, 'ウサギ', 'usagi'),
(3000003, 'ネコ', 'neko');
```

#### `ai_detail` テーブル
AIキャラクターの詳細設定（外見、性格、話し方など）。

| カラム名 | 型 | NULL | デフォルト | 説明 |
|---------|---|------|----------|------|
| ai_detail_id | INTEGER | NO | - | 主キー |
| ai_id | INTEGER | NO | - | AI設定ID（FK: ai_config.ai_id） |
| personality | TEXT | YES | NULL | 性格設定 |
| appearance | TEXT | YES | NULL | 外見設定 |
| speech_style | TEXT | YES | NULL | 話し方設定 |

**外部キー**
- `ai_id` → `ai_config(ai_id)` ON DELETE CASCADE

#### `ai_learning` テーブル
AI学習データ（システムプロンプトやコンテキスト）を管理。

| カラム名 | 型 | NULL | デフォルト | 説明 |
|---------|---|------|----------|------|
| ai_learning_id | INTEGER | NO | - | 主キー |
| ai_id | INTEGER | NO | - | AI設定ID（FK: ai_config.ai_id） |
| learning_data | TEXT | YES | NULL | 学習データ（システムプロンプト等） |

**外部キー**
- `ai_id` → `ai_config(ai_id)` ON DELETE CASCADE

#### `codemon_aiconversation` テーブル
AIとのチャットセッション（会話履歴の親）を管理。

| カラム名 | 型 | NULL | デフォルト | 説明 |
|---------|---|------|----------|------|
| id | BIGSERIAL | NO | - | 主キー |
| user_id | INTEGER | NO | - | ユーザーID（FK: account.user_id） |
| character_id | VARCHAR(32) | NO | - | AIキャラクターID（'usagi', 'kitsune'等） |
| title | VARCHAR(200) | YES | NULL | 会話タイトル |
| created_at | TIMESTAMP | NO | CURRENT_TIMESTAMP | 作成日時 |

**外部キー**
- `user_id` → `account(user_id)` ON DELETE CASCADE

**サンプルデータ**
```sql
INSERT INTO codemon_aiconversation (user_id, character_id, title) VALUES
(20000002, 'usagi', 'プログラミング学習相談 - 2025-01-11');
```

#### `codemon_aimessage` テーブル
AIとのチャットメッセージ（1会話内の各発言）を管理。

| カラム名 | 型 | NULL | デフォルト | 説明 |
|---------|---|------|----------|------|
| id | BIGSERIAL | NO | - | 主キー |
| conversation_id | BIGINT | NO | - | 会話ID（FK: codemon_aiconversation.id） |
| role | VARCHAR(20) | NO | - | 発言者ロール（'user', 'assistant', 'system'） |
| content | TEXT | NO | - | メッセージ本文 |
| tokens | INTEGER | YES | NULL | トークン数（API課金計算用） |
| created_at | TIMESTAMP | NO | CURRENT_TIMESTAMP | 作成日時 |

**外部キー**
- `conversation_id` → `codemon_aiconversation(id)` ON DELETE CASCADE

**制約**
- CHECK (role IN ('user', 'assistant', 'system'))

**サンプルデータ**
```sql
INSERT INTO codemon_aimessage (conversation_id, role, content, tokens) VALUES
(1, 'user', 'Pythonのfor文について教えてください', 150),
(1, 'assistant', 'Pythonのfor文は...（詳細説明）', 350);
```

---

### 5. 学習進捗・チェックリスト

#### `chat_history` テーブル
旧チャット履歴（後方互換用、現在は`chat_thread`/`chat_message`に移行）。

| カラム名 | 型 | NULL | デフォルト | 説明 |
|---------|---|------|----------|------|
| chat_id | INTEGER | NO | - | 主キー |
| user_id | INTEGER | NO | - | ユーザーID（FK: account.user_id） |
| ai_id | INTEGER | NO | - | AI設定ID（FK: ai_config.ai_id） |
| chat_text | TEXT | YES | NULL | チャット内容 |

**外部キー**
- `user_id` → `account(user_id)` ON DELETE CASCADE
- `ai_id` → `ai_config(ai_id)` ON DELETE CASCADE

#### `checklist` テーブル
学習チェックリスト（カテゴリレベル）を管理。

| カラム名 | 型 | NULL | デフォルト | 説明 |
|---------|---|------|----------|------|
| checklist_id | INTEGER | NO | - | 主キー（6000001〜） |
| user_id | INTEGER | NO | - | ユーザーID（FK: account.user_id） |
| algorithm_id | INTEGER | NO | - | アルゴリズムID（FK: algorithm.algorithm_id） |

**外部キー**
- `user_id` → `account(user_id)` ON DELETE CASCADE
- `algorithm_id` → `algorithm(algorithm_id)` ON DELETE CASCADE

#### `checklist_item` テーブル
個別チェック項目を管理。

| カラム名 | 型 | NULL | デフォルト | 説明 |
|---------|---|------|----------|------|
| item_id | SERIAL | NO | - | 主キー |
| checklist_id | INTEGER | NO | - | チェックリストID（FK: checklist.checklist_id） |
| item_name | VARCHAR(255) | NO | - | 項目名 |
| is_checked | BOOLEAN | NO | FALSE | チェック状態 |
| checked_at | TIMESTAMP | YES | NULL | チェック日時 |

**外部キー**
- `checklist_id` → `checklist(checklist_id)` ON DELETE CASCADE

**サンプルデータ**
```sql
INSERT INTO checklist_item (checklist_id, item_name, is_checked) VALUES
(6000001, 'バブルソートのアルゴリズムを理解する', FALSE),
(6000001, 'バブルソートをPythonで実装する', FALSE);
```

---

### 6. システム設定・アルゴリズム

#### `system` テーブル
システムレベルの設定を管理。

| カラム名 | 型 | NULL | デフォルト | 説明 |
|---------|---|------|----------|------|
| system_id | INTEGER | NO | - | 主キー（4000001〜） |
| system_name | VARCHAR(100) | NO | - | システム名 |

**サンプルデータ**
```sql
INSERT INTO system (system_id, system_name) VALUES
(4000001, 'Codemon Learning Platform v1.0');
```

#### `algorithm` テーブル
学習対象のアルゴリズムを管理。

| カラム名 | 型 | NULL | デフォルト | 説明 |
|---------|---|------|----------|------|
| algorithm_id | INTEGER | NO | - | 主キー（5000001〜） |
| algorithm_name | VARCHAR(100) | NO | - | アルゴリズム名 |
| system_id | INTEGER | NO | - | システムID（FK: system.system_id） |

**外部キー**
- `system_id` → `system(system_id)` ON DELETE CASCADE

**サンプルデータ**
```sql
INSERT INTO algorithm (algorithm_id, algorithm_name, system_id) VALUES
(5000001, 'バブルソート', 4000001),
(5000002, 'クイックソート', 4000001);
```

---

### ID範囲の設計思想

各テーブルで異なるID範囲を使用し、ダンプ/復元時の衝突を回避：

| テーブル | ID範囲 | シーケンス開始値 |
|---------|-------|--------------|
| account | 20000001〜 | 20000001 |
| ai_config | 3000001〜 | 3000001 |
| algorithm | 5000001〜 | 5000001 |
| checklist | 6000001〜 | 6000001 |
| group | 7000001〜 | 7000001 |
| system | 4000001〜 | 4000001 |
| chat_* / codemon_* | 1〜 | 1（BIGSERIAL） |

---

### 主要なリレーションシップ

```
account (1) ─── (N) group_member (N) ─── (1) group
   │                                         │
   │                                         │
   ├──(1)─(N) chat_thread (1)──(N) chat_message
   │                                         │
   │                                         ├──(1)─(N) chat_attachment
   │                                         ├──(1)─(N) chat_read_receipt
   │                                         └──(1)─(N) chat_score
   │
   ├──(1)─(N) codemon_aiconversation (1)─(N) codemon_aimessage
   │
   └──(1)─(N) checklist (N)───(1) algorithm (N)───(1) system
              │
              └──(1)─(N) checklist_item

ai_config (1)───(1) ai_detail
   │
   ├──(1)─(N) ai_learning
   └──(1)─(N) chat_history
```

**凡例**
- `(1)` - 1レコード
- `(N)` - 複数レコード
- `───` - 外部キー関係
- `ON DELETE CASCADE` - 親削除時に子も削除
- `ON DELETE SET NULL` - 親削除時に子はNULL

---

### よく使うクエリ例

#### 1. グループメンバー一覧取得
```sql
SELECT 
    g.group_name,
    a.user_name,
    a.user_mail,
    gm.joined_at
FROM group_member gm
JOIN "group" g ON gm.group_id = g.group_id
JOIN account a ON gm.member_id = a.user_id
WHERE g.group_id = 7000001 AND gm.is_active = TRUE
ORDER BY gm.joined_at;
```

#### 2. スレッド内の未読メッセージ数取得
```sql
SELECT 
    cm.message_id,
    cm.content,
    a.user_name AS sender_name
FROM chat_message cm
JOIN account a ON cm.sender_id = a.user_id
LEFT JOIN chat_read_receipt crr ON cm.message_id = crr.message_id AND crr.reader_id = 20000002
WHERE cm.thread_id = 1 
  AND cm.is_deleted = FALSE
  AND crr.id IS NULL
ORDER BY cm.created_at;
```

#### 3. 課題の点数一覧
```sql
SELECT 
    cm.content AS submission,
    a_sender.user_name AS student_name,
    cs.score,
    cs.comment,
    a_scorer.user_name AS teacher_name
FROM chat_score cs
JOIN chat_message cm ON cs.message_id = cm.message_id
JOIN account a_sender ON cm.sender_id = a_sender.user_id
JOIN account a_scorer ON cs.scorer_id = a_scorer.user_id
WHERE cm.thread_id = 1
ORDER BY cs.score DESC;
```

#### 4. AIチャット履歴取得
```sql
SELECT 
    ac.title,
    am.role,
    am.content,
    am.created_at
FROM codemon_aimessage am
JOIN codemon_aiconversation ac ON am.conversation_id = ac.id
WHERE ac.user_id = 20000002 AND ac.character_id = 'usagi'
ORDER BY am.created_at;
```

---

### データベースメンテナンス

#### バックアップ
```bash
# データベース全体
pg_dump -U postgres -d codemon > backup_$(date +%Y%m%d).sql

# 特定テーブルのみ
pg_dump -U postgres -d codemon -t account -t "group" > backup_accounts_groups.sql
```

#### 復元
```bash
# データベース全体
psql -U postgres -d codemon < backup_20250111.sql

# 特定テーブル
psql -U postgres -d codemon < backup_accounts_groups.sql
```

#### シーケンスのリセット
```sql
-- 全シーケンスを最大IDに同期
SELECT setval('account_user_id_seq', (SELECT MAX(user_id) FROM account));
SELECT setval('group_group_id_seq', (SELECT MAX(group_id) FROM "group"));
SELECT setval('chat_thread_thread_id_seq', (SELECT MAX(thread_id) FROM chat_thread));
```

---

### スキーマ変更履歴

#### 2025-01-11: 完全スキーマ整備
- `group`テーブルに`description`, `owner_id`, `is_active`カラムを追加
- `group_member`テーブルに`member_id`, `joined_at`, `is_active`カラムを追加
- チャット機能5テーブル新規作成（`chat_thread`, `chat_message`, `chat_attachment`, `chat_read_receipt`, `chat_score`）
- AI会話履歴2テーブル新規作成（`codemon_aiconversation`, `codemon_aimessage`）
- `account.type`カラム追加（views.py互換性のため）
- 全テーブルにCOMMENT追加（可読性向上）
- 完全なサンプルデータ投入（開発・テスト用）

詳細は`sql/SCHEMA_DIFF_ANALYSIS.md`を参照してください。

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