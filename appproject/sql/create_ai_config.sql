-- SQL: create_ai_config.sql
-- Creates sequence and table `ai_config` in the `codemon` database.
-- AI設定テーブル

-- 1) Create sequence starting at 3000001 for ai_setting_id
CREATE SEQUENCE IF NOT EXISTS ai_config_ai_setting_id_seq
    START WITH 3000001
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

-- 2) Create table
CREATE TABLE IF NOT EXISTS ai_config (
    ai_setting_id INTEGER NOT NULL PRIMARY KEY DEFAULT nextval('ai_config_ai_setting_id_seq'),
    user_id INTEGER NOT NULL,
    appearance VARCHAR(100) NOT NULL DEFAULT 'triangle',
    ai_name VARCHAR(50) NOT NULL DEFAULT 'codemon',
    ai_personality VARCHAR(100) DEFAULT 'energetic',
    ai_speech VARCHAR(50) DEFAULT 'desu',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3) Set sequence ownership to column
ALTER SEQUENCE ai_config_ai_setting_id_seq OWNED BY ai_config.ai_setting_id;