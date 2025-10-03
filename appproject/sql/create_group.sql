-- PostgreSQL: create_group.sql
-- Creates sequence and table `group` in the `codemon` database.
-- Group management table for organizing students into groups

-- 1) Create sequence starting at 7000001 for group_id (最初の桁を7で固定)
CREATE SEQUENCE IF NOT EXISTS group_group_id_seq
    START WITH 7000001
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

-- 2) Create group table
CREATE TABLE IF NOT EXISTS "group" (
    group_id INTEGER NOT NULL PRIMARY KEY DEFAULT nextval('group_group_id_seq'),
    group_name VARCHAR(50) NOT NULL,
    user_id INTEGER NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 3) Set sequence ownership to column
ALTER SEQUENCE group_group_id_seq OWNED BY "group".group_id;

-- 4) Create index for performance
CREATE INDEX IF NOT EXISTS idx_group_user_id ON "group"(user_id);
CREATE INDEX IF NOT EXISTS idx_group_name ON "group"(group_name);

-- 5) Create foreign key constraint to account table
-- Note: Uncomment when account table is created
-- ALTER TABLE "group" ADD CONSTRAINT fk_group_user_id 
-- FOREIGN KEY (user_id) REFERENCES account(user_id) ON DELETE CASCADE;

-- 6) Create trigger for automatic updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_group_updated_at 
    BEFORE UPDATE ON "group" 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 7) Insert sample data (optional)
-- INSERT INTO "group" (group_name, user_id) 
-- VALUES ('A班', 20000001);

-- 8) Comments for table and columns
COMMENT ON TABLE "group" IS 'グループ管理テーブル - 学生のグループ分けを管理';
COMMENT ON COLUMN "group".group_id IS 'グループID - 主キー、7から始まる一意な識別子';
COMMENT ON COLUMN "group".group_name IS 'グループ名 - 最大50文字';
COMMENT ON COLUMN "group".user_id IS 'ユーザーID - アカウントテーブルを参照する外部キー';
COMMENT ON COLUMN "group".created_at IS '作成日時 - レコード作成時のタイムスタンプ';
COMMENT ON COLUMN "group".updated_at IS '更新日時 - レコード更新時のタイムスタンプ（自動更新）';