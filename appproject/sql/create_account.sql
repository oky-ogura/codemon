-- ...existing code...
-- SQL: create_account.sql
-- Creates sequence and table `account` in the `codemon` database.
-- Updated to match the provided table definition document.
-- ...existing code...
CREATE SEQUENCE IF NOT EXISTS account_user_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
-- ...existing code...
-- 1) account テーブル定義（設計書に合わせる）

-- ...existing code...
CREATE TABLE IF NOT EXISTS account (
    user_id INTEGER NOT NULL PRIMARY KEY DEFAULT nextval('account_user_id_seq'),
    user_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    avatar VARCHAR(255) DEFAULT NULL,
    account_type VARCHAR(20) NOT NULL,
    age INTEGER NOT NULL,
    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    group_id INTEGER DEFAULT NULL,
    CONSTRAINT fk_account_group FOREIGN KEY (group_id) REFERENCES "group"(group_id) ON DELETE SET NULL,
    CONSTRAINT chk_account_age_nonneg CHECK (age IS NULL OR age >= 0)
);
-- ...existing code...


-- 3) シーケンス所有権を設定
ALTER SEQUENCE account_user_id_seq OWNED BY account.user_id;

-- 4) サンプルデータ（必要ならアンコメントして使用）
-- INSERT INTO account (user_name, email, password, account_type, group_id)
-- VALUES ('山田太郎', 'yamada@example.com', 'hashed_password123', 'teacher', NULL);
-- ...existing code...