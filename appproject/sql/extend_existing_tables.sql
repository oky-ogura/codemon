-- extend_existing_tables.sql
-- 既存テーブル (group, group_member) にDjangoモデルが必要とするカラムを追加
-- 実行前提: group, group_member, account テーブルが存在
-- 実行後: コード側の参照が安定し、既存データも保持される
--
-- 作成日: 2025-11-11
-- 方針: 既存カラム削除なし、新カラムはNULL可またはDEFAULT付きで安全に追加

SET client_encoding TO 'UTF8';
BEGIN;

-- ========================================
-- 1. group テーブル拡張
-- ========================================
-- Djangoモデル Group に合わせて以下を追加:
--   - description: グループ説明文（NULL可）
--   - owner_id: グループオーナー（管理者アカウント、NULL可）
--   - is_active: アクティブフラグ（デフォルトTRUE）

-- 1-1. description カラム追加（グループ説明文）
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_name='group' AND column_name='description'
  ) THEN
    ALTER TABLE "group" ADD COLUMN description TEXT NULL;
    RAISE NOTICE 'Added column: group.description';
  ELSE
    RAISE NOTICE 'Column already exists: group.description';
  END IF;
END; $$;

-- 1-2. owner_id カラム追加（グループオーナー、user_idとは異なる概念）
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_name='group' AND column_name='owner_id'
  ) THEN
    ALTER TABLE "group" ADD COLUMN owner_id INTEGER NULL;
    RAISE NOTICE 'Added column: group.owner_id';
    
    -- 既存データへのデフォルト設定: user_id をowner_id にコピー（暫定）
    -- 注: user_id とowner_id の意味が異なる場合は手動調整が必要
    UPDATE "group" SET owner_id = user_id WHERE owner_id IS NULL;
    RAISE NOTICE 'Populated group.owner_id from user_id for existing rows';
  ELSE
    RAISE NOTICE 'Column already exists: group.owner_id';
  END IF;
END; $$;

-- 1-3. owner_id に外部キー制約を追加（accountテーブルへの参照）
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.table_constraints
    WHERE table_name='group' AND constraint_name='fk_group_owner'
  ) THEN
    ALTER TABLE "group"
      ADD CONSTRAINT fk_group_owner
      FOREIGN KEY (owner_id) REFERENCES account(user_id) ON DELETE SET NULL;
    RAISE NOTICE 'Added FK constraint: group.owner_id -> account.user_id';
  ELSE
    RAISE NOTICE 'FK constraint already exists: fk_group_owner';
  END IF;
END; $$;

-- 1-4. is_active カラム追加（論理削除フラグ）
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_name='group' AND column_name='is_active'
  ) THEN
    ALTER TABLE "group" ADD COLUMN is_active BOOLEAN NOT NULL DEFAULT TRUE;
    RAISE NOTICE 'Added column: group.is_active (default=TRUE)';
  ELSE
    RAISE NOTICE 'Column already exists: group.is_active';
  END IF;
END; $$;

-- ========================================
-- 2. group_member テーブル拡張
-- ========================================
-- Djangoモデル GroupMember に合わせて以下を追加:
--   - member_id: メンバーアカウントID（member_user_idの別名、FK先変更）
--   - joined_at: 参加日時（デフォルト=現在時刻）
--   - is_active: アクティブフラグ（デフォルトTRUE）

-- 2-1. member_id カラム追加（member_user_idと同じ値を持つ新カラム）
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_name='group_member' AND column_name='member_id'
  ) THEN
    -- まずNULL可で追加
    ALTER TABLE group_member ADD COLUMN member_id INTEGER NULL;
    RAISE NOTICE 'Added column: group_member.member_id';
    
    -- 既存データをmember_user_idからコピー
    UPDATE group_member SET member_id = member_user_id WHERE member_id IS NULL;
    RAISE NOTICE 'Populated group_member.member_id from member_user_id';
    
    -- NOT NULL制約を後付け
    ALTER TABLE group_member ALTER COLUMN member_id SET NOT NULL;
    RAISE NOTICE 'Set NOT NULL on group_member.member_id';
  ELSE
    RAISE NOTICE 'Column already exists: group_member.member_id';
  END IF;
END; $$;

-- 2-2. member_id に外部キー制約を追加
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.table_constraints
    WHERE table_name='group_member' AND constraint_name='fk_gm_member'
  ) THEN
    ALTER TABLE group_member
      ADD CONSTRAINT fk_gm_member
      FOREIGN KEY (member_id) REFERENCES account(user_id) ON DELETE CASCADE;
    RAISE NOTICE 'Added FK constraint: group_member.member_id -> account.user_id';
  ELSE
    RAISE NOTICE 'FK constraint already exists: fk_gm_member';
  END IF;
END; $$;

-- 2-3. joined_at カラム追加（参加日時）
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_name='group_member' AND column_name='joined_at'
  ) THEN
    ALTER TABLE group_member
      ADD COLUMN joined_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP;
    RAISE NOTICE 'Added column: group_member.joined_at (default=CURRENT_TIMESTAMP)';
  ELSE
    RAISE NOTICE 'Column already exists: group_member.joined_at';
  END IF;
END; $$;

-- 2-4. is_active カラム追加（論理削除フラグ）
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_name='group_member' AND column_name='is_active'
  ) THEN
    ALTER TABLE group_member
      ADD COLUMN is_active BOOLEAN NOT NULL DEFAULT TRUE;
    RAISE NOTICE 'Added column: group_member.is_active (default=TRUE)';
  ELSE
    RAISE NOTICE 'Column already exists: group_member.is_active';
  END IF;
END; $$;

-- 2-5. UNIQUE制約を (group_id, member_id) に追加
-- 注: 既存のUNIQUE制約 uk_group_member_group_member は (group_id, member_user_id) を対象
--     新しい制約を追加して、Djangoモデルの unique_together に対応
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.table_constraints
    WHERE table_name='group_member' AND constraint_name='uk_group_member_group_member_id'
  ) THEN
    ALTER TABLE group_member
      ADD CONSTRAINT uk_group_member_group_member_id UNIQUE (group_id, member_id);
    RAISE NOTICE 'Added UNIQUE constraint: group_member(group_id, member_id)';
  ELSE
    RAISE NOTICE 'UNIQUE constraint already exists: uk_group_member_group_member_id';
  END IF;
END; $$;

COMMIT;

-- ========================================
-- 完了メッセージ
-- ========================================
SELECT '既存テーブル拡張が完了しました。' AS status;
SELECT 'group テーブル: description, owner_id, is_active を追加' AS group_changes;
SELECT 'group_member テーブル: member_id, joined_at, is_active を追加' AS group_member_changes;
