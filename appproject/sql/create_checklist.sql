-- SQL: create_checklist.sql
-- Creates sequence and table `checklist` in the `codemon` database.
-- Checklist management table

-- 1) Create sequence starting at 6000001 for checklist_id
CREATE SEQUENCE IF NOT EXISTS checklist_checklist_id_seq
    START WITH 6000001
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

-- 2) Create checklist table
CREATE TABLE IF NOT EXISTS checklist (
    checklist_id INTEGER NOT NULL PRIMARY KEY DEFAULT nextval('checklist_checklist_id_seq'),
    user_id INTEGER NOT NULL,
    checklist_name VARCHAR(100) NOT NULL,
    checklist_description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_selected BOOLEAN DEFAULT FALSE
);

-- 3) Set sequence ownership to column
ALTER SEQUENCE checklist_checklist_id_seq OWNED BY checklist.checklist_id;
-- 4) Create foreign key constraint to account table (if needed)
-- ALTER TABLE checklist ADD CONSTRAINT fk_checklist_user_id 
-- FOREIGN KEY (user_id) REFERENCES account(user_id) ON DELETE CASCADE;

-- 5) Insert sample data (optional)
-- INSERT INTO checklist (user_id, checklist_name, checklist_description) 
-- VALUES (20000001, '進捗管理システムのチェックリスト', '設定項目をさきすること');