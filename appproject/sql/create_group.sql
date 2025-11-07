-- ...existing code...
-- PostgreSQL: create_group.sql
-- グループ管理テーブル定義（設計書に準拠）
-- 主キーは先頭桁を7で固定（例: 7000001 から開始）

-- 1) シーケンス（group_id を 7000001 から開始）
CREATE SEQUENCE IF NOT EXISTS group_group_id_seq
    START WITH 7000001
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

-- 2) テーブル作成（カラム属性は設計書に準拠）
CREATE TABLE IF NOT EXISTS "group" (
    group_id INTEGER NOT NULL PRIMARY KEY DEFAULT nextval('group_group_id_seq'),
    group_name VARCHAR(50) NOT NULL,
    user_id INTEGER NOT NULL,
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 3) シーケンス所有者設定
ALTER SEQUENCE group_group_id_seq OWNED BY "group".group_id;

-- 4) インデックス（検索性能向上）
CREATE INDEX IF NOT EXISTS idx_group_user_id ON "group"(user_id);
CREATE INDEX IF NOT EXISTS idx_group_name ON "group"(group_name);


-- 5) updated_at 自動更新トリガー
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 既存トリガーがあれば削除してから作成
DROP TRIGGER IF EXISTS update_group_updated_at ON "group";
CREATE TRIGGER update_group_updated_at
    BEFORE UPDATE ON "group"
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 7) コメント（設計書の説明を反映）
COMMENT ON TABLE "group" IS 'グループ管理テーブル - 学生のグループ分けを管理';
COMMENT ON COLUMN "group".group_id IS 'グループID - 主キー、7から始まる一意な識別子';
COMMENT ON COLUMN "group".group_name IS 'グループ名 - 最大50文字';
COMMENT ON COLUMN "group".user_id IS '作成者ID - account.user_id を参照する外部キー';
COMMENT ON COLUMN "group".created_at IS '作成日時 - レコード作成時のタイムスタンプ';
COMMENT ON COLUMN "group".updated_at IS '更新日時 - レコード更新時のタイムスタンプ（自動更新）';
-- ...existing code...