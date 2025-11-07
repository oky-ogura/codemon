-- ...existing code...
-- PostgreSQL: create_group_member.sql
-- グループメンバー管理テーブル - group_id と account.user_id を参照するシンプルな定義

CREATE TABLE IF NOT EXISTS group_member (
    id SERIAL PRIMARY KEY,
    group_id INTEGER NOT NULL,
    member_user_id INTEGER NOT NULL,
    role VARCHAR(50),
    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_gm_group FOREIGN KEY (group_id) REFERENCES "group"(group_id) ON DELETE CASCADE,
    CONSTRAINT fk_gm_user FOREIGN KEY (member_user_id) REFERENCES account(user_id) ON DELETE CASCADE,
    CONSTRAINT uk_group_member_group_member UNIQUE (group_id, member_user_id)
);

-- インデックス
CREATE INDEX IF NOT EXISTS idx_group_member_group_id ON group_member(group_id);
CREATE INDEX IF NOT EXISTS idx_group_member_member_user_id ON group_member(member_user_id);
CREATE INDEX IF NOT EXISTS idx_group_member_created_at ON group_member(created_at);

-- サンプルデータ（必要ならアンコメントして使用）
-- INSERT INTO group_member (group_id, member_user_id, role) VALUES (7000001, 20000001, 'member');

-- コメント
COMMENT ON TABLE group_member IS 'グループメンバー管理テーブル - group_id で "group" を参照、member_user_id で account を参照';
COMMENT ON COLUMN group_member.id IS '主キー - レコード固有のシーケンスID';
COMMENT ON COLUMN group_member.group_id IS 'グループID - "group".group_id を参照';
COMMENT ON COLUMN group_member.member_user_id IS 'メンバーのアカウントID - account.user_id を参照';
COMMENT ON COLUMN group_member.role IS 'メンバーの役割';
COMMENT ON COLUMN group_member.created_at IS '追加日時';
-- ...existing code...