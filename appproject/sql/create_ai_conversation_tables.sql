-- create_ai_conversation_tables.sql
-- AI会話履歴関連の2テーブルを新規作成
-- Djangoモデル (codemon/models.py) の定義に完全準拠
--
-- 作成日: 2025-11-11
-- 対象テーブル:
--   1. codemon_aiconversation (AI会話セッション)
--   2. codemon_aimessage (AI会話メッセージ)
--
-- 前提: account テーブルが存在

SET client_encoding TO 'UTF8';
BEGIN;

-- ========================================
-- 1. codemon_aiconversation (AI会話セッション)
-- ========================================
-- ユーザーとAIキャラクターの会話セッション
-- character_id で使用するキャラクター(usagi, kitsune等)を識別
CREATE TABLE IF NOT EXISTS codemon_aiconversation (
    id BIGSERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    character_id VARCHAR(32) NOT NULL DEFAULT 'usagi',
    title VARCHAR(128) NOT NULL DEFAULT '',
    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT fk_aiconversation_user
        FOREIGN KEY (user_id) REFERENCES account(user_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_aiconversation_user ON codemon_aiconversation(user_id);
CREATE INDEX IF NOT EXISTS idx_aiconversation_character ON codemon_aiconversation(character_id);
CREATE INDEX IF NOT EXISTS idx_aiconversation_created_at ON codemon_aiconversation(created_at DESC);

COMMENT ON TABLE codemon_aiconversation IS 'AI会話セッション - ユーザーとAIキャラクターの会話';
COMMENT ON COLUMN codemon_aiconversation.id IS '会話セッションID - 主キー';
COMMENT ON COLUMN codemon_aiconversation.user_id IS 'ユーザーID - accountテーブルを参照';
COMMENT ON COLUMN codemon_aiconversation.character_id IS 'AIキャラクターID (usagi, kitsune, inu等)';
COMMENT ON COLUMN codemon_aiconversation.title IS '会話タイトル';
COMMENT ON COLUMN codemon_aiconversation.created_at IS '会話開始日時';

-- ========================================
-- 2. codemon_aimessage (AI会話メッセージ)
-- ========================================
-- 会話セッション内の個別メッセージ
-- role: user(ユーザー), assistant(AI), system(システム)
CREATE TABLE IF NOT EXISTS codemon_aimessage (
    id BIGSERIAL PRIMARY KEY,
    conversation_id BIGINT NOT NULL,
    role VARCHAR(16) NOT NULL,
    content TEXT NOT NULL,
    tokens INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT fk_aimessage_conversation
        FOREIGN KEY (conversation_id) REFERENCES codemon_aiconversation(id) ON DELETE CASCADE,
    CONSTRAINT chk_aimessage_role CHECK (role IN ('user', 'assistant', 'system'))
);

CREATE INDEX IF NOT EXISTS idx_aimessage_conversation ON codemon_aimessage(conversation_id);
CREATE INDEX IF NOT EXISTS idx_aimessage_role ON codemon_aimessage(role);
CREATE INDEX IF NOT EXISTS idx_aimessage_created_at ON codemon_aimessage(created_at);

COMMENT ON TABLE codemon_aimessage IS 'AI会話メッセージ - 会話セッション内の個別メッセージ';
COMMENT ON COLUMN codemon_aimessage.id IS 'メッセージID - 主キー';
COMMENT ON COLUMN codemon_aimessage.conversation_id IS '会話セッションID';
COMMENT ON COLUMN codemon_aimessage.role IS '送信者ロール (user/assistant/system)';
COMMENT ON COLUMN codemon_aimessage.content IS 'メッセージ本文';
COMMENT ON COLUMN codemon_aimessage.tokens IS 'トークン数 (API使用量計測用)';
COMMENT ON COLUMN codemon_aimessage.created_at IS 'メッセージ送信日時';

COMMIT;

-- ========================================
-- 完了メッセージ
-- ========================================
SELECT 'AI会話系テーブルの作成が完了しました。' AS status;
SELECT 'codemon_aiconversation, codemon_aimessage' AS created_tables;
