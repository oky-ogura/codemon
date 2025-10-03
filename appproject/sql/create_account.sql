-- SQL: create_account.sql
-- Creates sequence and table `account` in the `codemon` database.
-- Updated version based on table definition document

-- 1) Create sequence starting at 20000001 for user_id
CREATE SEQUENCE IF NOT EXISTS account_user_id_seq
    START WITH 20000001
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

-- 2) Create table with updated schema
CREATE TABLE IF NOT EXISTS account (
    user_id INTEGER NOT NULL PRIMARY KEY DEFAULT nextval('account_user_id_seq'),
    user_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    account_type VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    type VARCHAR(50)
);

-- 3) Set sequence ownership to column
ALTER SEQUENCE account_user_id_seq OWNED BY account.user_id;

-- 4) Insert sample data (optional)
-- INSERT INTO account (user_name, email, password, account_type, type) 
-- VALUES ('山田太郎', 'yamada@example.com', 'hashed_password123', 'teacher', '教員');