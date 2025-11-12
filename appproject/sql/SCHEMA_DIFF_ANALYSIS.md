# データベーススキーマ差分分析

## 実施日: 2025-11-11

## 分析対象
- 実テーブル: PostgreSQL codemon データベース (public スキーマ)
- Djangoモデル: codemon/models.py, accounts/models.py

---

## 差分サマリー

### 1. account テーブル
**現状 (SQL):**
- user_id (PK, INTEGER, シーケンス20000001~)
- user_name, email, password, account_type, age, created_at, group_id
- type (VARCHAR(20), NULL可) ← 既に追加済み

**Djangoモデル (accounts/models.py):**
```python
user_id (BigAutoField, PK)
user_name, email, password, age, account_type, created_at
```

**差分:** なし（type列は互換のため追加済み）

---

### 2. group テーブル
**現状 (SQL):**
- group_id (PK, INTEGER, シーケンス7000001~)
- group_name, user_id, password, created_at, updated_at

**Djangoモデル (codemon/models.py Group):**
```python
group_id (BigAutoField, PK)
group_name (CharField 50)
description (TextField, NULL可)
owner (ForeignKey to Account, NULL可)  # owner_id として参照
members (ManyToManyField through GroupMember)
created_at, updated_at (auto_now_add, auto_now)
is_active (BooleanField, default=True)
```

**不足カラム:**
1. `description` TEXT NULL
2. `owner_id` INTEGER NULL (user_idとは別。owner は管理者アカウント)
3. `is_active` BOOLEAN NOT NULL DEFAULT TRUE

**備考:**
- 既存の `user_id` と `password` は保持（他の作業に影響させない）
- `owner_id` を追加し、FK制約は後から付与可能

---

### 3. group_member テーブル
**現状 (SQL):**
- id (PK, INTEGER, シーケンス)
- group_id (FK to group), member_user_id (FK to account), role, created_at
- UNIQUE(group_id, member_user_id)

**Djangoモデル (codemon/models.py GroupMember):**
```python
id (BigAutoField, PK)
group (ForeignKey to Group)  # group_id
member (ForeignKey to Account)  # member_id として参照（member_user_id ではない）
role (CharField 20, choices=['owner','teacher','student'], default='student')
joined_at (DateTimeField, auto_now_add)
is_active (BooleanField, default=True)
UNIQUE(group, member)
```

**不足カラム:**
1. `member_id` INTEGER (member_user_idの別名またはコピー。FKはmemberに向く)
2. `joined_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
3. `is_active` BOOLEAN NOT NULL DEFAULT TRUE

**備考:**
- member_user_id は既存データで使用中。member_id を追加して同期させる
- UNIQUE制約は (group_id, member_id) に変更または追加

---

### 4. checklist / checklist_item / algorithm / system / ai_config / ai_detail / ai_learning / chat_history
**現状:** すべてモデルと一致またはモデルが使わない追加カラムあり
**差分:** なし（コード側は追加カラムを無視するため互換性あり）

---

### 5. 未作成テーブル（Djangoモデルに存在）
**ChatThread, ChatMessage, ChatAttachment, ReadReceipt, ChatScore:**
- models.py で定義されているが、PostgreSQLに未作成
- これらはチャット機能（スレッド・メッセージ・添付・既読・採点）を提供
- db_table名: chat_thread, chat_message, chat_attachment, chat_read_receipt, chat_score

**AIConversation, AIMessage:**
- models.py で定義されているが、PostgreSQLに未作成
- AI会話履歴を管理
- db_table名: codemon_aiconversation, codemon_aimessage (デフォルトテーブル名)

---

## ALTER戦略

### 原則
1. **既存データ保持**: 既存カラム(user_id, password, member_user_id等)は削除しない
2. **後方互換**: 新カラムはNULL可または DEFAULT値付きで追加
3. **段階的移行**: まずカラム追加→データ移行→制約追加の順
4. **コメント充実**: 各SQL文に用途・理由を明記

### 実施順序
1. group テーブル拡張（description, owner_id, is_active追加）
2. group_member テーブル拡張（member_id, joined_at, is_active追加）
3. チャット系5テーブル新規作成
4. AI会話系2テーブル新規作成
5. seedデータ更新（新カラム・新テーブル対応）

---

## 次ステップ
- `sql/extend_existing_tables.sql` にALTER文作成
- `sql/create_chat_tables.sql` に新規テーブル作成
- `sql/create_ai_conversation_tables.sql` に新規テーブル作成
- `sql/seed_data.sql` 更新（新カラム対応）
