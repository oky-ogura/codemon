-- seed_data_extended.sql
-- 新カラム・新テーブル対応の拡張シードデータ
-- extend_existing_tables.sql、create_chat_tables.sql、create_ai_conversation_tables.sql の実行後に使用
--
-- 作成日: 2025-11-11
-- 対象:
--   - group テーブルの新カラム (description, owner_id, is_active) を更新
--   - group_member テーブルの新カラム (member_id, joined_at, is_active) を更新
--   - chat_thread, chat_message, chat_attachment にサンプルデータ投入
--   - codemon_aiconversation, codemon_aimessage にサンプルデータ投入

SET client_encoding TO 'UTF8';
BEGIN;

-- ========================================
-- 1. group テーブルの新カラム更新
-- ========================================
-- 既存データ（7000001=A組, 7000002=B組）にdescription, owner_id, is_activeを設定
UPDATE "group"
SET 
  description = 'プログラミング基礎クラスA',
  owner_id = 20000001,  -- 教師（山田 太郎）
  is_active = TRUE
WHERE group_id = 7000001;

UPDATE "group"
SET 
  description = 'プログラミング応用クラスB',
  owner_id = 20000001,  -- 教師（山田 太郎）
  is_active = TRUE
WHERE group_id = 7000002;

-- ========================================
-- 2. group_member テーブルの新カラム更新
-- ========================================
-- member_id は既に extend_existing_tables.sql で member_user_id からコピー済み
-- joined_at, is_active はデフォルト値で設定済み
-- 念のため確認・更新
UPDATE group_member
SET 
  is_active = TRUE,
  joined_at = COALESCE(joined_at, created_at)  -- 既存のcreated_atをjoined_atに反映
WHERE is_active IS NULL OR joined_at IS NULL;

-- ========================================
-- 3. chat_thread (チャットスレッド) にサンプルデータ
-- ========================================
-- 教師が作成した投函ボックス
INSERT INTO chat_thread (thread_id, title, description, created_by_id, group_id, is_active)
VALUES
  (1, '第1回課題提出スレッド', 'プログラミング基礎の第1回課題を提出してください', 20000001, 7000001, TRUE),
  (2, '質問・相談スレッド', '学習中の疑問点や相談事項はこちらへ', 20000001, 7000001, TRUE),
  (3, '第2回課題提出スレッド', 'プログラミング応用の第2回課題を提出してください', 20000001, 7000002, TRUE)
ON CONFLICT (thread_id) DO NOTHING;

-- シーケンスを最新に
SELECT setval('chat_thread_thread_id_seq', (SELECT MAX(thread_id) FROM chat_thread), true);

-- ========================================
-- 4. chat_message (チャットメッセージ) にサンプルデータ
-- ========================================
-- スレッド1での学生2名の提出と教師のコメント
INSERT INTO chat_message (message_id, thread_id, sender_id, content, is_deleted)
VALUES
  (1, 1, 20000002, '第1回課題を提出します。変数と演算子について学びました。', FALSE),
  (2, 1, 20000001, 'お疲れ様です。提出ありがとうございます。', FALSE),
  (3, 1, 20000003, '課題提出いたします。ループ処理の理解が深まりました。', FALSE),
  (4, 1, 20000001, 'よくできています。次回も頑張りましょう。', FALSE),
  -- スレッド2での質問
  (5, 2, 20000002, 'for文とwhile文の使い分けが分かりません。', FALSE),
  (6, 2, 20000001, '繰り返し回数が決まっている場合はfor、条件で判断する場合はwhileを使うといいですよ。', FALSE)
ON CONFLICT (message_id) DO NOTHING;

SELECT setval('chat_message_message_id_seq', (SELECT MAX(message_id) FROM chat_message), true);

-- ========================================
-- 5. chat_attachment (添付ファイル) にサンプルデータ
-- ========================================
-- メッセージ1に添付ファイル例
INSERT INTO chat_attachment (attachment_id, message_id, file)
VALUES
  (1, 1, 'chat_attachments/2025/11/assignment1_student2.py'),
  (2, 3, 'chat_attachments/2025/11/assignment1_student3.py')
ON CONFLICT (attachment_id) DO NOTHING;

SELECT setval('chat_attachment_attachment_id_seq', (SELECT MAX(attachment_id) FROM chat_attachment), true);

-- ========================================
-- 6. chat_read_receipt (既読レシート) にサンプルデータ
-- ========================================
-- 教師がメッセージ1,3,5を既読
INSERT INTO chat_read_receipt (message_id, reader_id)
VALUES
  (1, 20000001),
  (3, 20000001),
  (5, 20000001)
ON CONFLICT (message_id, reader_id) DO NOTHING;

-- ========================================
-- 7. chat_score (採点) にサンプルデータ
-- ========================================
-- 教師がメッセージ1と3に点数を付与
INSERT INTO chat_score (message_id, scorer_id, score, comment)
VALUES
  (1, 20000001, 85, '変数と演算子の理解が良好です。次はもう少し複雑な演算にも挑戦しましょう。'),
  (3, 20000001, 90, 'ループ処理がしっかり理解できています。素晴らしいです。')
ON CONFLICT DO NOTHING;

-- ========================================
-- 8. codemon_aiconversation (AI会話セッション) にサンプルデータ
-- ========================================
-- 学生がAIキャラクター(usagi, kitsune)と会話
INSERT INTO codemon_aiconversation (id, user_id, character_id, title)
VALUES
  (1, 20000002, 'usagi', 'usagi-20251111-session'),
  (2, 20000003, 'kitsune', 'kitsune-20251111-session'),
  (3, 20000004, 'arupaka', 'arupaka-20251111-session')
ON CONFLICT (id) DO NOTHING;

SELECT setval('codemon_aiconversation_id_seq', (SELECT MAX(id) FROM codemon_aiconversation), true);

-- ========================================
-- 9. codemon_aimessage (AI会話メッセージ) にサンプルデータ
-- ========================================
-- 会話1: 学生2 と usagi
INSERT INTO codemon_aimessage (conversation_id, role, content, tokens)
VALUES
  (1, 'user', 'こんにちは、AIさん', 10),
  (1, 'assistant', 'ぼ、ぼく...こんにちは！何か手伝えることはあるかな...？', 15),
  (1, 'user', 'Pythonの勉強のコツを教えて', 12),
  (1, 'assistant', 'え、えっと...小さく書いて動かして、理解を積み上げるのが...おすすめだよ！', 18),
  -- 会話2: 学生3 と kitsune
  (2, 'user', 'プログラミングって難しいね', 11),
  (2, 'assistant', 'ふふっ、難しく見えるだけだよ～。コツをつかめば簡単さ♪', 16),
  -- 会話3: 学生4 と arupaka
  (3, 'user', 'アルゴリズムについて教えてください', 14),
  (3, 'assistant', 'ごきげんよう。アルゴリズムとは問題を解くための手順ですわ。わたくしに任せなさい！', 20)
ON CONFLICT (id) DO NOTHING;

SELECT setval('codemon_aimessage_id_seq', (SELECT MAX(id) FROM codemon_aimessage), true);

COMMIT;

-- ========================================
-- 完了メッセージ
-- ========================================
SELECT '拡張シードデータの投入が完了しました。' AS status;
SELECT 'group, group_member の新カラム更新' AS update_1;
SELECT 'chat_thread, chat_message, chat_attachment, chat_read_receipt, chat_score にサンプルデータ追加' AS update_2;
SELECT 'codemon_aiconversation, codemon_aimessage にサンプルデータ追加' AS update_3;
