-- create_chat_tables.sql
-- チャット機能関連の5テーブルを新規作成
-- Djangoモデル (codemon/models.py) の定義に完全準拠
--
-- 作成日: 2025-11-11
-- 対象テーブル:
--   1. chat_thread (投函ボックス/スレッド)
--   2. chat_message (メッセージ)
--   3. chat_attachment (添付ファイル)
--   4. chat_read_receipt (既読管理)
--   5. chat_score (採点)
--
-- 前提: account, "group" テーブルが存在

SET client_encoding TO 'UTF8';
BEGIN;

-- ========================================
-- 1. chat_thread (チャットスレッド)
-- ========================================
-- 教師が作成して生徒が投稿する用途を想定
-- グループに紐づけ可能
CREATE TABLE IF NOT EXISTS chat_thread (
    thread_id BIGSERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT NULL,
    created_by_id INTEGER NOT NULL,
    group_id INTEGER NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT fk_chat_thread_created_by
        FOREIGN KEY (created_by_id) REFERENCES account(user_id) ON DELETE CASCADE,
    CONSTRAINT fk_chat_thread_group
        FOREIGN KEY (group_id) REFERENCES "group"(group_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_chat_thread_created_by ON chat_thread(created_by_id);
CREATE INDEX IF NOT EXISTS idx_chat_thread_group ON chat_thread(group_id);
CREATE INDEX IF NOT EXISTS idx_chat_thread_is_active ON chat_thread(is_active);

COMMENT ON TABLE chat_thread IS 'チャットスレッド - 投函ボックス。教師が作成して学生が投稿';
COMMENT ON COLUMN chat_thread.thread_id IS 'スレッドID - 主キー';
COMMENT ON COLUMN chat_thread.title IS 'スレッド名';
COMMENT ON COLUMN chat_thread.description IS 'スレッド説明';
COMMENT ON COLUMN chat_thread.created_by_id IS '作成者ID - accountテーブルを参照';
COMMENT ON COLUMN chat_thread.group_id IS 'グループID - groupテーブルを参照（NULL可）';
COMMENT ON COLUMN chat_thread.is_active IS 'アクティブフラグ - 論理削除用';

-- ========================================
-- 2. chat_message (チャットメッセージ)
-- ========================================
-- スレッド内のメッセージ。AI含む送信者はaccountを参照
CREATE TABLE IF NOT EXISTS chat_message (
    message_id BIGSERIAL PRIMARY KEY,
    thread_id BIGINT NOT NULL,
    sender_id INTEGER NOT NULL,
    content TEXT NULL,
    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    
    CONSTRAINT fk_chat_message_thread
        FOREIGN KEY (thread_id) REFERENCES chat_thread(thread_id) ON DELETE CASCADE,
    CONSTRAINT fk_chat_message_sender
        FOREIGN KEY (sender_id) REFERENCES account(user_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_chat_message_thread ON chat_message(thread_id);
CREATE INDEX IF NOT EXISTS idx_chat_message_sender ON chat_message(sender_id);
CREATE INDEX IF NOT EXISTS idx_chat_message_created_at ON chat_message(created_at);
CREATE INDEX IF NOT EXISTS idx_chat_message_is_deleted ON chat_message(is_deleted);

COMMENT ON TABLE chat_message IS 'チャットメッセージ - スレッド内のメッセージ';
COMMENT ON COLUMN chat_message.message_id IS 'メッセージID - 主キー';
COMMENT ON COLUMN chat_message.thread_id IS 'スレッドID';
COMMENT ON COLUMN chat_message.sender_id IS '送信者ID - accountテーブルを参照';
COMMENT ON COLUMN chat_message.content IS 'メッセージ本文';
COMMENT ON COLUMN chat_message.created_at IS '送信日時';
COMMENT ON COLUMN chat_message.is_deleted IS '削除フラグ - 論理削除用';

-- ========================================
-- 3. chat_attachment (チャット添付)
-- ========================================
-- メッセージに紐づくファイル/画像の保存参照
CREATE TABLE IF NOT EXISTS chat_attachment (
    attachment_id BIGSERIAL PRIMARY KEY,
    message_id BIGINT NOT NULL,
    file VARCHAR(100) NOT NULL,
    uploaded_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT fk_chat_attachment_message
        FOREIGN KEY (message_id) REFERENCES chat_message(message_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_chat_attachment_message ON chat_attachment(message_id);
CREATE INDEX IF NOT EXISTS idx_chat_attachment_uploaded_at ON chat_attachment(uploaded_at);

COMMENT ON TABLE chat_attachment IS 'チャット添付 - メッセージに紐づくファイル';
COMMENT ON COLUMN chat_attachment.attachment_id IS '添付ID - 主キー';
COMMENT ON COLUMN chat_attachment.message_id IS 'メッセージID';
COMMENT ON COLUMN chat_attachment.file IS 'ファイルパス - FileFieldのパス';
COMMENT ON COLUMN chat_attachment.uploaded_at IS 'アップロード日時';

-- ========================================
-- 4. chat_read_receipt (既読レシート)
-- ========================================
-- メッセージごとに誰が読んだかを記録
CREATE TABLE IF NOT EXISTS chat_read_receipt (
    id BIGSERIAL PRIMARY KEY,
    message_id BIGINT NOT NULL,
    reader_id INTEGER NOT NULL,
    read_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT fk_chat_read_receipt_message
        FOREIGN KEY (message_id) REFERENCES chat_message(message_id) ON DELETE CASCADE,
    CONSTRAINT fk_chat_read_receipt_reader
        FOREIGN KEY (reader_id) REFERENCES account(user_id) ON DELETE CASCADE,
    CONSTRAINT uk_chat_read_receipt_message_reader UNIQUE (message_id, reader_id)
);

CREATE INDEX IF NOT EXISTS idx_chat_read_receipt_message ON chat_read_receipt(message_id);
CREATE INDEX IF NOT EXISTS idx_chat_read_receipt_reader ON chat_read_receipt(reader_id);
CREATE INDEX IF NOT EXISTS idx_chat_read_receipt_read_at ON chat_read_receipt(read_at);

COMMENT ON TABLE chat_read_receipt IS '既読レシート - メッセージごとの既読管理';
COMMENT ON COLUMN chat_read_receipt.id IS 'レシートID - 主キー';
COMMENT ON COLUMN chat_read_receipt.message_id IS 'メッセージID';
COMMENT ON COLUMN chat_read_receipt.reader_id IS '既読者ID - accountテーブルを参照';
COMMENT ON COLUMN chat_read_receipt.read_at IS '既読日時';

-- ========================================
-- 5. chat_score (チャットスコア)
-- ========================================
-- 教師が付ける点数（メッセージ単位またはスレッド単位）
CREATE TABLE IF NOT EXISTS chat_score (
    id BIGSERIAL PRIMARY KEY,
    message_id BIGINT NULL,
    thread_id BIGINT NULL,
    scorer_id INTEGER NOT NULL,
    score INTEGER NULL,
    comment TEXT NULL,
    created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT fk_chat_score_message
        FOREIGN KEY (message_id) REFERENCES chat_message(message_id) ON DELETE CASCADE,
    CONSTRAINT fk_chat_score_thread
        FOREIGN KEY (thread_id) REFERENCES chat_thread(thread_id) ON DELETE CASCADE,
    CONSTRAINT fk_chat_score_scorer
        FOREIGN KEY (scorer_id) REFERENCES account(user_id) ON DELETE CASCADE,
    CONSTRAINT chk_chat_score_target CHECK (
        (message_id IS NOT NULL AND thread_id IS NULL) OR
        (message_id IS NULL AND thread_id IS NOT NULL)
    )
);

CREATE INDEX IF NOT EXISTS idx_chat_score_message ON chat_score(message_id);
CREATE INDEX IF NOT EXISTS idx_chat_score_thread ON chat_score(thread_id);
CREATE INDEX IF NOT EXISTS idx_chat_score_scorer ON chat_score(scorer_id);
CREATE INDEX IF NOT EXISTS idx_chat_score_created_at ON chat_score(created_at);

COMMENT ON TABLE chat_score IS 'チャットスコア - 教師が付ける点数';
COMMENT ON COLUMN chat_score.id IS 'スコアID - 主キー';
COMMENT ON COLUMN chat_score.message_id IS 'メッセージID（メッセージ単位採点時）';
COMMENT ON COLUMN chat_score.thread_id IS 'スレッドID（スレッド単位採点時）';
COMMENT ON COLUMN chat_score.scorer_id IS '採点者ID - accountテーブルを参照';
COMMENT ON COLUMN chat_score.score IS '点数';
COMMENT ON COLUMN chat_score.comment IS 'コメント';
COMMENT ON COLUMN chat_score.created_at IS '採点日時';

COMMIT;

-- ========================================
-- 完了メッセージ
-- ========================================
SELECT 'チャット系テーブルの作成が完了しました。' AS status;
SELECT 'chat_thread, chat_message, chat_attachment, chat_read_receipt, chat_score' AS created_tables;
