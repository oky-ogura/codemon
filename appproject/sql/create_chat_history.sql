-- PostgreSQL: create_chat_history.sql
-- Creates sequence and table `chat_history` in the `codemon` database.
-- Chat history management table for storing AI chat conversations

-- 1) Create sequence for auto-incrementing chat_id
CREATE SEQUENCE IF NOT EXISTS chat_history_chat_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

-- 2) Create chat_history table
CREATE TABLE IF NOT EXISTS chat_history (
    chat_id INTEGER NOT NULL PRIMARY KEY DEFAULT nextval('chat_history_chat_id_seq'),
    user_id INTEGER NOT NULL,
    ai_setting_id INTEGER NOT NULL,
    sender_type VARCHAR(10) NOT NULL CHECK (sender_type IN ('user', 'ai')),
    message TEXT,
    sent_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 3) Set sequence ownership to column
ALTER SEQUENCE chat_history_chat_id_seq OWNED BY chat_history.chat_id;

-- 4) Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_chat_history_user_id ON chat_history(user_id);
CREATE INDEX IF NOT EXISTS idx_chat_history_ai_setting_id ON chat_history(ai_setting_id);
CREATE INDEX IF NOT EXISTS idx_chat_history_sent_at ON chat_history(sent_at);
CREATE INDEX IF NOT EXISTS idx_chat_history_sender_type ON chat_history(sender_type);
CREATE INDEX IF NOT EXISTS idx_chat_history_user_sent_at ON chat_history(user_id, sent_at);

-- 5) Create foreign key constraints
-- Note: Uncomment when account and ai_config tables are created
-- ALTER TABLE chat_history ADD CONSTRAINT fk_chat_history_user_id 
-- FOREIGN KEY (user_id) REFERENCES account(user_id) ON DELETE CASCADE;

-- ALTER TABLE chat_history ADD CONSTRAINT fk_chat_history_ai_setting_id 
-- FOREIGN KEY (ai_setting_id) REFERENCES ai_config(ai_setting_id) ON DELETE CASCADE;

-- 6) Insert sample data (optional)
-- INSERT INTO chat_history (user_id, ai_setting_id, sender_type, message) VALUES 
-- (20000001, 1, 'user', 'こんにちは、AIさん'),
-- (20000001, 1, 'ai', 'こんにちは！何かお手伝いできることはありますか？'),
-- (20000001, 1, 'user', 'プログラミングについて教えてください'),
-- (20000001, 1, 'ai', 'プログラミングについてお答えします。どの言語に興味がありますか？');

-- 7) Create view for conversation threads
CREATE OR REPLACE VIEW conversation_view AS
SELECT 
    ch.chat_id,
    ch.user_id,
    ch.ai_setting_id,
    ch.sender_type,
    ch.message,
    ch.sent_at,
    ROW_NUMBER() OVER (PARTITION BY ch.user_id, ch.ai_setting_id ORDER BY ch.sent_at) as message_order
FROM chat_history ch
ORDER BY ch.user_id, ch.ai_setting_id, ch.sent_at;

-- 8) Comments for table and columns
COMMENT ON TABLE chat_history IS 'チャット履歴テーブル - AIとユーザーの会話履歴を管理';
COMMENT ON COLUMN chat_history.chat_id IS 'AIチャットID - 主キー、自動採番';
COMMENT ON COLUMN chat_history.user_id IS 'ユーザーID - アカウントテーブルを参照する外部キー';
COMMENT ON COLUMN chat_history.ai_setting_id IS 'AI設定ID - AI設定テーブルを参照する外部キー';
COMMENT ON COLUMN chat_history.sender_type IS '送信者種別 - user（ユーザー）またはai（AI）';
COMMENT ON COLUMN chat_history.message IS 'メッセージ内容 - チャットの本文';
COMMENT ON COLUMN chat_history.sent_at IS '送信日時 - メッセージが送信された日時';

COMMENT ON VIEW conversation_view IS '会話スレッドビュー - ユーザーとAIの会話を時系列で表示';