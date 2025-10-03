-- PostgreSQL: create_group_member.sql
-- Creates table `group_member` in the `codemon` database.
-- Group member management table for managing students in groups

-- 1) Create group_member table
CREATE TABLE IF NOT EXISTS group_member (
    member_id INTEGER NOT NULL,
    group_name VARCHAR(50) NOT NULL,
    user_id INTEGER NOT NULL,
    addition_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (member_id, group_name)
);

-- 2) Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_group_member_group_name ON group_member(group_name);
CREATE INDEX IF NOT EXISTS idx_group_member_user_id ON group_member(user_id);
CREATE INDEX IF NOT EXISTS idx_group_member_addition_at ON group_member(addition_at);

-- 3) Create foreign key constraints
-- Note: Uncomment when group and account tables are created
-- ALTER TABLE group_member ADD CONSTRAINT fk_group_member_group_name 
-- FOREIGN KEY (group_name) REFERENCES "group"(group_name) ON DELETE CASCADE;

-- ALTER TABLE group_member ADD CONSTRAINT fk_group_member_user_id 
-- FOREIGN KEY (user_id) REFERENCES account(user_id) ON DELETE CASCADE;

-- 4) Create trigger function for auto-incrementing member_id within each group
CREATE OR REPLACE FUNCTION get_next_member_id(p_group_name VARCHAR(50))
RETURNS INTEGER AS $$
DECLARE
    next_id INTEGER;
BEGIN
    SELECT COALESCE(MAX(member_id), 0) + 1 
    INTO next_id 
    FROM group_member 
    WHERE group_name = p_group_name;
    
    RETURN next_id;
END;
$$ LANGUAGE plpgsql;

-- 5) Create trigger to auto-assign member_id
CREATE OR REPLACE FUNCTION assign_member_id()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.member_id IS NULL OR NEW.member_id = 0 THEN
        NEW.member_id := get_next_member_id(NEW.group_name);
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_assign_member_id
    BEFORE INSERT ON group_member
    FOR EACH ROW
    EXECUTE FUNCTION assign_member_id();

-- 6) Create unique constraint to prevent duplicate user in same group
ALTER TABLE group_member ADD CONSTRAINT uk_group_member_user_group 
UNIQUE (group_name, user_id);

-- 7) Insert sample data (optional)
-- INSERT INTO group_member (group_name, user_id) VALUES 
-- ('A班', 20000001),
-- ('A班', 20000002),
-- ('B班', 20000003);

-- 8) Comments for table and columns
COMMENT ON TABLE group_member IS 'グループメンバー管理テーブル - グループ内の学生を管理';
COMMENT ON COLUMN group_member.member_id IS 'メンバーID - グループ内で1から連番の識別子';
COMMENT ON COLUMN group_member.group_name IS 'グループ名 - グループテーブルを参照する外部キー';
COMMENT ON COLUMN group_member.user_id IS 'ユーザーID - アカウントテーブルを参照する外部キー';
COMMENT ON COLUMN group_member.addition_at IS '追加日時 - メンバーがグループに追加された日時';