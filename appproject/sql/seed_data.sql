-- seed_data.sql
-- 全機能テーブル向けの初期データ投入スクリプト（再実行しても安全なようにON CONFLICTで冪等化）
-- 前提: sql/*.sql によりテーブル・シーケンスは作成済み

SET client_encoding TO 'UTF8';
BEGIN;

-- 0) シーケンスの初期位置安全化（最低値のセット）
SELECT setval('account_user_id_seq',      GREATEST(COALESCE((SELECT MAX(user_id) FROM account),      1), 1), true);
SELECT setval('group_group_id_seq',       GREATEST(COALESCE((SELECT MAX(group_id) FROM "group"),    7000000),  7000000),  true);
SELECT setval('ai_config_ai_setting_id_seq', GREATEST(COALESCE((SELECT MAX(ai_setting_id) FROM ai_config), 3000000), 3000000), true);
SELECT setval('algorithm_algorithm_id_seq',  GREATEST(COALESCE((SELECT MAX(algorithm_id) FROM algorithm), 5000000), 5000000), true);
SELECT setval('checklist_checklist_id_seq',  GREATEST(COALESCE((SELECT MAX(checklist_id) FROM checklist), 6000000), 6000000), true);
-- checklist_item は一部環境で未作成の可能性があるため存在時のみ実行
DO $$
BEGIN
  PERFORM 1 FROM pg_class WHERE relname = 'checklist_item';
  IF FOUND THEN
    PERFORM setval('checklist_item_checklist_item_id_seq', GREATEST(COALESCE((SELECT MAX(checklist_item_id) FROM checklist_item), 6001000), 6001000), true);
  END IF;
END; $$;
SELECT setval('system_system_id_seq',      GREATEST(COALESCE((SELECT MAX(system_id) FROM system),    4000000),  4000000),  true);
SELECT setval('chat_history_chat_id_seq',  GREATEST(COALESCE((SELECT MAX(chat_id) FROM chat_history), 1),       1),        true);
SELECT setval('ai_learning_training_data_id_seq', GREATEST(COALESCE((SELECT MAX(training_data_id) FROM ai_learning), 1), 1), true);

-- 1) グループ（ID固定で冪等に投入）
INSERT INTO "group" (group_id, group_name, user_id, password)
VALUES
  (7000001, 'A組', 1, 'gApass'),
  (7000002, 'B組', 1, 'gBpass')
ON CONFLICT (group_id) DO NOTHING;

-- 2) アカウント（教師1 + 学生3）
INSERT INTO account (user_id, user_name, email, password, account_type, age, group_id)
VALUES
  (1, '山田 太郎(教師)', 'teacher@example.com', 'teacher_pass', 'teacher', 35, NULL),
  (2, '佐藤 花子',       'student1@example.com', 'stud_pass1',  'student', 18, 7000001),
  (3, '鈴木 次郎',       'student2@example.com', 'stud_pass2',  'student', 17, 7000001),
  (4, '高橋 三奈',       'student3@example.com', 'stud_pass3',  'student', 19, 7000002)
ON CONFLICT (user_id) DO NOTHING;

-- シーケンス追従
SELECT setval('account_user_id_seq', (SELECT MAX(user_id) FROM account), true);

-- 3) グループメンバー（教師をteacher、学生をmemberとして追加）
INSERT INTO group_member (group_id, member_user_id, role)
VALUES
  (7000001, 1, 'teacher'),
  (7000001, 2, 'member'),
  (7000001, 3, 'member'),
  (7000002, 1, 'teacher'),
  (7000002, 4, 'member')
ON CONFLICT (group_id, member_user_id) DO NOTHING;

-- 4) AI設定（ai_config）: ID固定で投入
INSERT INTO ai_config (ai_setting_id, user_id, appearance, ai_name, ai_personality, ai_speech)
VALUES
  (3000001, 1, 'triangle', 'codemon', 'energetic', 'です'),
  (3000002, 2, 'circle',   'usagi',   'おどおど',  'です'),
  (3000003, 3, 'square',   'neko',    'けだるげ',  'だよ')
ON CONFLICT (ai_setting_id) DO NOTHING;

SELECT setval('ai_config_ai_setting_id_seq', (SELECT MAX(ai_setting_id) FROM ai_config), true);

-- 5) AI詳細（ai_detail）: チェック制約に合う値のみ
INSERT INTO ai_detail (ai_setting_id, appearance, ai_name, ai_personality, ai_speech, ai_image)
VALUES
  (3000001, 'triangle', 'codemon', '元気',   'です', 'triangle'),
  (3000002, 'circle',   'うさぎ',   'おどおど', 'です', 'circle'),
  (3000003, 'square',   'ねこ',     'けだるげ', 'だよ', 'square')
ON CONFLICT (ai_setting_id) DO NOTHING;

-- 6) システム（system）
INSERT INTO system (system_id, user_id, system_name, system_description)
VALUES
  (4000001, 1, '進捗管理システム', '生徒の進捗を管理するシステム')
ON CONFLICT (system_id) DO NOTHING;

SELECT setval('system_system_id_seq', (SELECT MAX(system_id) FROM system), true);

-- 7) アルゴリズム（algorithm）
INSERT INTO algorithm (algorithm_id, user_id, algorithm_name, algorithm_description)
VALUES
  (5000001, 1, '進捗判定アルゴリズム', '課題達成・提出頻度・既読などから進捗を算出する'),
  (5000002, 1, '学習傾向分析',        '投稿内容と既読・添付から学習傾向を抽出する')
ON CONFLICT (algorithm_id) DO NOTHING;

SELECT setval('algorithm_algorithm_id_seq', (SELECT MAX(algorithm_id) FROM algorithm), true);

-- 8) チェックリスト（checklist）
INSERT INTO checklist (checklist_id, user_id, checklist_name, checklist_description, is_selected)
VALUES
  (6000001, 2, '毎日の学習チェック', '基礎学習の進捗を毎日確認', true),
  (6000002, 1, '授業準備チェック',   '授業前の準備確認', false)
ON CONFLICT (checklist_id) DO NOTHING;

SELECT setval('checklist_checklist_id_seq', (SELECT MAX(checklist_id) FROM checklist), true);

-- 9) チェックリスト項目（checklist_item）
-- checklist_item が存在する場合のみ投入
DO $$
BEGIN
  PERFORM 1 FROM pg_class WHERE relname = 'checklist_item';
  IF FOUND THEN
    INSERT INTO checklist_item (checklist_item_id, checklist_id, item_text, is_done, sort_order)
    VALUES
      (6001001, 6000001, '教科書を読む', false, 1),
      (6001002, 6000001, 'ノートをまとめる', false, 2),
      (6001003, 6000001, '演習問題を3問解く', false, 3),
      (6001004, 6000001, 'わからない点をメモ', false, 4),
      (6001005, 6000001, '翌日の計画を立てる', false, 5),
      (6001006, 6000002, '教材の配布準備', false, 1),
      (6001007, 6000002, '課題の採点', false, 2),
      (6001008, 6000002, 'スライド最終確認', false, 3),
      (6001009, 6000002, '出席簿の準備', false, 4)
    ON CONFLICT (checklist_item_id) DO NOTHING;
  END IF;
END; $$;

DO $$
BEGIN
  PERFORM 1 FROM pg_class WHERE relname = 'checklist_item';
  IF FOUND THEN
    PERFORM setval('checklist_item_checklist_item_id_seq', (SELECT MAX(checklist_item_id) FROM checklist_item), true);
  END IF;
END; $$;

-- 10) チャット履歴（chat_history）
INSERT INTO chat_history (chat_id, user_id, ai_setting_id, sender_type, message)
VALUES
  (1, 2, 3000001, 'user', 'こんにちは、AIさん'),
  (2, 2, 3000001, 'ai',   'こんにちは！何を手伝えばよいですか？'),
  (3, 2, 3000001, 'user', 'Pythonの勉強のコツを教えて'),
  (4, 2, 3000001, 'ai',   '小さく書いて動かして、理解を積み上げましょう。')
ON CONFLICT (chat_id) DO NOTHING;

SELECT setval('chat_history_chat_id_seq', (SELECT MAX(chat_id) FROM chat_history), true);

-- 11) AI学習（ai_learning）
INSERT INTO ai_learning (training_data_id, ai_setting_id, data_name, data_type, data_path, features, user_id)
VALUES
  (1, 3000001, 'プログラミング基礎データ', 'text',  '/data/programming_basics.txt', '{"keyword":"進捗","count":5}'::jsonb, 1),
  (2, 3000001, 'Python学習画像',         'image', '/data/python_tutorial.jpg',   '{"language":"python","difficulty":"beginner"}'::jsonb, 1),
  (3, 3000002, 'Java演習問題',           'text',  '/data/java_exercises.txt',    '{"keyword":"演習","count":10}'::jsonb, 2)
ON CONFLICT (training_data_id) DO NOTHING;

SELECT setval('ai_learning_training_data_id_seq', (SELECT MAX(training_data_id) FROM ai_learning), true);

COMMIT;
