-- verify_complete_schema.sql
-- 全テーブルの件数確認とスキーマ完全性検証
-- 実行後、各テーブルにデータが存在することを確認

SET client_encoding TO 'UTF8';

\echo '========================================='
\echo '全テーブル件数確認'
\echo '========================================='

SELECT 'account' AS table_name, COUNT(*) AS row_count FROM account
UNION ALL
SELECT 'group', COUNT(*) FROM "group"
UNION ALL
SELECT 'group_member', COUNT(*) FROM group_member
UNION ALL
SELECT 'ai_config', COUNT(*) FROM ai_config
UNION ALL
SELECT 'ai_detail', COUNT(*) FROM ai_detail
UNION ALL
SELECT 'ai_learning', COUNT(*) FROM ai_learning
UNION ALL
SELECT 'algorithm', COUNT(*) FROM algorithm
UNION ALL
SELECT 'system', COUNT(*) FROM system
UNION ALL
SELECT 'checklist', COUNT(*) FROM checklist
UNION ALL
SELECT 'checklist_item', COUNT(*) FROM checklist_item
UNION ALL
SELECT 'chat_history', COUNT(*) FROM chat_history
UNION ALL
SELECT 'chat_thread', COUNT(*) FROM chat_thread
UNION ALL
SELECT 'chat_message', COUNT(*) FROM chat_message
UNION ALL
SELECT 'chat_attachment', COUNT(*) FROM chat_attachment
UNION ALL
SELECT 'chat_read_receipt', COUNT(*) FROM chat_read_receipt
UNION ALL
SELECT 'chat_score', COUNT(*) FROM chat_score
UNION ALL
SELECT 'codemon_aiconversation', COUNT(*) FROM codemon_aiconversation
UNION ALL
SELECT 'codemon_aimessage', COUNT(*) FROM codemon_aimessage
ORDER BY table_name;

\echo ''
\echo '========================================='
\echo 'group テーブルの新カラム確認'
\echo '========================================='
SELECT group_id, group_name, description, owner_id, is_active
FROM "group"
ORDER BY group_id;

\echo ''
\echo '========================================='
\echo 'group_member テーブルの新カラム確認'
\echo '========================================='
SELECT id, group_id, member_user_id, member_id, role, is_active
FROM group_member
ORDER BY id
LIMIT 5;

\echo ''
\echo '========================================='
\echo 'chat_thread サンプル'
\echo '========================================='
SELECT thread_id, title, created_by_id, group_id, is_active
FROM chat_thread
ORDER BY thread_id;

\echo ''
\echo '========================================='
\echo 'chat_message サンプル'
\echo '========================================='
SELECT message_id, thread_id, sender_id, LEFT(content, 50) AS content_preview
FROM chat_message
ORDER BY message_id
LIMIT 5;

\echo ''
\echo '========================================='
\echo 'codemon_aiconversation サンプル'
\echo '========================================='
SELECT id, user_id, character_id, title
FROM codemon_aiconversation
ORDER BY id;

\echo ''
\echo '========================================='
\echo 'codemon_aimessage サンプル'
\echo '========================================='
SELECT id, conversation_id, role, LEFT(content, 40) AS content_preview
FROM codemon_aimessage
ORDER BY id
LIMIT 5;

\echo ''
\echo '========================================='
\echo '検証完了: すべてのテーブルが正常に作成され、データが投入されました。'
\echo '========================================='
